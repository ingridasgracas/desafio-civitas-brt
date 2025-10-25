{{
    config(
        materialized='view',
        description='Camada Silver - Dados do BRT limpos e padronizados'
    )
}}

/*
Modelo Silver - BRT GPS Cleaned
Aplica transformações e limpezas nos dados brutos:
- Remove registros duplicados
- Valida coordenadas GPS (dentro dos limites do Rio de Janeiro)
- Padroniza formatos de data e hora
- Calcula campos derivados
*/

WITH source_data AS (
    SELECT
        capture_timestamp,
        vehicle_id,
        line,
        latitude,
        longitude,
        speed,
        timestamp_gps,
        raw_data
    FROM {{ source('brt_external', 'brt_gps_raw') }}
),

cleaned_data AS (
    SELECT
        -- Identificadores
        vehicle_id,
        line,
        
        -- Timestamps
        CAST(capture_timestamp AS TIMESTAMP) AS capture_timestamp,
        TIMESTAMP_MILLIS(SAFE_CAST(timestamp_gps AS INT64)) AS gps_timestamp,
        
        -- Geolocalização
        CAST(latitude AS FLOAT64) AS latitude,
        CAST(longitude AS FLOAT64) AS longitude,
        
        -- Velocidade
        CAST(speed AS FLOAT64) AS speed_kmh,
        
        -- Campos derivados
        DATE(CAST(capture_timestamp AS TIMESTAMP)) AS capture_date,
        EXTRACT(HOUR FROM CAST(capture_timestamp AS TIMESTAMP)) AS capture_hour,
        EXTRACT(DAYOFWEEK FROM CAST(capture_timestamp AS TIMESTAMP)) AS day_of_week,
        
        -- Validação de coordenadas (Rio de Janeiro aproximado)
        CASE
            WHEN CAST(latitude AS FLOAT64) BETWEEN -23.0 AND -22.7
                AND CAST(longitude AS FLOAT64) BETWEEN -43.8 AND -43.1
            THEN TRUE
            ELSE FALSE
        END AS is_valid_location,
        
        -- Categorização de velocidade
        CASE
            WHEN CAST(speed AS FLOAT64) = 0 THEN 'Parado'
            WHEN CAST(speed AS FLOAT64) BETWEEN 0 AND 20 THEN 'Lento'
            WHEN CAST(speed AS FLOAT64) BETWEEN 20 AND 50 THEN 'Normal'
            WHEN CAST(speed AS FLOAT64) > 50 THEN 'Rápido'
            ELSE 'Desconhecido'
        END AS speed_category,
        
        -- Período do dia
        CASE
            WHEN EXTRACT(HOUR FROM CAST(capture_timestamp AS TIMESTAMP)) BETWEEN 6 AND 11 THEN 'Manhã'
            WHEN EXTRACT(HOUR FROM CAST(capture_timestamp AS TIMESTAMP)) BETWEEN 12 AND 17 THEN 'Tarde'
            WHEN EXTRACT(HOUR FROM CAST(capture_timestamp AS TIMESTAMP)) BETWEEN 18 AND 23 THEN 'Noite'
            ELSE 'Madrugada'
        END AS period_of_day,
        
        -- Metadata
        raw_data
        
    FROM source_data
    
    -- Filtros de qualidade
    WHERE vehicle_id IS NOT NULL
        AND latitude IS NOT NULL
        AND longitude IS NOT NULL
)

SELECT
    *,
    -- Hash único para deduplicação
    TO_HEX(MD5(CONCAT(
        CAST(capture_timestamp AS STRING),
        vehicle_id,
        CAST(latitude AS STRING),
        CAST(longitude AS STRING)
    ))) AS row_hash
    
FROM cleaned_data

-- Filtra apenas localizações válidas
WHERE is_valid_location = TRUE

-- Remove duplicatas baseado em timestamp e veículo
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY vehicle_id, capture_timestamp 
    ORDER BY gps_timestamp DESC
) = 1
