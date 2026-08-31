from django.core.management.base import BaseCommand
import sys
import os
from analizar_metricas import procesar_fuentes, imprimir_reporte_consola, exportar_csv, exportar_json


class Command(BaseCommand):
    help = 'Analiza métricas de API (volumen, tiempo de respuesta y errores) desde archivos de logs de Railway'

    def add_arguments(self, parser):
        parser.add_argument(
            'archivos',
            nargs='*',
            type=str,
            help='Archivos de log a analizar (ej. railway_logs.txt)'
        )
        parser.add_argument(
            '--csv',
            dest='csv_output',
            type=str,
            help='Ruta para exportar el reporte en CSV'
        )
        parser.add_argument(
            '--json',
            dest='json_output',
            type=str,
            help='Ruta para exportar el reporte en JSON'
        )
        parser.add_argument(
            '--filtro-path',
            dest='filtro_path',
            type=str,
            help='Filtrar únicamente endpoints que contengan este subtexto'
        )

    def handle(self, *args, **options):
        archivos = options['archivos']
        csv_output = options.get('csv_output')
        json_output = options.get('json_output')
        filtro_path = options.get('filtro_path')

        if archivos:
            def lineas_generador():
                for archivo_path in archivos:
                    if not os.path.exists(archivo_path):
                        self.stderr.write(self.style.WARNING(f"⚠️ Archivo no encontrado: {archivo_path}"))
                        continue
                    with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            yield line
            iterador = lineas_generador()
        else:
            if sys.stdin.isatty():
                self.stdout.write("Esperando entrada de logs por stdin (Ctrl+C para cancelar)...")
            iterador = sys.stdin

        resultados, resumen = procesar_fuentes(iterador, filtro_path=filtro_path)

        imprimir_reporte_consola(resultados, resumen)

        if csv_output:
            exportar_csv(resultados, csv_output)
            self.stdout.write(self.style.SUCCESS(f"✅ Reporte CSV guardado en {csv_output}"))

        if json_output:
            exportar_json(resultados, resumen, json_output)
            self.stdout.write(self.style.SUCCESS(f"✅ Reporte JSON guardado en {json_output}"))
