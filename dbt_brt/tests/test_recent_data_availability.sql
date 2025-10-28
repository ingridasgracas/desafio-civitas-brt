-- Teste customizado: Verificar se existem dados GPS válidos recentes
-- Garante que dados foram capturados nas últimas 24 horas

SELECT COUNT(*) as records_count
FROM {{ ref('stg_brt_gps_cleaned') }}
WHERE capture_date >= CURRENT_DATE() - 1
HAVING COUNT(*) = 0