from google import genai
import os
from dotenv import load_dotenv
import pandas as pd
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# promt que exxtrae los datos
PROMPT_EXTRACTOR = """
Actúa como un experto en contabilidad y visión artificial. 
Analiza la imagen de la factura/ticket adjunta y extrae la información ÚNICAMENTE en el siguiente formato JSON:

{
  "proveedor": "Nombre de la empresa",
  "Tipo de empresa": "tipo de sociedades de empresas",
  "rfc": "RFC",
  "folio": "Número de factura o ticket",
  "fecha": "DD/MM/AAAA",
  "monto_total": 0.00
}

REGLAS ESTRICTAS:
1. Si no encuentras un dato, pon "N/A".
2. El 'monto_total' debe ser un número (float).
3. No escribas nada más que el JSON puro, sin comillas invertidas ni la palabra json.
4. El RFC es de 12 caracteres para persona moral o de 13 caracteres para persona fisica.
"""

def analizar_factura(ruta_imagen):
    print(f"Subiendo y analizando la factura {ruta_imagen}")

    try:
        print("entro al try")
        # subir la imagen a la api
        imagen_s = client.files.upload(file=ruta_imagen)

        respuesta = client.models.generate_content(model="gemini-2.5-flash", contents=[imagen_s, PROMPT_EXTRACTOR])

        return respuesta.text

    except Exception as e:
        print("no entro al try")
        return f"Error procesando la imagen: {e}"




carpeta_archivos = "./data"
i = 0
# leer todos los archivos de mi carpeta
for nombre_archivo in os.listdir(carpeta_archivos):
  if nombre_archivo.endswith(".jpg") or nombre_archivo.endswith(".png"):
    ruta_completa = f"./{carpeta_archivos}/{nombre_archivo}"
    print(analizar_factura(ruta_completa))
    print("-" * 40)


# 1. Creamos una lista vacía. Aquí meteremos cada factura ya procesada.
lista_resultados = []
carpeta_datos = "data"

print("Iniciando procesamiento de facturas...\n")

for nombre_archivo in os.listdir(carpeta_datos):
    if nombre_archivo.endswith(".jpg"):
        ruta_completa = f"./{carpeta_datos}/{nombre_archivo}"

        # Obtenemos el texto crudo de la IA
        resultado_texto = analizar_factura(ruta_completa)

        try:
            # 2. Limpiamos un poco el texto por si la IA nos manda las comillas invertidas de Markdown
            texto_limpio = resultado_texto.replace("```json", "").replace("```", "").strip()

            # 3. Convertimos el texto a un formato estructurado (Diccionario de Python)
            datos_diccionario = json.loads(texto_limpio)

            # 4. Agregamos esta factura a nuestra lista maestra
            lista_resultados.append(datos_diccionario)
            print(f"✅ Factura {nombre_archivo} procesada con éxito.")

        except Exception as e:
            # Si la IA se equivoca y no manda un JSON válido, el programa no se detiene, solo nos avisa.
            print(f"❌ Error al decodificar la respuesta de {nombre_archivo}: {e}")

        print("-" * 40)

# ==========================================
# 5. LA MAGIA: EXPORTAR A EXCEL CON PANDAS
# ==========================================
if len(lista_resultados) > 0:
    print("Generando archivo Excel...")

    # Pandas toma nuestra lista y la convierte en una "Tabla" (DataFrame)
    df = pd.DataFrame(lista_resultados)

    # Exportamos esa tabla a Excel. index=False evita que se cree una columna de números inútil.
    df.to_excel("reporte_facturas.xlsx", index=False)

    print("🎉 ¡PROYECTO TERMINADO! Revisa tu carpeta, el archivo 'reporte_facturas.xlsx' está listo.")
else:
    print("No se logró procesar ninguna factura correctamente.")