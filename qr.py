import qrcode
import cv2
from qrcode.image.pure import PyPNGImage
def qrshow():
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )

    qr.add_data('https://esewa.com.np/#/home')
    qr.make(fit=True)

    qrimg = qr.make_image(fill_color="black", back_color="white")
    qrimg.save("qr.jpg")
    img = cv2.imread("qr.jpg")
    return img