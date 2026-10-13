# Procurement Analytics Practice Report

All suppliers, identifiers and transactions in this report are fictional sample data. These are practice prototypes, not customer engagements.

## 1 Supplier master data quality

- Source supplier records: 13; canonical suppliers: 6; records pending manual review: 1.
- Registration IDs support consolidation. Name-only matches stay in a review queue; they are not automatically merged.

## 2 Spend visibility

- Source invoice rows: 123; accepted for analysis: 120; excluded with recorded reasons: 3.
- Accepted spend: INR 303,350.00. This includes invoices with PO or policy exceptions awaiting review.
- Top three suppliers account for 55.32% of accepted spend.
- Every category total reconciles to the accepted invoice population. An unmapped commodity remains explicitly Unclassified.

| Parent category | Category | Suppliers | Spend |
|---|---|---:|---:|
| Technology | IT hardware | 6 | INR 65,075.00 |
| Technology | Software | 6 | INR 58,825.00 |
| Services | Logistics | 6 | INR 52,725.00 |
| Indirect materials | Office supplies | 6 | INR 45,700.00 |
| Indirect materials | Maintenance supplies | 6 | INR 42,050.00 |
| Services | Facilities | 6 | INR 37,550.00 |
| Unclassified | Unclassified | 1 | INR 1,425.00 |

Categories with at least four suppliers are candidates for a fragmentation review. Supplier count alone does not establish a consolidation opportunity.

## 3 Invoice and purchase order checks

| Check | Invoice count |
|---|---:|
| no_po_reference | 5 |
| quantity_above_po | 2 |
| unit_price_above_po | 5 |

Policy checks are separate from PO checks. Non-PO spend is not automatically labelled maverick spend.

| Policy review reason | Invoice count |
|---|---:|
| missing_or_invalid_contract_review | 10 |
| non_approved_supplier_review | 20 |

Unique invoices requiring policy review: 20; associated spend: INR 58,075.00. An invoice may have several reasons; its spend is counted once.

## Follow-up questions

- For missing PO references, was a non-PO purchase permitted by policy?
- For price or quantity differences, was there an approved PO amendment?
- For fragmented categories, are specifications and service levels comparable across suppliers?
- For unapproved suppliers or missing contracts, is the master data complete and current?

## Scope and limitations

The model assumes one line and one invoice per PO. It does not aggregate partial invoices against a PO, match goods receipts, handle tax, foreign exchange or credit notes, establish fraud, or calculate realised savings. Multi-line and partial-invoice support would be necessary before business use.
