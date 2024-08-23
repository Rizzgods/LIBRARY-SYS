# image_test.py

from PIL import Image

try:
    img = Image.open("media/book_images/samplebook.jpg")
    img.show()  # This should display the image
except Exception as e:
    print("Error:", e)