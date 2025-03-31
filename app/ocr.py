import pathlib
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

BASE_DIR = pathlib.Path(__file__).parent
IMAGE_DIR = BASE_DIR / "images"
img_path = IMAGE_DIR / "ingredients-1.png"

img = Image.open(img_path)

predictions = pytesseract.image_to_string(img)
predictions_list = [x for x in predictions.split("\n")]
print(predictions_list)