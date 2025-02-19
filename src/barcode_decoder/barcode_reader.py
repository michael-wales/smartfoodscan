from pyzbar.pyzbar import decode
import cv2
import numpy as np

def barcode_reader(image):
    image = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    # Decode the barcode
    decoded = decode(image)
    # Print the barcode data and type
    for barcode in decoded:
        return int(barcode.data.decode("utf-8"))
