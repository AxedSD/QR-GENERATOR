import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

import qrcode
from PIL import Image, ImageTk

# Characters that are not allowed in file names (Windows is the strictest)
CARACTERES_INVALIDOS = '<>:"/\\|?*'
TAMANO_VISTA = 250  # Size in pixels of the QR preview


# Function to generate QRs (same idea as in codedexfinal.py)
def crearqr(texto, nombreqr, carpeta):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(texto)
    qr.make(fit=True)  # fit=True makes the QR bigger if the text doesn't fit in version 1
    img = qr.make_image(fill_color='black', back_color='white')

    # SAVE INTO FOLDER
    guardadocarpeta = Path(carpeta)
    guardadocarpeta.mkdir(parents=True, exist_ok=True)
    archivo = guardadocarpeta / f"{nombreqr}.png"
    img.save(archivo)
    return archivo


class AppQR:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("QR Generator")
        self.ventana.resizable(False, False)
        self.imagen_vista = None  # Keeps a reference so tkinter doesn't delete the image

        marco = tk.Frame(ventana, padx=20, pady=20)
        marco.pack()

        tk.Label(marco, text="Welcome to your favorite QR generator!!",
                 font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # LINK
        tk.Label(marco, text="Link:").grid(row=1, column=0, sticky="w")
        self.entrada_link = tk.Entry(marco, width=40)
        self.entrada_link.grid(row=1, column=1, columnspan=2, pady=4, sticky="we")
        self.entrada_link.focus()

        # QR NAME
        tk.Label(marco, text="QR name:").grid(row=2, column=0, sticky="w")
        self.entrada_nombre = tk.Entry(marco, width=40)
        self.entrada_nombre.grid(row=2, column=1, columnspan=2, pady=4, sticky="we")

        # FOLDER
        tk.Label(marco, text="Folder:").grid(row=3, column=0, sticky="w")
        self.entrada_carpeta = tk.Entry(marco, width=30)
        self.entrada_carpeta.insert(0, str(Path.cwd() / "QRs"))
        self.entrada_carpeta.grid(row=3, column=1, pady=4, sticky="we")
        tk.Button(marco, text="Browse...", command=self.elegir_carpeta).grid(row=3, column=2, padx=(5, 0))

        # GENERATE BUTTON
        tk.Button(marco, text="Generate QR", command=self.generar,
                  bg="#2e7d32", fg="white", font=("Helvetica", 11, "bold"),
                  padx=10, pady=5).grid(row=4, column=0, columnspan=3, pady=15)

        # PREVIEW (starts as an empty white square)
        vacio = Image.new("RGB", (TAMANO_VISTA, TAMANO_VISTA), "white")
        self.imagen_vista = ImageTk.PhotoImage(vacio)
        self.vista = tk.Label(marco, image=self.imagen_vista, relief="solid", borderwidth=1)
        self.vista.grid(row=5, column=0, columnspan=3)

        # STATUS MESSAGE
        self.estado = tk.Label(marco, text="Type a link and press Generate QR",
                               fg="gray", wraplength=350)
        self.estado.grid(row=6, column=0, columnspan=3, pady=(10, 0))

        # Pressing Enter also generates the QR
        ventana.bind("<Return>", lambda evento: self.generar())

    def elegir_carpeta(self):
        carpeta = filedialog.askdirectory(initialdir=self.entrada_carpeta.get() or ".")
        if carpeta:  # Empty if the user cancels
            self.entrada_carpeta.delete(0, tk.END)
            self.entrada_carpeta.insert(0, carpeta)

    def generar(self):
        link = self.entrada_link.get().strip()
        nombre = self.entrada_nombre.get().strip()
        carpeta = self.entrada_carpeta.get().strip()

        # CHECK THE INPUTS BEFORE CREATING THE QR
        if not link:
            messagebox.showwarning("Missing link", "The link is empty. Try again")
            return
        if not nombre:
            messagebox.showwarning("Missing name", "Please type a name for this QR")
            return
        if any(c in CARACTERES_INVALIDOS for c in nombre):
            messagebox.showwarning("Invalid name",
                                   f"The name can't contain any of these characters: {CARACTERES_INVALIDOS}")
            return
        if not carpeta:
            messagebox.showwarning("Missing folder", "Please choose a folder to save the QR")
            return

        archivo = Path(carpeta) / f"{nombre}.png"
        if archivo.exists():
            if not messagebox.askyesno("File exists", f"{archivo.name} already exists. Replace it?"):
                return

        try:
            ruta = crearqr(link, nombre, carpeta)
        except OSError as error:
            messagebox.showerror("Error", f"Couldn't save the QR:\n{error}")
            return

        # SHOW THE NEW QR IN THE WINDOW
        img = Image.open(ruta).resize((TAMANO_VISTA, TAMANO_VISTA), Image.NEAREST)
        self.imagen_vista = ImageTk.PhotoImage(img)
        self.vista.config(image=self.imagen_vista)
        self.estado.config(text=f"✅ QR saved: {ruta}", fg="#2e7d32")

        # Clear the fields to make the next QR
        self.entrada_link.delete(0, tk.END)
        self.entrada_nombre.delete(0, tk.END)
        self.entrada_link.focus()


if __name__ == "__main__":
    ventana = tk.Tk()
    AppQR(ventana)
    ventana.mainloop()
