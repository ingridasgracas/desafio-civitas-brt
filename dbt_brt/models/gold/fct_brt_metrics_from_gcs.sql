{{
  config(
    materialized='table',
    partition_by={
      "field": "ultima_atualizacao",
      "data_type": "timestamp",
      "granularity": "day"
    }
  )
}}

-- Tabela agregada com métricas por linha de BRT
SELECT
    line as linha,
    COUNT(DISTINCT vehicle_id) as total_veiculos,
    ROUND(AVG(speed_kmh), 2) as velocidade_media_kmh,
    ROUND(MAX(speed_kmh), 2) as velocidade_maxima_kmh,
    ROUND(MIN(speed_kmh), 2) as velocidade_minima_kmh,
    MAX(timestamp) as ultima_atualizacao,
    ROUND(AVG(latitude), 6) as latitude_media,
    ROUND(AVG(longitude), 6) as longitude_media,
    
    -- Contadores por categoria de velocidade
    COUNTIF(speed_category = 'parado') as veiculos_parados,
    COUNTIF(speed_category = 'lento') as veiculos_lentos,
    COUNTIF(speed_category = 'moderado') as veiculos_moderados,
    COUNTIF(speed_category = 'rapido') as veiculos_rapidos,
    
    -- Contadores por período do dia
    COUNTIF(period_of_day = 'manha') as registros_manha,
    COUNTIF(period_of_day = 'tarde') as registros_tarde,
    COUNTIF(period_of_day = 'noite') as registros_noite,
    COUNTIF(period_of_day = 'madrugada') as registros_madrugada,
    
    -- Contadores por sentido
    COUNTIF(sentido = 'ida') as registros_ida,
    COUNTIF(sentido = 'volta') as registros_volta,
    
    COUNT(*) as total_registros,
    CURRENT_TIMESTAMP() as processado_em

FROM {{ ref('stg_brt_gps_from_gcs') }}

GROUP BY line
