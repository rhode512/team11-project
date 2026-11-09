-- Step 1.5: Create the views. Views store only the query, so they can be
-- created before the tables have data.
--
-- PowerShell:
-- Get-Content sql/02_views.sql | docker exec -i team11-mariadb mariadb -u team11 -pchange_me team11

-- The schools we are studying: Texas public four-year universities
CREATE OR REPLACE VIEW tx_public_4yr AS
SELECT i.unitid, i.instnm, i.carnegie,
       s.pct_pell, s.npt41_pub, s.pell_debt_mdn,
       s.grad_debt_mdn, s.md_earn_wne_p10, s.mn_earn_wne_inc1_p10
FROM institution i
INNER JOIN scorecard_outcomes s ON i.unitid = s.unitid
WHERE i.stabbr = 'TX'
  AND i.control = 1
  AND i.iclevel = 1
  AND s.npt41_pub IS NOT NULL
  AND s.md_earn_wne_p10 IS NOT NULL;

-- Each school's share of bachelor's degrees by field family
CREATE OR REPLACE VIEW program_mix AS
WITH bach AS (
  SELECT c.unitid, c.cip2, SUM(c.ctotalt) AS degrees
  FROM completions c
  INNER JOIN tx_public_4yr t ON c.unitid = t.unitid
  WHERE c.awlevel = 5
  GROUP BY c.unitid, c.cip2
),
totals AS (
  SELECT unitid, SUM(degrees) AS total_degrees
  FROM bach
  GROUP BY unitid
)
SELECT b.unitid, b.cip2, f.family_name, b.degrees,
       b.degrees / t.total_degrees AS share
FROM bach b
INNER JOIN totals t ON b.unitid = t.unitid
LEFT JOIN cip_family f ON b.cip2 = f.cip2;

-- Each school's bachelor's earnings by field family,
-- weighted by the number of degrees in each 4-digit field
CREATE OR REPLACE VIEW field_earnings AS
SELECT fo.unitid, fo.cip2,
       SUM(fo.earn_mdn * fo.n_awards) / SUM(fo.n_awards) AS uni_field_earn
FROM field_outcomes fo
INNER JOIN tx_public_4yr t ON fo.unitid = t.unitid
WHERE fo.credlev = 3
  AND fo.earn_mdn IS NOT NULL
  AND fo.n_awards > 0
GROUP BY fo.unitid, fo.cip2;
