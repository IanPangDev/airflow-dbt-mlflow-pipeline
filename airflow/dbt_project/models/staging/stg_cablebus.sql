{{ config(materialized='table', alias='stg_cablebus') }}

select
    cast(rc.fecha as date) as fecha,
    cast(rc.tipo_pago as text) as tipo_pago,
    cast(rc.linea as text) as linea,
    cast(rc.afluencia as float) as afluencia,
    cast(rc.anio as int) as anio,
    cast(rc.mes as text) as mes
from {{ source('public', 'raw_cablebus') }} rc