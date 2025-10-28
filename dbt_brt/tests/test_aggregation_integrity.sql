-- Teste customizado: Verificar integridade das métricas agregadas
-- Garante que as agregações na camada Gold estão matematicamente corretas

WITH source_data AS (
    SELECT 
        EXTRACT(DATE FROM capture_timestamp) as test_date,
        line,
        period_of_day,
        COUNT(DISTINCT vehicle_id) as silver_vehicle_count,
        COUNT(*) as silver_total_observations,
        AVG(speed_kmh) as silver_avg_speed
    FROM {{ ref('stg_brt_gps_cleaned') }}
    WHERE EXTRACT(DATE FROM capture_timestamp) = CURRENT_DATE()
    GROUP BY 1, 2, 3
),

gold_data AS (
    SELECT 
        date_partition,
        line,
        period_of_day,
        total_vehicles as gold_vehicle_count,
        total_observations as gold_total_observations,
        avg_speed_kmh as gold_avg_speed
    FROM {{ ref('fct_brt_line_metrics') }}
    WHERE date_partition = CURRENT_DATE()
)

SELECT 
    s.test_date,
    s.line,
    s.period_of_day,
    'Vehicle count mismatch' as error_type
FROM source_data s
JOIN gold_data g 
    ON s.test_date = g.date_partition 
    AND s.line = g.line 
    AND s.period_of_day = g.period_of_day
WHERE s.silver_vehicle_count != g.gold_vehicle_count

UNION ALL

SELECT 
    s.test_date,
    s.line,
    s.period_of_day,
    'Observation count mismatch' as error_type
FROM source_data s
JOIN gold_data g 
    ON s.test_date = g.date_partition 
    AND s.line = g.line 
    AND s.period_of_day = g.period_of_day
WHERE s.silver_total_observations != g.gold_total_observations

UNION ALL

SELECT 
    s.test_date,
    s.line,
    s.period_of_day,
    'Average speed mismatch' as error_type
FROM source_data s
JOIN gold_data g 
    ON s.test_date = g.date_partition 
    AND s.line = g.line 
    AND s.period_of_day = g.period_of_day
WHERE ABS(s.silver_avg_speed - g.gold_avg_speed) > 0.1