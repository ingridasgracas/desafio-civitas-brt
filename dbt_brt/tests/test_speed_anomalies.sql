-- Teste customizado: Verificar velocidades anômalas
-- Detecta velocidades fisicamente impossíveis para ônibus BRT

SELECT 
    vehicle_id,
    line,
    speed_kmh,
    capture_timestamp
FROM {{ ref('stg_brt_gps_cleaned') }}
WHERE 
    -- Velocidade negativa (impossível)
    speed_kmh < 0
    -- Velocidade excessivamente alta para ônibus urbano (>120 km/h)
    OR speed_kmh > 120
    -- Velocidade muito alta para BRT em área urbana (>80 km/h é suspeito)
    OR speed_kmh > 80