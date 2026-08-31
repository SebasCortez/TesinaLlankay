#!/usr/bin/env python3
"""
Script de Análisis de Métricas de API para TécniCusco (Railway Logs)
-------------------------------------------------------------------
Procesa los logs estándar generados por APIMetricsMiddleware para calcular:
  1. Volumen total de solicitudes por endpoint y método HTTP.
  2. Tiempos de respuesta (Promedio, Mediana P50, Percentil 95 P95, Mínimo y Máximo en ms).
  3. Códigos de estado y tasas de error (4xx y 5xx).

Uso:
  python analizar_metricas.py railway_logs.txt
  python analizar_metricas.py --csv reporte_semanal.csv railway_logs.txt
  cat logs.txt | python analizar_metricas.py
"""

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime


def extraer_json_metrica(linea: str):
    """
    Extrae el objeto JSON de una línea de log, incluso si Railway
    o Docker anteponen timestamps, headers o identificadores.
    """
    linea = linea.strip()
    if not linea:
        return None

    # Si la línea completa es JSON directo
    if linea.startswith('{') and linea.endswith('}'):
        try:
            data = json.loads(linea)
            if data.get('type') == 'api_metric':
                return data
        except json.JSONDecodeError:
            pass

    # Si el JSON está embebido en una línea con prefijos de Railway
    match = re.search(r'(\{.*"type"\s*:\s*"api_metric".*\})', linea)
    if match:
        try:
            data = json.loads(match.group(1))
            if data.get('type') == 'api_metric':
                return data
        except json.JSONDecodeError:
            pass

    return None


def calcular_percentil(lista_ordenada, percentil):
    """Calcula el percentil p (entre 0 y 100) de una lista ordenada."""
    if not lista_ordenada:
        return 0.0
    k = (len(lista_ordenada) - 1) * (percentil / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return lista_ordenada[int(k)]
    d0 = lista_ordenada[int(f)] * (c - k)
    d1 = lista_ordenada[int(c)] * (k - f)
    return d0 + d1


def procesar_fuentes(lineas_iterador, filtro_path=None):
    """
    Procesa un iterador de líneas y agrupa las métricas por endpoint y método.
    """
    registros_por_endpoint = defaultdict(lambda: {
        'duraciones': [],
        'codigos': defaultdict(int),
        'status_2xx': 0,
        'status_3xx': 0,
        'status_4xx': 0,
        'status_5xx': 0,
        'total': 0,
        'timestamps': []
    })

    total_lineas = 0
    total_metricas = 0
    primer_ts = None
    ultimo_ts = None

    for linea in lineas_iterador:
        total_lineas += 1
        metrica = extraer_json_metrica(linea)
        if not metrica:
            continue

        path = metrica.get('path', 'desconocido')
        method = metrica.get('method', 'GET').upper()
        duration_ms = float(metrica.get('duration_ms', 0.0))
        status_code = int(metrica.get('status_code', 200))
        ts_str = metrica.get('timestamp')

        if filtro_path and filtro_path not in path:
            continue

        total_metricas += 1
        if ts_str:
            if primer_ts is None or ts_str < primer_ts:
                primer_ts = ts_str
            if ultimo_ts is None or ts_str > ultimo_ts:
                ultimo_ts = ts_str

        clave = f"{method} {path}"
        ep = registros_por_endpoint[clave]
        ep['total'] += 1
        ep['duraciones'].append(duration_ms)
        ep['codigos'][status_code] += 1
        if ts_str:
            ep['timestamps'].append(ts_str)

        if 200 <= status_code < 300:
            ep['status_2xx'] += 1
        elif 300 <= status_code < 400:
            ep['status_3xx'] += 1
        elif 400 <= status_code < 500:
            ep['status_4xx'] += 1
        elif status_code >= 500:
            ep['status_5xx'] += 1

    # Calcular estadísticas consolidadas
    resultados = []
    total_duraciones_global = []
    total_2xx_global = 0
    total_3xx_global = 0
    total_4xx_global = 0
    total_5xx_global = 0

    for clave, data in registros_por_endpoint.items():
        duraciones = sorted(data['duraciones'])
        total_duraciones_global.extend(duraciones)
        count = data['total']
        avg_ms = sum(duraciones) / count if count else 0.0
        min_ms = duraciones[0] if count else 0.0
        max_ms = duraciones[-1] if count else 0.0
        p50_ms = calcular_percentil(duraciones, 50)
        p95_ms = calcular_percentil(duraciones, 95)
        p99_ms = calcular_percentil(duraciones, 99)

        total_2xx_global += data['status_2xx']
        total_3xx_global += data['status_3xx']
        total_4xx_global += data['status_4xx']
        total_5xx_global += data['status_5xx']

        tasa_error = ((data['status_4xx'] + data['status_5xx']) / count * 100.0) if count else 0.0
        tasa_5xx = (data['status_5xx'] / count * 100.0) if count else 0.0

        partes = clave.split(' ', 1)
        method = partes[0]
        path = partes[1] if len(partes) > 1 else ''

        resultados.append({
            'endpoint': clave,
            'method': method,
            'path': path,
            'volumen': count,
            'avg_ms': round(avg_ms, 2),
            'p50_ms': round(p50_ms, 2),
            'p95_ms': round(p95_ms, 2),
            'p99_ms': round(p99_ms, 2),
            'min_ms': round(min_ms, 2),
            'max_ms': round(max_ms, 2),
            'c2xx': data['status_2xx'],
            'c3xx': data['status_3xx'],
            'c4xx': data['status_4xx'],
            'c5xx': data['status_5xx'],
            'tasa_error_pct': round(tasa_error, 2),
            'tasa_5xx_pct': round(tasa_5xx, 2),
            'codigos_detalle': dict(data['codigos'])
        })

    # Resumen global
    total_duraciones_global.sort()
    resumen_global = {
        'total_solicitudes': total_metricas,
        'total_lineas_leidas': total_lineas,
        'primer_timestamp': primer_ts,
        'ultimo_timestamp': ultimo_ts,
        'avg_ms_global': round(sum(total_duraciones_global) / total_metricas, 2) if total_metricas else 0.0,
        'p50_ms_global': round(calcular_percentil(total_duraciones_global, 50), 2) if total_metricas else 0.0,
        'p95_ms_global': round(calcular_percentil(total_duraciones_global, 95), 2) if total_metricas else 0.0,
        'total_2xx': total_2xx_global,
        'total_3xx': total_3xx_global,
        'total_4xx': total_4xx_global,
        'total_5xx': total_5xx_global,
        'tasa_error_global_pct': round(((total_4xx_global + total_5xx_global) / total_metricas * 100.0), 2) if total_metricas else 0.0,
    }

    return resultados, resumen_global


def imprimir_reporte_consola(resultados, resumen):
    """
    Imprime un informe en consola con tablas formateadas.
    """
    # Configurar UTF-8 en stdout si es soportado por el entorno
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    print("\n" + "=" * 95)
    print(" [*] INFORME DE RENDIMIENTO Y METRICAS DE API (TECNICUSCO - RAILWAY LOGS)")
    print("=" * 95)

    if resumen['primer_timestamp'] and resumen['ultimo_timestamp']:
        print(f"  Periodo analizado:  {resumen['primer_timestamp']}  -->  {resumen['ultimo_timestamp']}")
    print(f"  Solicitudes totales: {resumen['total_solicitudes']:,}")
    print(f"  Latencia promedio:   {resumen['avg_ms_global']} ms  |  P50: {resumen['p50_ms_global']} ms  |  P95: {resumen['p95_ms_global']} ms")
    print(f"  Tasa global error:   {resumen['tasa_error_global_pct']}%  (2xx: {resumen['total_2xx']:,} | 3xx: {resumen['total_3xx']:,} | 4xx: {resumen['total_4xx']:,} | 5xx: {resumen['total_5xx']:,})")
    print("=" * 95)

    if not resultados:
        print("\n [!] No se encontraron metricas de API en los logs proporcionados.")
        print("     Asegurate de que el middleware APIMetricsMiddleware este activo.\n")
        return

    # Ordenar por volumen descendente
    ordenados = sorted(resultados, key=lambda x: x['volumen'], reverse=True)

    # Tabla principal
    print("\n [>] RESUMEN DETALLADO POR ENDPOINT (Ordenado por volumen de solicitudes):")
    print("-" * 120)
    header = f"{'ENDPOINT':<44} {'SOLICITUDES':>11} {'AVG ms':>9} {'P50 ms':>8} {'P95 ms':>8} {'MAX ms':>8} {'2xx':>6} {'4xx':>6} {'5xx':>6} {'% ERROR':>9}"
    print(header)
    print("-" * 120)

    for r in ordenados:
        ep_name = r['endpoint']
        if len(ep_name) > 42:
            ep_name = ep_name[:39] + "..."
        print(
            f"{ep_name:<44} "
            f"{r['volumen']:>11,} "
            f"{r['avg_ms']:>9.2f} "
            f"{r['p50_ms']:>8.2f} "
            f"{r['p95_ms']:>8.2f} "
            f"{r['max_ms']:>8.2f} "
            f"{r['c2xx']:>6} "
            f"{r['c4xx']:>6} "
            f"{r['c5xx']:>6} "
            f"{r['tasa_error_pct']:>8.2f}%"
        )
    print("-" * 120)

    # Top 5 endpoints más lentos (con al menos 1 solicitud)
    top_lentos = sorted(resultados, key=lambda x: x['p95_ms'], reverse=True)[:5]
    print("\n [!] TOP ENDPOINTS MAS LENTOS (Por P95):")
    for idx, r in enumerate(top_lentos, 1):
        print(f"  {idx}. {r['endpoint']:<40} P95: {r['p95_ms']:>7.2f} ms | Avg: {r['avg_ms']:>7.2f} ms | Max: {r['max_ms']:>7.2f} ms ({r['volumen']} reqs)")

    # Top 5 endpoints con mayor tasa de error
    top_errores = sorted([r for r in resultados if r['tasa_error_pct'] > 0], key=lambda x: x['tasa_error_pct'], reverse=True)[:5]
    if top_errores:
        print("\n [!] TOP ENDPOINTS CON MAYOR TASA DE ERROR:")
        for idx, r in enumerate(top_errores, 1):
            print(f"  {idx}. {r['endpoint']:<40} Error: {r['tasa_error_pct']:>5.1f}% (4xx: {r['c4xx']}, 5xx: {r['c5xx']} de {r['volumen']} reqs)")
    else:
        print("\n [OK] No se registraron errores 4xx ni 5xx en los endpoints analizados.")

    print("\n" + "=" * 95 + "\n")


def exportar_csv(resultados, ruta_csv):
    """Exporta las métricas calculadas a un archivo CSV."""
    campos = [
        'endpoint', 'method', 'path', 'volumen',
        'avg_ms', 'p50_ms', 'p95_ms', 'p99_ms', 'min_ms', 'max_ms',
        'status_2xx', 'status_3xx', 'status_4xx', 'status_5xx',
        'tasa_error_pct', 'tasa_5xx_pct'
    ]

    with open(ruta_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(campos)
        for r in resultados:
            writer.writerow([
                r['endpoint'], r['method'], r['path'], r['volumen'],
                r['avg_ms'], r['p50_ms'], r['p95_ms'], r['p99_ms'], r['min_ms'], r['max_ms'],
                r['c2xx'], r['c3xx'], r['c4xx'], r['c5xx'],
                r['tasa_error_pct'], r['tasa_5xx_pct']
            ])
    print(f"📄 Reporte CSV exportado exitosamente a: {ruta_csv}")


def exportar_json(resultados, resumen, ruta_json):
    """Exporta las métricas y resumen general a un archivo JSON."""
    data = {
        'resumen_general': resumen,
        'endpoints': resultados
    }
    with open(ruta_json, mode='w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"📦 Reporte JSON exportado exitosamente a: {ruta_json}")


def main():
    parser = argparse.ArgumentParser(
        description="Analizador de métricas de API de TécniCusco desde logs de Railway."
    )
    parser.add_argument(
        'archivos',
        nargs='*',
        help="Rutas de los archivos de log a procesar (si se omite, lee de la entrada estándar)."
    )
    parser.add_argument(
        '--csv',
        dest='csv_output',
        help="Ruta donde guardar el reporte en formato CSV."
    )
    parser.add_argument(
        '--json',
        dest='json_output',
        help="Ruta donde guardar el reporte en formato JSON."
    )
    parser.add_argument(
        '--filtro-path',
        dest='filtro_path',
        help="Filtrar únicamente endpoints que contengan este subtexto en su ruta (ej: /api/solicitudes/)."
    )

    args = parser.parse_args()

    # Iterador de líneas según archivos o stdin
    if args.archivos:
        def lineas_generador():
            for archivo_path in args.archivos:
                if not os.path.exists(archivo_path):
                    print(f"⚠️ Archivo no encontrado: {archivo_path}", file=sys.stderr)
                    continue
                with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        yield line
        iterador = lineas_generador()
    else:
        if sys.stdin.isatty():
            print("Esperando entrada de logs por stdin (Ctrl+C para cancelar o pasa un archivo como argumento)...", file=sys.stderr)
        iterador = sys.stdin

    resultados, resumen = procesar_fuentes(iterador, filtro_path=args.filtro_path)

    imprimir_reporte_consola(resultados, resumen)

    if args.csv_output:
        exportar_csv(resultados, args.csv_output)

    if args.json_output:
        exportar_json(resultados, resumen, args.json_output)


if __name__ == '__main__':
    main()
