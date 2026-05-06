WITH agg_measures AS (
    SELECT
        AVG(height) AS avg_height,
        STDDEV(height) AS stddev_height
    FROM
        manufacturing_parts
),
limits AS (
    SELECT
        avg_height + (3 * stddev_height) / sqrt(5) AS ucl,
        avg_height - (3 * stddev_height) / sqrt(5) AS lcl
    FROM
        agg_measures
)
SELECT
    item_no,
    operator,
    height,
    lcl,
    ucl,
    CASE
        WHEN (
            height > ucl
            OR height < lcl
        ) THEN TRUE
        ELSE FALSE
    END,
    ROW_NUMBER() OVER(
        ORDER BY
            item_no
    )
FROM
    manufacturing_parts,
    limits
ORDER BY
    item_no;