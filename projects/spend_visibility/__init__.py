"""Practice project 2: hierarchical spend reporting in SQLite."""
import sqlite3


QUERIES = {
    'supplier_spend': '''SELECT supplier_id, COUNT(*) AS invoices,
        SUM(amount_paise) AS spend_paise FROM spend GROUP BY supplier_id
        ORDER BY spend_paise DESC, supplier_id''',
    'category_spend': '''SELECT parent_category, category, COUNT(DISTINCT supplier_id) AS suppliers,
        SUM(amount_paise) AS spend_paise FROM spend GROUP BY parent_category, category
        ORDER BY spend_paise DESC, category''',
    'business_unit_spend': '''SELECT business_unit, SUM(amount_paise) AS spend_paise
        FROM spend GROUP BY business_unit ORDER BY spend_paise DESC''',
    'geography_spend': '''SELECT geography, SUM(amount_paise) AS spend_paise
        FROM spend GROUP BY geography ORDER BY spend_paise DESC''',
    'monthly_spend': '''SELECT substr(invoice_date,1,7) AS month, SUM(amount_paise) AS spend_paise
        FROM spend GROUP BY month ORDER BY month''',
    'policy_review': '''SELECT SUM(policy_review) AS invoice_count,
        SUM(CASE WHEN policy_review = 1 THEN amount_paise ELSE 0 END) AS spend_paise FROM spend'''
}


def analyse(rows, taxonomy, database_path):
    connection = sqlite3.connect(database_path)
    with connection:
        connection.execute('DROP TABLE IF EXISTS spend')
        connection.execute('''CREATE TABLE spend (
            row_id TEXT PRIMARY KEY, invoice_date TEXT, supplier_id TEXT,
            parent_category TEXT, category TEXT, business_unit TEXT, geography TEXT,
            amount_paise INTEGER, policy_review INTEGER)''')
        for row in rows:
            parent, category = taxonomy.get(row['commodity_code'], ['Unclassified', 'Unclassified'])
            connection.execute('INSERT INTO spend VALUES (?,?,?,?,?,?,?,?,?)', (
                row['row_id'], row['invoice_date'], row['canonical_supplier_id'], parent, category,
                row['business_unit'], row['geography'], row['amount_paise'], int(bool(row['policy_checks']))))
    connection.row_factory = sqlite3.Row
    output = {name: [dict(r) for r in connection.execute(sql)] for name, sql in QUERIES.items()}
    connection.close()
    total = sum(r['amount_paise'] for r in rows)
    grouped_total = sum(r['spend_paise'] for r in output['category_spend'])
    assert total == grouped_total, 'Category totals do not reconcile'
    top_three = sum(r['spend_paise'] for r in output['supplier_spend'][:3])
    output['metrics'] = {'accepted_invoice_count': len(rows), 'total_spend_paise': total,
                         'top_three_supplier_share_pct': round(100 * top_three / total, 2) if total else 0,
                         'fragmented_category_candidates': [r['category'] for r in output['category_spend'] if r['suppliers'] >= 4]}
    return output
