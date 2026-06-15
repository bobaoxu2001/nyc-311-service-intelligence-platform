CREATE OR REPLACE TABLE bronze_311 AS
SELECT
    *
FROM read_parquet('{{ raw_path }}');
