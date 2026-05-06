WITH agg_measures AS (
    SELECT
        item_no,
        operator,
        height,
        AVG(height) OVER(
            PARTITION BY operator
            ORDER BY
                item_no ROWS BETWEEN 4 PRECEDING
                AND CURRENT ROW
        ) AS avg_height,
        STDDEV(height) OVER(
            PARTITION BY operator
            ORDER BY
                item_no ROWS BETWEEN 4 PRECEDING
                AND CURRENT ROW
        ) AS stddev_height,
        ROW_NUMBER() OVER(
            PARTITION BY operator
            ORDER BY
                item_no
        ) AS row_number
    FROM
        manufacturing_parts
),
limits AS (
    SELECT
        item_no,
        operator,
        height,
        row_number,
        avg_height,
        stddev_height,
        avg_height + ((3 * stddev_height) / SQRT(5)) AS ucl,
        avg_height - ((3 * stddev_height) / SQRT(5)) AS lcl
    FROM
        agg_measures
    WHERE
        row_number >= 5
)
SELECT
    operator,
    row_number,
    height,
    avg_height,
    stddev_height,
    ucl,
    lcl,
    CASE
        WHEN height > ucl
        OR height < lcl THEN TRUE
        ELSE FALSE
    END AS alert
FROM
    limits
ORDER BY
    item_no;