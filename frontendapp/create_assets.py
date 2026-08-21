import os
import zlib
import struct

def create_png(width, height, color_rgb=(128, 82, 255)):
    r, g, b = color_rgb
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter type 0
        for x in range(width):
            raw_data.extend([r, g, b, 255])
    
    compressed_data = zlib.compress(raw_data)
    png_bytes = bytearray(b'\x89PNG\r\n\x1a\n')
    
    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    png_bytes.extend(struct.pack('>I', len(ihdr_data)))
    png_bytes.extend(b'IHDR')
    png_bytes.extend(ihdr_data)
    png_bytes.extend(struct.pack('>I', ihdr_crc))
    
    # IDAT chunk
    idat_crc = zlib.crc32(b'IDAT' + compressed_data)
    png_bytes.extend(struct.pack('>I', len(compressed_data)))
    png_bytes.extend(b'IDAT')
    png_bytes.extend(compressed_data)
    png_bytes.extend(struct.pack('>I', idat_crc))
    
    # IEND chunk
    iend_crc = zlib.crc32(b'IEND')
    png_bytes.extend(struct.pack('>I', 0))
    png_bytes.extend(b'IEND')
    png_bytes.extend(struct.pack('>I', iend_crc))
    
    return bytes(png_bytes)

assets_dir = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(assets_dir, exist_ok=True)

with open(os.path.join(assets_dir, "icon.png"), "wb") as f:
    f.write(create_png(512, 512, (128, 82, 255)))

with open(os.path.join(assets_dir, "splash.png"), "wb") as f:
    f.write(create_png(512, 512, (0, 0, 0)))

with open(os.path.join(assets_dir, "adaptive-icon.png"), "wb") as f:
    f.write(create_png(512, 512, (128, 82, 255)))

with open(os.path.join(assets_dir, "favicon.png"), "wb") as f:
    f.write(create_png(48, 48, (128, 82, 255)))

print("Assets created successfully!")
