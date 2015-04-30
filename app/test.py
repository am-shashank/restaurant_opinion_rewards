import pyqrcode
# import qrtools
def generate_qr_code(filename, text):
    filename = "database_images/qr_code/Sitar_India_Bill1.png"
    text = 'restaurant_name:Sitar India\nbill_id:1\nitem1:name1; quantity:2; price:100\nitem2:name2; quantity:3; price:100\ntotal:200\ntime: 1'
    qr = pyqrcode.create(text)
    qr.png(filename, scale=6)
    
'''qr = pyqrcode.create("HORN O.K. PLEASE.")
qr.png("horn.png", scale=6)
qr = qrtools.QR()
qr.decode("horn.png")
print qr.data'''
generate_qr_code('','')
