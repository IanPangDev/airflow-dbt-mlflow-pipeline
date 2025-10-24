{{ config(materialized='view', alias='vw_afluencia_transportes_forecasting') }}

select
	at.fecha,
	sum(at.afluencia_tren_ligero) as afluencia_tren_ligero,
	sum(at.afluencia_trolebus) as afluencia_trolebus,
	sum(at.afluencia_cablebus) as afluencia_cablebus,
	LTRIM(RTRIM(TO_CHAR(at.fecha, 'Day'))) as dia_nombre,
	DATE_PART('day', at.fecha) as dia,
	DATE_PART('month', at.fecha) as mes,
	case when cdf.dia is not null then true else false end as es_festivo
from {{ ref('vw_afluencia_transportes') }} at
left join {{ source('public', 'cat_dias_festivos')}} cdf
	on cdf.dia = DATE_PART('day', at.fecha) and cdf.mes = DATE_PART('month', at.fecha)
group by 
	at.fecha, cdf.dia, cdf.mes
order by 
	at.fecha asc