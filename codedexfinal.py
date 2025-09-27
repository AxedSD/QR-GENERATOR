import qrcode
from pathlib import Path

# FUNCTIONS FOR THE PROGRAM

# Function to generate QRs
def crearqr(texto, nombreqr, carpeta):
    qr = qrcode.QRCode(version=1, box_size=5, border=5)
    qr.add_data(texto)
    qr.make()
    img = qr.make_image(fill_color='black', back_color='white')
    # The "version" parameter is an integer from 1 to 40 that controls the QR code size.
    # The "box_size" parameter controls the number of pixels for each "box" of the QR code.
    # The "border" parameter controls the border thickness in boxes.
    
    # SAVE INTO FOLDER
    guardadocarpeta = Path(carpeta)            # Creates a path to that folder (not created on disk yet)
    guardadocarpeta.mkdir(exist_ok=True)       # Creates the folder if it doesn't exist
    archivo = guardadocarpeta / f"{nombreqr}.png"  # .png so everything is an image; sets the name and saves
    img.save(archivo)
    return archivo


def bienvenida():
    print("")
    print("Welcome to your favorite QR generator!!")


Selecion = 0
bienvenida()
# PROGRAM WITH ITS MENU 
while Selecion != 2:
    print("")
    print("Do you want to generate a QR?")
    print("1) Yes")
    print("2) No, thanks")
    print("")
    
    Selecion = int(input("Enter an option: "))
    
    if Selecion == 1:
        carpeta = input("What would you like to name the output folder? ").strip()
        while True:
            link = input("\nType a LINK (or 0 to finish): ").strip()
            if link == "0":
                break
            if not link:
                print("The link is empty. Try again")
                continue
            nombre = input("Name for this QR? ")
            ruta = crearqr(link, nombre, carpeta)
            print(f"✅ QR saved: {ruta}")
    elif Selecion == 2:
        print("\nDone. Thanks for using the generator! 🎉")
    else:
        print("")
        print("INVALID OPTION. ENTER ANOTHER NUMBER")
        print("")
