import os
import time
import shutil
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from configdb2 import *

CARPETA_A_VIGILAR = "./IMPORTACION"
CARPETA_PROCESADOS = "./IMPORTACION/PROCESADOS"

class ManejadorExcel(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.xlsx', '.xls')):
            ruta_archivo = event.src_path
            print(f"\n📌 ¡Documento detectado!: {os.path.basename(ruta_archivo)}")

            time.sleep(2)
            self.procesar_pestañas_paises(ruta_archivo)

    def procesar_pestañas_paises(self, ruta_archivo):
        try:
            #Cargar el Excel forzando a texto plano
            excel_completo = pd.read_excel(ruta_archivo, sheet_name=None, dtype=str)

            conexion_MySQLdb = connectionBD()
            mycursor = conexion_MySQLdb.cursor()

            sql = """
                INSERT INTO llamadas (
                    numero, pais, cliente, grupo, fecha_abandono, hora_abandono, 
                    duracion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            total_registros = 0

            #Recorrer el Excel
            for nombre_pais, df_hoja in excel_completo.items():
                pais_limpio = str(nombre_pais).strip()
                print(f"🌍 Absorbiendo registros de la pestaña: [{pais_limpio}]")

                #Insertar las filas de esta hoja
                for _, fila in df_hoja.iterrows():
                    
                    # Función interna que limpia y adapta formatos para MySQL
                    def limpiar_valor(campo):
                        val = fila.get(campo)
                        if val is None or pd.isna(val):
                            return None
                        
                        val_str = str(val).strip()
                        if val_str.lower() in ['nan', '<na>', 'null', '']:
                            return None
                        
                        #Convertir DD/MM/YYYY a YYYY-MM-DD
                        if campo == 'fecha':
                            if '/' in val_str:
                                partes = val_str.split('/')
                                if len(partes) == 3:
                                    # Reorganizamos los elementos: Año-Mes-Día
                                    return f"{partes[2]}-{partes[1]}-{partes[0]}"
                        return val_str

                    valores = (
                        limpiar_valor('numero'),
                        pais_limpio, 
                        limpiar_valor('cliente'),
                        limpiar_valor('agente'),
                        limpiar_valor('fecha'),
                        limpiar_valor('hora'),
                        limpiar_valor('duracion'),
                    )
                    
                    mycursor.execute(sql, valores)
                    total_registros += 1

            conexion_MySQLdb.commit()
            mycursor.close()
            conexion_MySQLdb.close()

            print(f"✅ ¡Todo listo!: Se han importado {total_registros} llamadas correctamente.")

            #Archivar el Excel
            nombre_archivo = os.path.basename(ruta_archivo)
            ruta_destino = os.path.join(CARPETA_PROCESADOS, nombre_archivo)
            shutil.move(ruta_archivo, ruta_destino)
            print(f"📦 El archivo ha sido movido a la carpeta de 'procesados'.")

        except Exception as e:
            if 'mycursor' in locals() and mycursor: mycursor.close()
            if 'conexion_MySQLdb' in locals() and conexion_MySQLdb: conexion_MySQLdb.close()
            print(f"❌ Error al procesar el archivo multihoja: {str(e)}")

if __name__ == "__main__":
    if not os.path.exists(CARPETA_A_VIGILAR): os.makedirs(CARPETA_A_VIGILAR)
    if not os.path.exists(CARPETA_PROCESADOS): os.makedirs(CARPETA_PROCESADOS)

    print(f"👀 Sistema automático activo. Monitoreando la carpeta: '{CARPETA_A_VIGILAR}'")

    event_handler = ManejadorExcel()
    observer = Observer()
    observer.schedule(event_handler, path=CARPETA_A_VIGILAR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()