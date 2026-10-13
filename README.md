# Procurement Spend Analytics

Three related Python and SQL prototypes for exploring supplier data quality, spend visibility, and invoice exceptions. All records are fictional and generated locally. No customer data, credentials, external services, or paid dependencies are required.

**Status:** working practice prototypes. AI-assisted development. These examples demonstrate analytical workflows and are not production procurement controls.

## Projects

| Project | What it demonstrates | Source |
|---|---|---|
| Supplier Data Quality | Name standardisation, supplier alias mapping, duplicate review and traceability | [Supplier module](projects/supplier_data_quality/) |
| Spend Visibility | Category hierarchy, SQL aggregation, supplier concentration and grouped-total reconciliation | [Spend module](projects/spend_visibility/) |
| Invoice Validation | Data-quality checks, duplicate invoice handling, PO comparison and policy-review flags | [Invoice module](projects/invoice_validation/) |

## Run the examples

Use Python 3.10 or later. The project uses only the standard library.

```bash
python run_portfolio.py
python -m unittest -v test_portfolio.py
```

On systems where Python is named `python3`, replace `python` with `python3`.

The runner regenerates the sample data and reports inside this repository. Open [the analysis report](outputs/analysis_report.md) to review the results. The generated SQLite database is excluded from version control; rerunning the examples recreates it.

## Sample results

| Measure | Result |
|---|---:|
| Source supplier records | 13 |
| Canonical suppliers | 6 |
| Supplier records requiring manual review | 1 |
| Source invoice rows | 123 |
| Invoice rows accepted for analysis | 120 |
| Excluded rows with recorded reasons | 3 |
| Accepted sample spend | INR 303,350.00 |
| Top-three supplier share of accepted spend | 55.32% |

These figures describe the fictional dataset. They do not represent customer savings or a business engagement.

## Data flow

The supplier module first maps known aliases using sample registration identifiers. The invoice module validates required fields and invoice arithmetic, quarantines conflicting references, and removes identical repeated records. It then compares accepted invoices with purchase orders and sample policy inputs. The spend module stores the accepted population in SQLite and produces reconciled summaries by supplier, category, business unit, geography and month.

## Outputs

- `data/sample_procurement_data.json`: reproducible suppliers, invoices, purchase orders, contracts and taxonomy.
- `outputs/01_supplier_normalisation.json`: original records, canonical IDs and manual-review candidates.
- `outputs/02_spend_analysis.json`: SQL summaries and concentration measures.
- `outputs/03_invoice_checks.json`: invoice-level PO and policy checks.
- `outputs/excluded_records.json`: exclusion reasons and retained-record links where applicable.
- `outputs/analysis_report.md`: findings, review questions and limitations.
- `spend_analysis.sql`: the SQL queries used by the reporting module.

## Validation

Seven automated tests check supplier identity boundaries, duplicate references across supplier aliases, conflicting invoices, invoice-number scope, the distinction between non-PO and policy-review spend, and reconciliation across reporting dimensions.

```bash
python -m unittest -v test_portfolio.py
```

## Assumptions and limitations

- Supplier names and registration identifiers are fictional. Identifiers beginning with `DEMO-REG` are not real tax IDs.
- Money is stored as integer paise. All records use INR.
- The sample uses one invoice line per invoice and one invoice per purchase order. Partial billing and multi-line invoice matching are not implemented.
- Taxes, currency conversion, credit notes and goods-receipt matching are outside the current scope.
- Name similarity alone does not justify merging suppliers. Unresolved names remain in a review queue.
- Non-PO invoices are not automatically classified as maverick spend. Supplier approval and required contract coverage are checked separately.
- Spend totals include data-quality-valid invoices with PO or policy exceptions awaiting review.
- The four-supplier fragmentation threshold is illustrative. Supplier count and concentration alone do not prove risk or savings potential.

## Possible extensions

Add reviewed supplier mappings with an audit trail, support cumulative invoice quantities against PO lines, or build an Excel/Power BI report from the validated outputs. These extensions are not part of the current implementation.
