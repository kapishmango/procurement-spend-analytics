"""Practice project 3: invoice data quality and two-way PO matching."""
import re
from collections import defaultdict
from datetime import date


def invoice_key(value):
    return re.sub(r'[^A-Z0-9]', '', str(value).upper())


def clean_invoices(invoices, supplier_rows):
    suppliers = {s['supplier_record_id']: s for s in supplier_rows}
    groups, excluded = defaultdict(list), []
    for row in invoices:
        supplier = suppliers.get(row['supplier_record_id'])
        reasons = []
        if not supplier or not supplier.get('canonical_supplier_id'):
            reasons.append('unresolved_supplier')
        if not invoice_key(row.get('invoice_number', '')):
            reasons.append('missing_invoice_number')
        if row.get('currency') != 'INR':
            reasons.append('unsupported_currency')
        try:
            date.fromisoformat(row['invoice_date'])
        except (ValueError, KeyError, TypeError):
            reasons.append('invalid_invoice_date')
        money_fields = ('quantity', 'unit_price_paise', 'amount_paise')
        if any(type(row.get(k)) is not int for k in money_fields):
            reasons.append('invalid_numeric_type')
        elif row['quantity'] <= 0 or row['unit_price_paise'] < 0 or row['amount_paise'] < 0:
            reasons.append('invalid_numeric_value')
        elif row['quantity'] * row['unit_price_paise'] != row['amount_paise']:
            reasons.append('amount_mismatch')
        if reasons:
            excluded.append({'row_id': row['row_id'], 'reasons': reasons})
            continue
        item = {**row, 'canonical_supplier_id': supplier['canonical_supplier_id'],
                'supplier_approved': supplier['approved']}
        key = (item['canonical_supplier_id'], invoice_key(item['invoice_number']), item['currency'])
        groups[key].append(item)
    accepted = []
    signature_fields = ('invoice_date', 'po_id', 'quantity', 'unit_price_paise', 'amount_paise',
                        'commodity_code', 'business_unit', 'geography', 'contract_id', 'contract_required')
    for rows in groups.values():
        signatures = {tuple(r.get(k) for k in signature_fields) for r in rows}
        if len(signatures) > 1:
            excluded.extend({'row_id': r['row_id'], 'reasons': ['conflicting_invoice_reference']} for r in rows)
        else:
            accepted.append(rows[0])
            excluded.extend({'row_id': r['row_id'], 'reasons': ['repeated_identical_invoice_record'],
                             'retained_row_id': rows[0]['row_id']} for r in rows[1:])
    return accepted, excluded


def reconcile(invoices, purchase_orders, contracts):
    pos = {p['po_id']: p for p in purchase_orders}
    contract_lookup = {c['contract_id']: c for c in contracts}
    results = []
    for row in invoices:
        checks, policy = [], []
        po = pos.get(row.get('po_id'))
        if not row.get('po_id'):
            checks.append('no_po_reference')
        elif po is None:
            checks.append('unknown_po_reference')
        else:
            if po['canonical_supplier_id'] != row['canonical_supplier_id']:
                checks.append('po_supplier_mismatch')
            if po['currency'] != row['currency']:
                checks.append('po_currency_mismatch')
            if row['quantity'] > po['quantity']:
                checks.append('quantity_above_po')
            if row['unit_price_paise'] > po['unit_price_paise']:
                checks.append('unit_price_above_po')
        if not row['supplier_approved']:
            policy.append('non_approved_supplier_review')
        if row['contract_required']:
            contract = contract_lookup.get(row.get('contract_id'))
            valid = (contract and contract['canonical_supplier_id'] == row['canonical_supplier_id']
                     and contract['valid_from'] <= row['invoice_date'] <= contract['valid_to'])
            if not valid:
                policy.append('missing_or_invalid_contract_review')
        results.append({**row, 'po_checks': checks, 'policy_checks': policy})
    return results
