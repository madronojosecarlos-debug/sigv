"""
Script de inicialización de la base de datos
- Crea un usuario administrador
- Crea zonas predefinidas
- Crea etiquetas predefinidas
- Crea cámaras de ejemplo
"""
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..models.usuario import Usuario, Rol
from ..models.etiqueta import Etiqueta
from ..models.zona import Zona, Camara
from ..models.vehiculo import CampoPersonalizado

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_admin(db: Session):
    """Crear usuario administrador por defecto"""
    admin = db.query(Usuario).filter(Usuario.email == "admin@sigv.local").first()

    if not admin:
        admin = Usuario(
            email="admin@sigv.local",
            nombre="Administrador",
            apellidos="SIGV",
            password_hash=pwd_context.hash("admin123"),
            rol=Rol.ADMINISTRADOR
        )
        db.add(admin)
        db.commit()
        print("Usuario administrador creado: admin@sigv.local / admin123")
    else:
        print("Usuario administrador ya existe")

    return admin


def init_etiquetas(db: Session):
    """Crear etiquetas predefinidas"""
    etiquetas_default = [
        {"nombre": "Recepción", "color": "#3498db", "descripcion": "Vehículo recién llegado", "orden": 1},
        {"nombre": "En diagnóstico", "color": "#9b59b6", "descripcion": "Evaluando daños/reparaciones", "orden": 2},
        {"nombre": "Presupuestado", "color": "#f39c12", "descripcion": "Presupuesto enviado al cliente", "orden": 3},
        {"nombre": "Aprobado", "color": "#27ae60", "descripcion": "Cliente aprobó reparación", "orden": 4},
        {"nombre": "Esperando piezas", "color": "#e74c3c", "descripcion": "Pendiente de recibir piezas", "orden": 5},
        {"nombre": "En reparación", "color": "#2980b9", "descripcion": "Trabajo en curso", "orden": 6},
        {"nombre": "En pintura", "color": "#8e44ad", "descripcion": "En cabina de pintura", "orden": 7},
        {"nombre": "Control de calidad", "color": "#16a085", "descripcion": "Revisión final", "orden": 8},
        {"nombre": "Listo para entrega", "color": "#2ecc71", "descripcion": "Preparado para entregar", "orden": 9, "es_sistema": True},
        {"nombre": "Entregado", "color": "#95a5a6", "descripcion": "Vehículo entregado al cliente", "orden": 10, "es_sistema": True},
    ]

    creadas = 0
    for etiqueta_data in etiquetas_default:
        existente = db.query(Etiqueta).filter(Etiqueta.nombre == etiqueta_data["nombre"]).first()
        if not existente:
            etiqueta = Etiqueta(**etiqueta_data)
            db.add(etiqueta)
            creadas += 1

    db.commit()
    print(f"Etiquetas creadas: {creadas}")


def init_zonas(db: Session):
    """Crear zonas predefinidas según el plano en L"""
    zonas_default = [
        {
            "nombre": "Entrada Principal",
            "codigo": "ENTRADA",
            "descripcion": "Puerta de acceso principal",
            "tipo": "entrada",
            "pos_x": 50,
            "pos_y": 450,
            "ancho": 100,
            "alto": 50,
            "color": "#e74c3c",
            "orden": 1
        },
        {
            "nombre": "Campa - Parcela 15",
            "codigo": "CAMPA_15",
            "descripcion": "Zona de aparcamiento principal",
            "tipo": "campa",
            "pos_x": 50,
            "pos_y": 250,
            "ancho": 200,
            "alto": 200,
            "color": "#3498db",
            "orden": 2
        },
        {
            "nombre": "Campa - Parcela 14",
            "codigo": "CAMPA_14",
            "descripcion": "Zona de aparcamiento superior",
            "tipo": "campa",
            "pos_x": 150,
            "pos_y": 50,
            "ancho": 200,
            "alto": 200,
            "color": "#2ecc71",
            "orden": 3
        },
        {
            "nombre": "Taller Principal",
            "codigo": "TALLER_1",
            "descripcion": "Zona de reparaciones",
            "tipo": "taller",
            "pos_x": 400,
            "pos_y": 150,
            "ancho": 150,
            "alto": 200,
            "color": "#f39c12",
            "orden": 4
        }
    ]

    creadas = 0
    for zona_data in zonas_default:
        existente = db.query(Zona).filter(Zona.codigo == zona_data["codigo"]).first()
        if not existente:
            zona = Zona(**zona_data)
            db.add(zona)
            creadas += 1

    db.commit()
    print(f"Zonas creadas: {creadas}")


def init_camaras(db: Session):
    """Crear cámaras de ejemplo según el plano"""
    # Obtener zonas
    entrada = db.query(Zona).filter(Zona.codigo == "ENTRADA").first()
    campa_15 = db.query(Zona).filter(Zona.codigo == "CAMPA_15").first()
    campa_14 = db.query(Zona).filter(Zona.codigo == "CAMPA_14").first()
    taller = db.query(Zona).filter(Zona.codigo == "TALLER_1").first()

    camaras_default = [
        # Cámaras LPR en entrada
        {
            "nombre": "LPR Entrada 1",
            "codigo": "LPR-1",
            "tipo": "lpr",
            "zona_id": entrada.id if entrada else None,
            "direccion": "entrada",
            "pos_x": 30,
            "pos_y": 460,
            "angulo": 45
        },
        {
            "nombre": "LPR Entrada 2 (Salida)",
            "codigo": "LPR-2",
            "tipo": "lpr",
            "zona_id": entrada.id if entrada else None,
            "direccion": "salida",
            "pos_x": 70,
            "pos_y": 460,
            "angulo": 135
        },
        # Cámaras de vigilancia (Overview)
        {
            "nombre": "Overview Campa 15 - Esquina 1",
            "codigo": "OV-5",
            "tipo": "vigilancia",
            "zona_id": campa_15.id if campa_15 else None,
            "pos_x": 50,
            "pos_y": 400,
            "angulo": 0
        },
        {
            "nombre": "Overview Campa 15 - Esquina 2",
            "codigo": "OV-6",
            "tipo": "vigilancia",
            "zona_id": campa_15.id if campa_15 else None,
            "pos_x": 200,
            "pos_y": 400,
            "angulo": 0
        },
        {
            "nombre": "Overview Intersección",
            "codigo": "OV-2",
            "tipo": "vigilancia",
            "zona_id": campa_15.id if campa_15 else None,
            "pos_x": 150,
            "pos_y": 250,
            "angulo": 0
        },
        {
            "nombre": "Overview Campa 14 - Esquina 1",
            "codigo": "OV-1",
            "tipo": "vigilancia",
            "zona_id": campa_14.id if campa_14 else None,
            "pos_x": 300,
            "pos_y": 150,
            "angulo": 0
        },
        {
            "nombre": "Overview Campa 14 - Esquina 2",
            "codigo": "OV-3",
            "tipo": "vigilancia",
            "zona_id": campa_14.id if campa_14 else None,
            "pos_x": 300,
            "pos_y": 50,
            "angulo": 0
        },
        {
            "nombre": "Overview Campa 14 - Esquina 3",
            "codigo": "OV-4",
            "tipo": "vigilancia",
            "zona_id": campa_14.id if campa_14 else None,
            "pos_x": 150,
            "pos_y": 100,
            "angulo": 0
        }
    ]

    creadas = 0
    for camara_data in camaras_default:
        existente = db.query(Camara).filter(Camara.codigo == camara_data["codigo"]).first()
        if not existente:
            camara = Camara(**camara_data)
            db.add(camara)
            creadas += 1

    db.commit()
    print(f"Cámaras creadas: {creadas}")


def init_campos_personalizados(db: Session):
    """Crear campos personalizados predefinidos"""
    campos_default = [
        {"nombre": "numero_orden", "etiqueta": "Número de Orden", "tipo": "texto", "orden": 1},
        {"nombre": "compania_seguros", "etiqueta": "Compañía de Seguros", "tipo": "texto", "orden": 2},
        {"nombre": "numero_siniestro", "etiqueta": "Número de Siniestro", "tipo": "texto", "orden": 3},
        {"nombre": "perito_asignado", "etiqueta": "Perito Asignado", "tipo": "texto", "orden": 4},
        {"nombre": "fecha_cita_perito", "etiqueta": "Fecha Cita Perito", "tipo": "fecha", "orden": 5},
        {"nombre": "presupuesto", "etiqueta": "Presupuesto (€)", "tipo": "numero", "orden": 6},
        {"nombre": "vehiculo_cortesia", "etiqueta": "Vehículo de Cortesía", "tipo": "booleano", "orden": 7},
        {
            "nombre": "tipo_reparacion",
            "etiqueta": "Tipo de Reparación",
            "tipo": "seleccion",
            "opciones": ["Chapa y pintura", "Mecánica", "Electricidad", "ITV", "Mantenimiento", "Otro"],
            "orden": 8
        },
        {"nombre": "kilometraje", "etiqueta": "Kilometraje", "tipo": "numero", "orden": 9},
        {"nombre": "fecha_estimada_entrega", "etiqueta": "Fecha Estimada de Entrega", "tipo": "fecha", "orden": 10}
    ]

    creados = 0
    for campo_data in campos_default:
        existente = db.query(CampoPersonalizado).filter(CampoPersonalizado.nombre == campo_data["nombre"]).first()
        if not existente:
            campo = CampoPersonalizado(**campo_data)
            db.add(campo)
            creados += 1

    db.commit()
    print(f"Campos personalizados creados: {creados}")


def init_all(db: Session):
    """Ejecutar toda la inicialización"""
    print("=" * 50)
    print("Inicializando base de datos SIGV...")
    print("=" * 50)

    init_admin(db)
    init_etiquetas(db)
    init_zonas(db)
    init_camaras(db)
    init_campos_personalizados(db)

    print("=" * 50)
    print("Inicialización completada!")
    print("=" * 50)
