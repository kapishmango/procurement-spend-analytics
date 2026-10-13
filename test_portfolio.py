"""Checks for materially incorrect merges, double counting and PO classification."""
import unittest
import tempfile
from pathlib import Path
from copy import deepcopy
from generate_sample_data import generate
from projects.supplier_data_quality import normalise_suppliers
from projects.invoice_validation import clean_invoices, reconcile
from projects.spend_visibility import analyse


class PortfolioChecks(unittest.TestCase):
    def setUp(self):
        self.data = generate()
        self.suppliers = normalise_suppliers(self.data['suppliers'])

    def test_name_only_records_are_not_automatically_merged(self):
        review = self.suppliers[-1]
        self.assertIsNone(review['canonical_supplier_id'])
        self.assertEqual(review['candidate_supplier_ids'], ['S01'])

    def test_same_names_with_different_registration_ids_stay_separate(self):
        rows = deepcopy(self.data['suppliers'][:2])
        rows[1]['registration_id'] = 'DIFFERENT-ID'
        mapped = normalise_suppliers(rows)
        self.assertNotEqual(mapped[0]['canonical_supplier_id'], mapped[1]['canonical_supplier_id'])

    def test_duplicates_across_supplier_aliases_do_not_inflate_spend(self):
        valid, excluded = clean_invoices(self.data['invoices'], self.suppliers)
        self.assertEqual(len(valid), 120)
        self.assertEqual(len(excluded), 3)
        self.assertEqual(sum(r['amount_paise'] for r in valid), sum(r['amount_paise'] for r in self.data['invoices'][:120]))
        reasons = {x for r in excluded for x in r['reasons']}
        self.assertEqual(reasons, {'repeated_identical_invoice_record', 'unresolved_supplier', 'amount_mismatch'})

    def test_conflicting_reference_is_quarantined_not_arbitrarily_deduplicated(self):
        first = deepcopy(self.data['invoices'][4])
        second = deepcopy(first)
        second.update(row_id='CONFLICT', quantity=first['quantity']+1)
        second['amount_paise'] = second['quantity'] * second['unit_price_paise']
        valid, excluded = clean_invoices([first, second], self.suppliers)
        self.assertEqual(valid, [])
        self.assertEqual(len(excluded), 2)

    def test_invoice_number_is_scoped_to_supplier(self):
        first, second = deepcopy(self.data['invoices'][:2])
        second['invoice_number'] = first['invoice_number']
        valid, _ = clean_invoices([first, second], self.suppliers)
        self.assertEqual(len(valid), 2)

    def test_missing_po_alone_is_not_maverick_spend(self):
        rows, _ = clean_invoices(self.data['invoices'][:1], self.suppliers)
        checked = reconcile(rows, self.data['purchase_orders'], self.data['contracts'])[0]
        self.assertIn('no_po_reference', checked['po_checks'])
        self.assertEqual(checked['policy_checks'], [])

    def test_price_and_quantity_exceptions_and_category_reconciliation(self):
        rows, _ = clean_invoices(self.data['invoices'], self.suppliers)
        checked = reconcile(rows, self.data['purchase_orders'], self.data['contracts'])
        self.assertTrue(any('unit_price_above_po' in r['po_checks'] for r in checked))
        self.assertTrue(any('quantity_above_po' in r['po_checks'] for r in checked))
        with tempfile.TemporaryDirectory() as tmp:
            output = analyse(checked, self.data['taxonomy'], Path(tmp)/'test.sqlite')
        total = output['metrics']['total_spend_paise']
        for key in ['supplier_spend', 'category_spend', 'business_unit_spend', 'geography_spend', 'monthly_spend']:
            self.assertEqual(total, sum(r['spend_paise'] for r in output[key]))
        self.assertTrue(any(r['category'] == 'Unclassified' for r in output['category_spend']))


if __name__ == '__main__':
    unittest.main()
