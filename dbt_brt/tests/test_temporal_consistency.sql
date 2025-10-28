-- Teste customizado: Verificar consistência temporal
-- Garante que não há registros com timestamps futuros ou muito antigos

SELECT 
    vehicle_id,
    capture_timestamp,
    gps_timestamp
FROM {{ ref('stg_brt_gps_cleaned') }}
WHERE 
    -- Timestamps futuros (mais de 1 hora no futuro)
    capture_timestamp > TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
    -- Timestamps muito antigos (mais de 30 dias)
    OR capture_timestamp < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    -- GPS timestamp muito desatualizado em relação ao capture
    OR ABS(TIMESTAMP_DIFF(capture_timestamp, gps_timestamp, MINUTE)) > 60