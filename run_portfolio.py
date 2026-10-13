"""Run all three practice projects using only the Python standard library."""
import json
from pathlib import Path
from collections import Counter
from generate_sample_data import generate
from projects.supplier_data_quality import normalise_suppliers
from projects.invoice_validation import clean_invoices, reconcile
from projects.spend_visibility import analyse, QUERIES


ROOT = Path(__file__).resolve().parent


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def money(paise):
    return f'INR {paise/100:,.2f}'


def run():
    data_dir, out = ROOT/'data', ROOT/'outputs'
    data_dir.mkdir(exist_ok=True)
    out.mkdir(exist_ok=True)
    data = generate()
    save_json(data_dir/'sample_procurement_data.json', data)
    mapped = normalise_suppliers(data['suppliers'])
    accepted, exclusions = clean_invoices(data['invoices'], mapped)
    checked = reconcile(accepted, data['purchase_orders'], data['contracts'])
    analysis = analyse(checked, data['taxonomy'], out/'spend.sqlite')
    save_json(out/'01_supplier_normalisation.json', mapped)
    save_json(out/'02_spend_analysis.json', analysis)
    save_json(out/'03_invoice_checks.json', checked)
    save_json(out/'excluded_records.json', exclusions)
    (ROOT/'spend_analysis.sql').write_text('\n\n'.join(f'-- {k}\n{v};' for k,v in QUERIES.items()), encoding='utf-8')
    exceptions = Counter(c for row in checked for c in row['po_checks'])
    policies = Counter(c for row in checked for c in row['policy_checks'])
    metrics = analysis['metrics']
    normalised_count = len({s['canonical_supplier_id'] for s in mapped if s['canonical_supplier_id']})
    pending = sum(s['match_status'] == 'manual_review' for s in mapped)
    lines = ['# Procurement Analytics Practice Report', '',
             'All suppliers, identifiers and transactions in this report are fictional sample data. These are practice prototypes, not customer engagements.', '',
             '## 1 Supplier master data quality', '',
             f"- Source supplier records: {len(mapped)}; canonical suppliers: {normalised_count}; records pending manual review: {pending}.",
             '- Registration IDs support consolidation. Name-only matches stay in a review queue; they are not automatically merged.', '',
             '## 2 Spend visibility', '',
             f"- Source invoice rows: {len(data['invoices'])}; accepted for analysis: {len(checked)}; excluded with recorded reasons: {len(exclusions)}.",
             f"- Accepted spend: {money(metrics['total_spend_paise'])}. This includes invoices with PO or policy exceptions awaiting review.",
             f"- Top three suppliers account for {metrics['top_three_supplier_share_pct']}% of accepted spend.",
             '- Every category total reconciles to the accepted invoice population. An unmapped commodity remains explicitly Unclassified.', '',
             '| Parent category | Category | Suppliers | Spend |', '|---|---|---:|---:|']
    for r in analysis['category_spend']:
        lines.append(f"| {r['parent_category']} | {r['category']} | {r['suppliers']} | {money(r['spend_paise'])} |")
    lines += ['', 'Categories with at least four suppliers are candidates for a fragmentation review. Supplier count alone does not establish a consolidation opportunity.', '',
              '## 3 Invoice and purchase order checks', '', '| Check | Invoice count |', '|---|---:|']
    for name, count in sorted(exceptions.items()):
        lines.append(f'| {name} | {count} |')
    lines += ['', 'Policy checks are separate from PO checks. Non-PO spend is not automatically labelled maverick spend.', '',
              '| Policy review reason | Invoice count |', '|---|---:|']
    for name, count in sorted(policies.items()):
        lines.append(f'| {name} | {count} |')
    pr = analysis['policy_review'][0]
    lines += ['', f"Unique invoices requiring policy review: {pr['invoice_count']}; associated spend: {money(pr['spend_paise'])}. An invoice may have several reasons; its spend is counted once.", '',
              '## Follow-up questions', '',
              '- For missing PO references, was a non-PO purchase permitted by policy?',
              '- For price or quantity differences, was there an approved PO amendment?',
              '- For fragmented categories, are specifications and service levels comparable across suppliers?',
              '- For unapproved suppliers or missing contracts, is the master data complete and current?', '',
              '## Scope and limitations', '',
              'The model assumes one line and one invoice per PO. It does not aggregate partial invoices against a PO, match goods receipts, handle tax, foreign exchange or credit notes, establish fraud, or calculate realised savings. Multi-line and partial-invoice support would be necessary before business use.']
    (out/'analysis_report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'supplier_records': len(mapped), 'canonical_suppliers': normalised_count,
                      'supplier_reviews': pending, 'invoice_rows': len(data['invoices']),
                      'accepted_invoices': len(checked), 'excluded_rows': len(exclusions),
                      **metrics}, indent=2))


if __name__ == '__main__':
    run()
