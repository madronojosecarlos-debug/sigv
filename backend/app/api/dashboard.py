"""
Endpoints del Dashboard / Panel Principal
- Estadísticas generales
- Resumen de vehículos por zona
- Mapa interactivo
- Listados prioritarios
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from ..database import get_db
from ..config import settings
from ..models.vehiculo import Vehiculo
from ..models.etiqueta import Etiqueta, VehiculoEtiqueta
from ..models.zona import Zona
from ..models.movimiento import Movimiento, TipoMovimiento
from ..models.alerta import Alerta
from ..models.usuario import Usuario
from .auth import get_current_user

router = APIRouter()


@router.get("/estadisticas")
async def obtener_estadisticas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas generales del sistema"""

    # Contadores de vehículos
    total_vehiculos = db.query(Vehiculo).filter(Vehiculo.activo == True).count()
    en_instalaciones = db.query(Vehiculo).filter(
        Vehiculo.en_instalaciones == True,
        Vehiculo.activo == True
    ).count()

    # Vehículos por zona
    vehiculos_por_zona = []
    zonas = db.query(Zona).filter(Zona.activo == True).order_by(Zona.orden).all()
    for zona in zonas:
        cantidad = db.query(Vehiculo).filter(
            Vehiculo.zona_actual_id == zona.id,
            Vehiculo.en_instalaciones == True
        ).count()
        vehiculos_por_zona.append({
            "zona_id": zona.id,
            "zona_nombre": zona.nombre,
            "zona_codigo": zona.codigo,
            "zona_color": zona.color,
            "cantidad": cantidad
        })

    # Vehículos por etiqueta
    vehiculos_por_etiqueta = []
    etiquetas = db.query(Etiqueta).filter(Etiqueta.activo == True).order_by(Etiqueta.orden).all()
    for etiqueta in etiquetas:
        cantidad = db.query(VehiculoEtiqueta).filter(
            VehiculoEtiqueta.etiqueta_id == etiqueta.id,
            VehiculoEtiqueta.activa == True
        ).count()
        vehiculos_por_etiqueta.append({
            "etiqueta_id": etiqueta.id,
            "etiqueta_nombre": etiqueta.nombre,
            "etiqueta_color": etiqueta.color,
            "cantidad": cantidad
        })

    # Alertas pendientes
    alertas_pendientes = db.query(Alerta).filter(Alerta.resuelta == False).count()
    alertas_no_leidas = db.query(Alerta).filter(
        Alerta.leida == False,
        Alerta.resuelta == False
    ).count()

    # Movimientos hoy
    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    entradas_hoy = db.query(Movimiento).filter(
        Movimiento.tipo == TipoMovimiento.ENTRADA,
        Movimiento.fecha_hora >= hoy
    ).count()
    salidas_hoy = db.query(Movimiento).filter(
        Movimiento.tipo == TipoMovimiento.SALIDA,
        Movimiento.fecha_hora >= hoy
    ).count()

    return {
        "vehiculos": {
            "total": total_vehiculos,
            "en_instalaciones": en_instalaciones,
            "fuera": total_vehiculos - en_instalaciones
        },
        "vehiculos_por_zona": vehiculos_por_zona,
        "vehiculos_por_etiqueta": vehiculos_por_etiqueta,
        "alertas": {
            "pendientes": alertas_pendientes,
            "no_leidas": alertas_no_leidas
        },
        "movimientos_hoy": {
            "entradas": entradas_hoy,
            "salidas": salidas_hoy
        }
    }


@router.get("/mapa")
async def obtener_datos_mapa(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener datos para el mapa interactivo"""
    zonas = db.query(Zona).filter(Zona.activo == True).all()

    resultado = []
    for zona in zonas:
        # Obtener vehículos en esta zona
        vehiculos = db.query(Vehiculo).filter(
            Vehiculo.zona_actual_id == zona.id,
            Vehiculo.en_instalaciones == True
        ).all()

        vehiculos_list = []
        for v in vehiculos:
            # Obtener etiquetas del vehículo
            etiquetas = db.query(VehiculoEtiqueta).filter(
                VehiculoEtiqueta.vehiculo_id == v.id,
                VehiculoEtiqueta.activa == True
            ).all()

            etiquetas_info = []
            for ve in etiquetas:
                etiqueta = db.query(Etiqueta).filter(Etiqueta.id == ve.etiqueta_id).first()
                if etiqueta:
                    etiquetas_info.append({
                        "nombre": etiqueta.nombre,
                        "color": etiqueta.color
                    })

            vehiculos_list.append({
                "id": v.id,
                "matricula": v.matricula,
                "marca": v.marca,
                "modelo": v.modelo,
                "color": v.color,
                "etiquetas": etiquetas_info,
                "fecha_ultimo_movimiento": v.fecha_ultimo_movimiento
            })

        resultado.append({
            "id": zona.id,
            "nombre": zona.nombre,
            "codigo": zona.codigo,
            "tipo": zona.tipo,
            "pos_x": zona.pos_x,
            "pos_y": zona.pos_y,
            "ancho": zona.ancho,
            "alto": zona.alto,
            "color": zona.color,
            "vehiculos": vehiculos_list,
            "cantidad_vehiculos": len(vehiculos_list)
        })

    return resultado


@router.get("/vehiculos-inactivos")
async def listar_vehiculos_inactivos(
    dias: int = Query(default=20, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar vehículos que llevan más de X días sin movimiento"""
    fecha_limite = datetime.utcnow() - timedelta(days=dias)

    vehiculos = db.query(Vehiculo).filter(
        Vehiculo.en_instalaciones == True,
        Vehiculo.fecha_ultimo_movimiento < fecha_limite
    ).order_by(Vehiculo.fecha_ultimo_movimiento.asc()).limit(limit).all()

    resultado = []
    for v in vehiculos:
        dias_inactivo = (datetime.utcnow() - v.fecha_ultimo_movimiento).days if v.fecha_ultimo_movimiento else 0

        resultado.append({
            "id": v.id,
            "matricula": v.matricula,
            "marca": v.marca,
            "modelo": v.modelo,
            "cliente_nombre": v.cliente_nombre,
            "zona_actual": v.zona_actual.nombre if v.zona_actual else None,
            "dias_inactivo": dias_inactivo,
            "fecha_ultimo_movimiento": v.fecha_ultimo_movimiento
        })

    return resultado


@router.get("/vehiculos-esperando-piezas")
async def listar_vehiculos_esperando_piezas(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar vehículos con etiqueta 'Esperando piezas' o similar"""
    # Buscar etiquetas que contengan "pieza" o "espera"
    etiquetas_espera = db.query(Etiqueta).filter(
        Etiqueta.activo == True,
        (Etiqueta.nombre.ilike("%pieza%")) | (Etiqueta.nombre.ilike("%espera%"))
    ).all()

    if not etiquetas_espera:
        return []

    etiqueta_ids = [e.id for e in etiquetas_espera]

    # Buscar vehículos con estas etiquetas
    vehiculo_etiquetas = db.query(VehiculoEtiqueta).filter(
        VehiculoEtiqueta.etiqueta_id.in_(etiqueta_ids),
        VehiculoEtiqueta.activa == True
    ).order_by(VehiculoEtiqueta.fecha_asignacion.asc()).limit(limit).all()

    resultado = []
    for ve in vehiculo_etiquetas:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == ve.vehiculo_id).first()
        etiqueta = db.query(Etiqueta).filter(Etiqueta.id == ve.etiqueta_id).first()

        if vehiculo:
            dias_esperando = (datetime.utcnow() - ve.fecha_asignacion).days if ve.fecha_asignacion else 0

            resultado.append({
                "id": vehiculo.id,
                "matricula": vehiculo.matricula,
                "marca": vehiculo.marca,
                "modelo": vehiculo.modelo,
                "cliente_nombre": vehiculo.cliente_nombre,
                "cliente_telefono": vehiculo.cliente_telefono,
                "etiqueta": etiqueta.nombre if etiqueta else None,
                "etiqueta_color": etiqueta.color if etiqueta else None,
                "dias_esperando": dias_esperando,
                "fecha_asignacion_etiqueta": ve.fecha_asignacion
            })

    return resultado


@router.get("/vehiculos-por-tiempo-estancia")
async def listar_vehiculos_por_tiempo_estancia(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar vehículos ordenados por tiempo de estancia (más antiguos primero)"""
    vehiculos = db.query(Vehiculo).filter(
        Vehiculo.en_instalaciones == True,
        Vehiculo.fecha_primera_entrada.isnot(None)
    ).order_by(Vehiculo.fecha_primera_entrada.asc()).limit(limit).all()

    resultado = []
    for v in vehiculos:
        dias_estancia = (datetime.utcnow() - v.fecha_primera_entrada).days if v.fecha_primera_entrada else 0

        # Obtener etiquetas
        etiquetas = db.query(VehiculoEtiqueta).filter(
            VehiculoEtiqueta.vehiculo_id == v.id,
            VehiculoEtiqueta.activa == True
        ).all()

        etiquetas_info = []
        for ve in etiquetas:
            etiqueta = db.query(Etiqueta).filter(Etiqueta.id == ve.etiqueta_id).first()
            if etiqueta:
                etiquetas_info.append({
                    "nombre": etiqueta.nombre,
                    "color": etiqueta.color
                })

        resultado.append({
            "id": v.id,
            "matricula": v.matricula,
            "marca": v.marca,
            "modelo": v.modelo,
            "cliente_nombre": v.cliente_nombre,
            "zona_actual": v.zona_actual.nombre if v.zona_actual else None,
            "dias_estancia": dias_estancia,
            "fecha_entrada": v.fecha_primera_entrada,
            "etiquetas": etiquetas_info
        })

    return resultado


@router.get("/actividad-reciente")
async def obtener_actividad_reciente(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener actividad reciente (entradas/salidas)"""
    movimientos = db.query(Movimiento).filter(
        Movimiento.tipo.in_([TipoMovimiento.ENTRADA, TipoMovimiento.SALIDA])
    ).order_by(desc(Movimiento.fecha_hora)).limit(limit).all()

    resultado = []
    for mov in movimientos:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == mov.vehiculo_id).first()

        resultado.append({
            "id": mov.id,
            "tipo": mov.tipo.value,
            "vehiculo_id": mov.vehiculo_id,
            "matricula": vehiculo.matricula if vehiculo else "N/A",
            "marca": vehiculo.marca if vehiculo else None,
            "modelo": vehiculo.modelo if vehiculo else None,
            "zona": mov.zona_destino.nombre if mov.zona_destino else None,
            "fecha_hora": mov.fecha_hora,
            "manual": mov.manual
        })

    return resultado
