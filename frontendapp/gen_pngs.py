import os
import base64

# Valid 1x1 PNG image
png_b64 = "iVBORw0KGgoAAAANSU5EUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
raw_png = base64.b64decode(png_b64)

assets_dir = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(assets_dir, exist_ok=True)

for filename in ["icon.png", "splash.png", "adaptive-icon.png", "favicon.png"]:
    file_path = os.path.join(assets_dir, filename)
    with open(file_path, "wb") as f:
        f.write(raw_png)

print("Generated assets successfully in", assets_dir)
