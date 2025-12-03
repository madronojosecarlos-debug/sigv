"""
Simulador de Cámaras LPR
Permite probar el sistema sin tener las cámaras físicas instaladas.
Simula detecciones de matrículas y las envía al backend.
"""
import requests
import random
import time
import argparse
from datetime import datetime

# Configuración
API_URL = "http://localhost:8000/api/movimientos/lpr/detectar"

# Cámaras disponibles
CAMARAS = ["LPR-1", "LPR-2"]

# Matrículas de ejemplo para simular
MATRICULAS_EJEMPLO = [
    "1234ABC", "5678DEF", "9012GHI", "3456JKL", "7890MNO",
    "2345PQR", "6789STU", "0123VWX", "4567YZA", "8901BCD",
    "1122EFG", "3344HIJ", "5566KLM", "7788NOP", "9900QRS"
]


def simular_deteccion(matricula: str, camara: str, confianza: float = None):
    """Envía una detección simulada al backend"""
    if confianza is None:
        confianza = random.uniform(85, 99)

    payload = {
        "matricula": matricula,
        "camara_codigo": camara,
        "confianza": round(confianza, 2)
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            resultado = response.json()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] OK - {matricula} detectada por {camara}")
            print(f"    Acción: {resultado['resultado']['accion']}")
            if resultado['resultado'].get('vehiculo_nuevo'):
                print(f"    (Vehículo nuevo creado)")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR - {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR - No se puede conectar al servidor")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR - {e}")


def modo_interactivo():
    """Modo interactivo para enviar detecciones manualmente"""
    print("\n" + "=" * 50)
    print("SIMULADOR LPR - Modo Interactivo")
    print("=" * 50)
    print("\nComandos:")
    print("  <matricula>     - Detectar matrícula en LPR-1 (entrada)")
    print("  <matricula> 2   - Detectar matrícula en LPR-2 (salida)")
    print("  random          - Generar detección aleatoria")
    print("  lista           - Ver matrículas de ejemplo")
    print("  salir           - Terminar simulador")
    print()

    while True:
        try:
            entrada = input("Matrícula > ").strip().upper()

            if not entrada:
                continue

            if entrada == "SALIR":
                print("Hasta luego!")
                break

            if entrada == "LISTA":
                print("\nMatrículas de ejemplo:")
                for m in MATRICULAS_EJEMPLO:
                    print(f"  {m}")
                print()
                continue

            if entrada == "RANDOM":
                matricula = random.choice(MATRICULAS_EJEMPLO)
                camara = random.choice(CAMARAS)
                print(f"Simulando: {matricula} en {camara}")
                simular_deteccion(matricula, camara)
                continue

            # Procesar entrada: "1234ABC" o "1234ABC 2"
            partes = entrada.split()
            matricula = partes[0]
            camara = "LPR-2" if len(partes) > 1 and partes[1] == "2" else "LPR-1"

            simular_deteccion(matricula, camara)

        except KeyboardInterrupt:
            print("\nHasta luego!")
            break


def modo_automatico(intervalo: int = 30, cantidad: int = 10):
    """Modo automático: genera detecciones aleatorias periódicamente"""
    print("\n" + "=" * 50)
    print("SIMULADOR LPR - Modo Automático")
    print(f"Intervalo: {intervalo} segundos")
    print(f"Detecciones a generar: {cantidad}")
    print("=" * 50)
    print("\nPresiona Ctrl+C para detener\n")

    try:
        for i in range(cantidad):
            matricula = random.choice(MATRICULAS_EJEMPLO)
            camara = random.choice(CAMARAS)
            print(f"\n[Detección {i + 1}/{cantidad}]")
            simular_deteccion(matricula, camara)

            if i < cantidad - 1:
                time.sleep(intervalo)

        print("\n" + "=" * 50)
        print("Simulación completada!")

    except KeyboardInterrupt:
        print("\n\nSimulación detenida por el usuario")


def modo_escenario():
    """Simula un escenario típico de un día"""
    print("\n" + "=" * 50)
    print("SIMULADOR LPR - Escenario de Día Típico")
    print("=" * 50)

    escenario = [
        ("1234ABC", "LPR-1", "Entrada cliente 1"),
        ("5678DEF", "LPR-1", "Entrada cliente 2"),
        ("9012GHI", "LPR-1", "Entrada cliente 3"),
        ("1234ABC", "LPR-2", "Salida cliente 1 (recogida rápida)"),
        ("3456JKL", "LPR-1", "Entrada cliente 4"),
        ("5678DEF", "LPR-2", "Salida cliente 2"),
        ("7890MNO", "LPR-1", "Entrada cliente 5"),
    ]

    print(f"\nEjecutando {len(escenario)} eventos...\n")

    for matricula, camara, descripcion in escenario:
        print(f"\n--- {descripcion} ---")
        simular_deteccion(matricula, camara)
        time.sleep(2)

    print("\n" + "=" * 50)
    print("Escenario completado!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de Cámaras LPR para SIGV")
    parser.add_argument("--modo", choices=["interactivo", "auto", "escenario"],
                        default="interactivo", help="Modo de simulación")
    parser.add_argument("--intervalo", type=int, default=30,
                        help="Intervalo entre detecciones en modo auto (segundos)")
    parser.add_argument("--cantidad", type=int, default=10,
                        help="Número de detecciones en modo auto")

    args = parser.parse_args()

    print("\n" + "=" * 50)
    print("SIGV - Simulador de Cámaras LPR")
    print("Centro de Automóvil Pedro Madroño")
    print("=" * 50)

    if args.modo == "interactivo":
        modo_interactivo()
    elif args.modo == "auto":
        modo_automatico(args.intervalo, args.cantidad)
    elif args.modo == "escenario":
        modo_escenario()
