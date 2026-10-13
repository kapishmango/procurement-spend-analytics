# Spend Visibility

Uses SQLite to aggregate accepted invoices by supplier, category, business unit, geography and month. A two-level category hierarchy keeps unmapped commodity codes visible in an Unclassified bucket.

**Input:** validated invoices with canonical supplier IDs and policy-check results.

**Outputs:** `outputs/02_spend_analysis.json`, `spend_analysis.sql` and the generated `outputs/spend.sqlite` database.

Run `python run_portfolio.py` from the repository root. The shared test suite checks that each reporting dimension reconciles to the same accepted spend total. Concentration and fragmentation measures are review indicators, not measured savings.
