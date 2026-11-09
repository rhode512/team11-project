-- Step 1.5: Create the final tables with primary and foreign keys.
-- Rerunning this drops and rebuilds everything (raw_ tables are kept).
--
-- PowerShell:
-- Get-Content sql/01_schema.sql | docker exec -i team11-mariadb mariadb -u team11 -pchange_me team11

DROP VIEW IF EXISTS field_earnings, program_mix, tx_public_4yr;
DROP TABLE IF EXISTS completions, field_outcomes, scorecard_outcomes,
                     cip_family, institution;

CREATE TABLE institution (
  unitid    INT PRIMARY KEY,
  instnm    VARCHAR(150),
  stabbr    CHAR(2),
  control   TINYINT,       -- 1 = public
  iclevel   TINYINT,       -- 1 = four-year
  carnegie  SMALLINT
);

CREATE TABLE cip_family (
  cip2         CHAR(2) PRIMARY KEY,
  family_name  VARCHAR(150)
);

CREATE TABLE scorecard_outcomes (
  unitid                INT PRIMARY KEY,
  pct_pell              DECIMAL(5,4),
  npt41_pub             DECIMAL(10,2),   -- net price, $0-30k family income
  pell_debt_mdn         DECIMAL(10,2),
  grad_debt_mdn         DECIMAL(10,2),
  md_earn_wne_p10       DECIMAL(10,2),
  mn_earn_wne_inc1_p10  DECIMAL(10,2),
  FOREIGN KEY (unitid) REFERENCES institution(unitid)
);

CREATE TABLE field_outcomes (
  unitid    INT,
  cipcode   CHAR(4),
  cip2      CHAR(2),
  credlev   TINYINT,         -- 3 = bachelor's
  n_awards  INT,
  earn_mdn  DECIMAL(10,2),
  debt_mdn  DECIMAL(10,2),
  PRIMARY KEY (unitid, cipcode, credlev),
  FOREIGN KEY (unitid) REFERENCES institution(unitid),
  FOREIGN KEY (cip2) REFERENCES cip_family(cip2)
);

CREATE TABLE completions (
  unitid    INT,
  cipcode   CHAR(7),         -- e.g. 52.0201
  cip2      CHAR(2),
  majornum  TINYINT,
  awlevel   TINYINT,         -- 5 = bachelor's
  ctotalt   INT,
  PRIMARY KEY (unitid, cipcode, majornum, awlevel),
  FOREIGN KEY (unitid) REFERENCES institution(unitid),
  FOREIGN KEY (cip2) REFERENCES cip_family(cip2)
);
