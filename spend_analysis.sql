-- supplier_spend
SELECT supplier_id, COUNT(*) AS invoices,
        SUM(amount_paise) AS spend_paise FROM spend GROUP BY supplier_id
        ORDER BY spend_paise DESC, supplier_id;

-- category_spend
SELECT parent_category, category, COUNT(DISTINCT supplier_id) AS suppliers,
        SUM(amount_paise) AS spend_paise FROM spend GROUP BY parent_category, category
        ORDER BY spend_paise DESC, category;

-- business_unit_spend
SELECT business_unit, SUM(amount_paise) AS spend_paise
        FROM spend GROUP BY business_unit ORDER BY spend_paise DESC;

-- geography_spend
SELECT geography, SUM(amount_paise) AS spend_paise
        FROM spend GROUP BY geography ORDER BY spend_paise DESC;

-- monthly_spend
SELECT substr(invoice_date,1,7) AS month, SUM(amount_paise) AS spend_paise
        FROM spend GROUP BY month ORDER BY month;

-- policy_review
SELECT SUM(policy_review) AS invoice_count,
        SUM(CASE WHEN policy_review = 1 THEN amount_paise ELSE 0 END) AS spend_paise FROM spend;