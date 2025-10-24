{{ config(materialized='table', alias='stg_tren_ligero') }}

select
    cast(rtl.fecha as date) as fecha,
    cast(rtl.tipo_pago as text) as tipo_pago,
    cast(rtl.afluencia as float) as afluencia,
    cast(rtl.anio as int) as anio,
    cast(rtl.mes as text) as mes
from {{ source('public', 'raw_tren_ligero') }} rtl