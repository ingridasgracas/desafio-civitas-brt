-- Teste customizado: Verificar integridade das coordenadas GPS
-- Garante que não existem coordenadas impossíveis ou inválidas

SELECT 
    vehicle_id,
    latitude,
    longitude,
    capture_timestamp
FROM {{ ref('stg_brt_gps_cleaned') }}
WHERE 
    -- Coordenadas fora dos limites físicos possíveis
    latitude NOT BETWEEN -90 AND 90
    OR longitude NOT BETWEEN -180 AND 180
    -- Coordenadas excessivamente fora do Rio de Janeiro (margem de segurança)
    OR latitude NOT BETWEEN -24 AND -22
    OR longitude NOT BETWEEN -44 AND -42
    -- Coordenadas zeradas (provavelmente erro de GPS)
    OR (latitude = 0 AND longitude = 0)