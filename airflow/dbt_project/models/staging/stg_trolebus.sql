{{ config(materialized='table', alias='stg_trolebus') }}

select
    cast(tr.fecha as date) as fecha,
    cast(tr.tipo_pago as text) as tipo_pago,
    cast(tr.linea as text) as linea,
    cast(tr.afluencia as float) as afluencia,
    cast(tr.anio as int) as anio,
    cast(tr.mes as text) as mes
from {{ source('public', 'raw_trolebus') }} tr