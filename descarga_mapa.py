#install "pip install mercantile requests Pillow rasterio"
import mercantile
import requests
from PIL import Image
from io import BytesIO
import rasterio
from rasterio.transform import from_bounds

def download_tile(tile, zoom, tile_server, retries=3):
    url = f"{tile_server}/{zoom}/{tile.x}/{tile.y}.png"
    for attempt in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            else:
                print(f"Failed to download tile {tile} at zoom {zoom} (status code: {response.status_code})")
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
    raise Exception(f"Failed to download tile {tile} at zoom {zoom} from {url} after {retries} attempts")

def stitch_tiles(tiles, zoom, tile_server, out_path):
    images = [download_tile(tile, zoom, tile_server) for tile in tiles]

    tile_width, tile_height = images[0].size
    num_tiles_x = max(tile.x for tile in tiles) - min(tile.x for tile in tiles) + 1
    num_tiles_y = max(tile.y for tile in tiles) - min(tile.y for tile in tiles) + 1

    map_image = Image.new('RGB', (num_tiles_x * tile_width, num_tiles_y * tile_height))

    for tile, img in zip(tiles, images):
        x_offset = (tile.x - min(tile.x for tile in tiles)) * tile_width
        y_offset = (tile.y - min(tile.y for tile in tiles)) * tile_height
        map_image.paste(img, (x_offset, y_offset))

    map_image.save(out_path)

    with rasterio.open(out_path, 'r+') as dst:
        transform = from_bounds(*mercantile.xy_bounds(tiles[0]), map_image.width, map_image.height)
        dst.transform = transform
        dst.crs = 'EPSG:3857'

def main(lat, lon, zoom, tile_server, out_path):
    tile = mercantile.tile(lon, lat, zoom)
    tiles = [mercantile.Tile(tile.x + dx, tile.y + dy, tile.z) for dx in range(-1, 2) for dy in range(-1, 2)]
    stitch_tiles(tiles, zoom, tile_server, out_path)

if __name__ == "__main__":
    lat = -33.4489  # Latitud de Santiago, Chile
    lon = -70.6693  # Longitud de Santiago, Chile
    zoom = 12  # Nivel de zoom deseado
    tile_server = "https://tile.openstreetmap.org"
    out_path = "santiago_map.tif"

    try:
        main(lat, lon, zoom, tile_server, out_path)
        print(f"Mapa descargado y guardado en {out_path}")
    except Exception as e:
        print(f"Error: {e}")