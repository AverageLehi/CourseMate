from PIL import Image
import sys

# Usage: python tilt_icon.py input.png output.png
if len(sys.argv) != 3:
    print("Usage: python tilt_icon.py input.png output.png")
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]

img = Image.open(input_path)
rotated = img.rotate(90, expand=True)
rotated.save(output_path)
print(f"Saved rotated icon to {output_path}")
