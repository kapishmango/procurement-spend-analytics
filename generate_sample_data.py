"""Deterministic fictional procurement data, entirely generated for practice."""
from copy import deepcopy
from datetime import date, timedelta


def generate():
    names = ['Demo Harbour Supplies', 'Demo Vertex Trading', 'Demo Orion Services',
             'Demo Cedar Facilities', 'Demo Westfield Products', 'Demo Meadow Solutions']
    suppliers = []
    for number, name in enumerate(names, 1):
        for alias in ('A', 'B'):
            suppliers.append({'supplier_record_id': f'V{number:02d}{alias}',
                              'supplier_name': name + ' Pvt Ltd' if alias == 'A' else name.upper() + ' PRIVATE LIMITED',
                              'registration_id': f'DEMO-REG-{number:04d}', 'approved': number != 6})
    suppliers.append({'supplier_record_id': 'V01C', 'supplier_name': names[0] + ' Limited',
                      'registration_id': None, 'approved': True})
    taxonomy = {'OFF': ['Indirect materials', 'Office supplies'], 'IT': ['Technology', 'IT hardware'],
                'SW': ['Technology', 'Software'], 'FAC': ['Services', 'Facilities'],
                'MRO': ['Indirect materials', 'Maintenance supplies'], 'LOG': ['Services', 'Logistics']}
    codes = list(taxonomy)
    pos, invoices = [], []
    contracts = [{'contract_id': f'CT-{i:02d}', 'canonical_supplier_id': f'S{i:02d}',
                  'valid_from': '2026-01-01', 'valid_to': '2026-12-31'} for i in range(1, 6)]
    for i in range(120):
        supplier_num = i % 6 + 1
        quantity = i % 5 + 1
        unit_price = (350 + (i % 9) * 125) * 100
        code = codes[(i // 6) % len(codes)]
        po_id = f'PO-{i + 1:04d}'
        pos.append({'po_id': po_id, 'canonical_supplier_id': f'S{supplier_num:02d}',
                    'quantity': quantity, 'unit_price_paise': unit_price, 'currency': 'INR'})
        billed_quantity = quantity + (1 if i % 41 == 0 else 0)
        billed_price = unit_price + (2500 if i % 23 == 0 else 0)
        invoices.append({'row_id': f'ROW-{i + 1:04d}', 'invoice_number': f'INV-{i + 1:04d}',
                         'invoice_date': (date(2026, 1, 1) + timedelta(days=2*i)).isoformat(),
                         'supplier_record_id': f"V{supplier_num:02d}{'A' if (i // 6) % 2 == 0 else 'B'}",
                         'po_id': None if i % 29 == 0 else po_id,
                         'quantity': billed_quantity, 'unit_price_paise': billed_price,
                         'amount_paise': billed_quantity * billed_price, 'currency': 'INR',
                         'commodity_code': 'UNMAPPED' if i == 37 else code,
                         'business_unit': ['Operations', 'Engineering', 'Finance'][(i // 2) % 3],
                         'geography': ['Mumbai', 'Bengaluru', 'Pune'][(i // 3) % 3],
                         'contract_required': code in {'IT', 'FAC', 'MRO'},
                         'contract_id': None if i % 17 == 0 or supplier_num == 6 else f'CT-{supplier_num:02d}'})
    repeated = deepcopy(invoices[10])
    repeated['row_id'] = 'ROW-0121'
    repeated['invoice_number'] = ' inv 0011 '
    repeated['supplier_record_id'] = 'V05A'
    unresolved = deepcopy(invoices[1])
    unresolved.update(row_id='ROW-0122', invoice_number='INV-UNRESOLVED', supplier_record_id='V01C')
    bad_amount = deepcopy(invoices[2])
    bad_amount.update(row_id='ROW-0123', invoice_number='INV-BAD-AMOUNT', amount_paise=bad_amount['amount_paise'] + 100)
    invoices.extend([repeated, unresolved, bad_amount])
    return {'suppliers': suppliers, 'invoices': invoices, 'purchase_orders': pos,
            'contracts': contracts, 'taxonomy': taxonomy}
