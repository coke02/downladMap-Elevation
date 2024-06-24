import os
import leafmap
import shutil
import sys

# Verificar si el paquete rio-cogeo está instalado, si no, instalarlo
try:
    from rio_cogeo.cogeo import cog_translate
except ImportError:
    os.system('pip install rio-cogeo')

# Crear un mapa centrado en las coordenadas especificadas
m = leafmap.Map(center=[40, -100], zoom=4)
m
# Obtener los límites de la región seleccionada por el usuario
region = m.user_roi_bounds()
if region is None:
    # Si no se selecciona ninguna región, usar una región por defecto
    region = [-115.9689, 35.9758, -115.3619, 36.4721]

print(f"Región seleccionada: {region}")

# Descargar los datos de elevación para la región seleccionada
ned_url = leafmap.download_ned(region, return_url=True)
print(f"URL del NED descargado: {ned_url}")

# Definir el directorio de salida para guardar los archivos
out_dir = "data"
os.makedirs(out_dir, exist_ok=True)

# Descargar los datos y guardarlos en el directorio de salida
leafmap.download_ned(region, out_dir)

# Crear un mosaico de los archivos descargados
mosaic = "mosaic.tif"
try:
    leafmap.mosaic(images=out_dir, output=mosaic)
    print(f"Mosaico creado: {mosaic}")
except ImportError:
    print("No se pudo convertir a COG. Asegúrate de que el paquete rio-cogeo esté instalado.")
except Exception as e:
    print(f"Error al crear el mosaico: {e}")

# Si el usuario ha seleccionado una región de interés (ROI), recortar la imagen
if m.user_roi is not None:
    image = "dem.tif"
    try:
        leafmap.clip_image(mosaic, mask=m.user_roi, output=image)
        print(f"Imagen recortada: {image}")

        # Copiar la imagen recortada al directorio de salida final
        final_out_dir = "/Data"
        os.makedirs(final_out_dir, exist_ok=True)
        shutil.copyfile(image, os.path.join(final_out_dir, image))
        print(f"Imagen copiada a: {os.path.join(final_out_dir, image)}")
    except Exception as e:
        print(f"Error al recortar la imagen: {e}")
else:
    print("No se seleccionó ninguna región de interés para recortar.")

# Confirmación final
print("Proceso completado.")