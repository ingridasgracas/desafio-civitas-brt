{{
    config(
        materialized='table',
        partition_by={
            'field': 'date_partition',
            'data_type': 'date',
            'granularity': 'day'
        },
        cluster_by=['line', 'period_of_day'],
        description='Camada Gold - Métricas agregadas por linha e período do dia'
    )
}}

/*
Modelo Gold - BRT Line Metrics
Agregações e métricas de negócio prontas para consumo:
- Análise por linha de BRT
- Métricas de operação (velocidade média, total de veículos)
- Agregações temporais
*/

WITH silver_data AS (
    SELECT
        vehicle_id,
        line,
        capture_date,
        capture_hour,
        day_of_week,
        period_of_day,
        latitude,
        longitude,
        speed_kmh,
        speed_category
    FROM {{ ref('stg_brt_gps_cleaned') }}
),

aggregated_metrics AS (
    SELECT
        -- Dimensões
        capture_date AS date_partition,
        line,
        period_of_day,
        
        -- Métricas de frota
        COUNT(DISTINCT vehicle_id) AS total_vehicles,
        COUNT(*) AS total_observations,
        
        -- Métricas de velocidade
        ROUND(AVG(speed_kmh), 2) AS avg_speed_kmh,
        ROUND(MIN(speed_kmh), 2) AS min_speed_kmh,
        ROUND(MAX(speed_kmh), 2) AS max_speed_kmh,
        ROUND(STDDEV(speed_kmh), 2) AS stddev_speed_kmh,
        
        -- Distribuição de velocidade
        COUNTIF(speed_category = 'Parado') AS vehicles_stopped,
        COUNTIF(speed_category = 'Lento') AS vehicles_slow,
        COUNTIF(speed_category = 'Normal') AS vehicles_normal,
        COUNTIF(speed_category = 'Rápido') AS vehicles_fast,
        
        -- Coordenadas médias (centro de operação)
        ROUND(AVG(latitude), 6) AS avg_latitude,
        ROUND(AVG(longitude), 6) AS avg_longitude,
        
        -- Metadata
        MIN(capture_hour) AS first_hour,
        MAX(capture_hour) AS last_hour,
        CURRENT_TIMESTAMP() AS processed_at
        
    FROM silver_data
    
    GROUP BY 
        capture_date,
        line,
        period_of_day
)

SELECT
    *,
    
    -- KPIs calculados
    ROUND(SAFE_DIVIDE(vehicles_stopped, total_vehicles) * 100, 2) AS pct_vehicles_stopped,
    ROUND(SAFE_DIVIDE(vehicles_slow, total_vehicles) * 100, 2) AS pct_vehicles_slow,
    ROUND(SAFE_DIVIDE(vehicles_normal, total_vehicles) * 100, 2) AS pct_vehicles_normal,
    ROUND(SAFE_DIVIDE(vehicles_fast, total_vehicles) * 100, 2) AS pct_vehicles_fast,
    
    -- Taxa de observações por veículo
    ROUND(SAFE_DIVIDE(total_observations, total_vehicles), 2) AS avg_observations_per_vehicle
    
FROM aggregated_metrics
