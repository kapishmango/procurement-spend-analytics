# Invoice Validation

Checks invoice identifiers, dates, currency and arithmetic before comparing records with purchase orders. Repeated identical records are linked to a retained row; conflicting invoice references are quarantined for review.

**Input:** fictional invoices, normalised suppliers, purchase orders and contracts.

**Outputs:** `outputs/03_invoice_checks.json` and `outputs/excluded_records.json`.

Run `python run_portfolio.py` from the repository root. PO checks cover missing references and supplier, currency, quantity and unit-price differences. Policy checks separately review supplier approval and required contract coverage. The prototype assumes one line and one invoice per PO; cumulative partial invoicing is not implemented.
