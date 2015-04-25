import pyqrcode
import qrtools
def generate_qr_code(filename, text):
    filename = "database_images/qr_code/bill1.png"
    text = 'restaurant_name:name\nbill_id:id\nitem1:name; quantity:number; price:number\nitem2:name; quantity:number; price:number\ntotal:number\ntime: currentTime'
    qr = pyqrcode.create(text)
    qr.png(filename, scale=6)
    
qr = pyqrcode.create("HORN O.K. PLEASE.")
qr.png("horn.png", scale=6)
qr = qrtools.QR()
qr.decode("horn.png")
print qr.data