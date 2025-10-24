{{ config(materialized='view', alias='vw_afluencia_transportes') }}

with process_tren_ligero as (
    select 
        rtl.fecha,
        rtl.tipo_pago,
        sum(rtl.afluencia) as afluencia
    from {{ ref('stg_tren_ligero') }} rtl
    group by fecha, tipo_pago
),

process_cablebus as (
    select
        rc.fecha,
        rc.tipo_pago,
        sum(rc.afluencia) as afluencia
    from {{ ref('stg_cablebus') }} rc
    group by fecha, tipo_pago
),

process_trolebus as (
    select
        tr.fecha,
        tr.tipo_pago,
        sum(tr.afluencia) as afluencia
    from {{ ref('stg_trolebus') }} tr
    group by fecha, tipo_pago
)

select 
    ptl.fecha,
    ptl.tipo_pago,
    ptl.afluencia as afluencia_tren_ligero,
    pcb.afluencia as afluencia_cablebus,
    ptb.afluencia as afluencia_trolebus
from process_tren_ligero ptl
join process_cablebus pcb
    on ptl.fecha = pcb.fecha and ptl.tipo_pago = pcb.tipo_pago
join process_trolebus ptb
    on ptl.fecha = ptb.fecha and ptl.tipo_pago = ptb.tipo_pago