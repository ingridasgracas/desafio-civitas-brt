{{
  config(
    materialized='view',
    schema='brt_dataset_silver'
  )
}}

-- View que lê da tabela externa do GCS e aplica transformações
SELECT
    timestamp,
    vehicle_id,
    line,
    latitude,
    longitude,
    speed as speed_kmh,
    gps_timestamp,
    placa,
    sentido,
    trajeto,
    
    -- Adicionar categorização de velocidade
    CASE
        WHEN speed = 0 THEN 'parado'
        WHEN speed < 20 THEN 'lento'
        WHEN speed < 40 THEN 'moderado'
        ELSE 'rapido'
    END as speed_category,
    
    -- Adicionar período do dia
    CASE
        WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 6 AND 11 THEN 'manha'
        WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 12 AND 17 THEN 'tarde'
        WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 18 AND 23 THEN 'noite'
        ELSE 'madrugada'
    END as period_of_day,
    
    -- Hash único para identificação
    TO_HEX(MD5(CONCAT(CAST(vehicle_id AS STRING), '_', CAST(timestamp AS STRING)))) as record_hash,
    
    -- Metadados
    CURRENT_TIMESTAMP() as processed_at

FROM {{ source('gcs_bronze', 'external_brt_gps_data') }}

WHERE
    -- Validar coordenadas
    latitude BETWEEN -90 AND 90
    AND longitude BETWEEN -180 AND 180
    -- Remover registros sem linha definida
    AND line IS NOT NULL
    AND line != '0'
