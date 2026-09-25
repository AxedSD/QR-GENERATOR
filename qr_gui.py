import os
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import qrcode
from PIL import Image, ImageDraw, ImageOps
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    CircleModuleDrawer, RoundedModuleDrawer, SquareModuleDrawer)

# COLORS OF THE APP: ("color in light mode", "color in dark mode")
FONDO = ("#EEF0F8", "#0F1117")
TARJETA = ("#FFFFFF", "#1A1D29")
BORDE = ("#E2E5F0", "#2A2E3F")
CAMPO = ("#F6F7FB", "#12141D")
TEXTO = ("#1B1E2B", "#EDEFF7")
TEXTO_SUAVE = ("#6B7087", "#8C92AB")
ACENTO = "#6C5CE7"
ACENTO_HOVER = "#5847D9"
EXITO = ("#12A150", "#3DD68C")
ERROR = ("#E5484D", "#FF6369")

# Colors for the QR. They are all dark so phones can still read the QR on white
COLORES_QR = ["#111827", "#4F46E5", "#7C3AED", "#0369A1", "#15803D", "#BE123C"]

# Styles for the QR: (shape of the small squares, shape of the 3 big corner squares)
ESTILOS_QR = {
    "Square": (SquareModuleDrawer, SquareModuleDrawer),
    "Rounded": (RoundedModuleDrawer, RoundedModuleDrawer),
    "Dots": (CircleModuleDrawer, RoundedModuleDrawer),
}

CARACTERES_INVALIDOS = '<>:"/\\|?*'  # Characters that are not allowed in file names
TAMANO_VISTA = 260  # Size in pixels of the QR preview


# Function that draws a QR and returns the image (without saving it)
def hacer_qr(texto, color, estilo):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(texto)
    qr.make(fit=True)  # fit=True picks the smallest QR size where the text fits
    forma_modulos, forma_esquinas = ESTILOS_QR[estilo]
    img = qr.make_image(image_factory=StyledPilImage,
                        module_drawer=forma_modulos(), eye_drawer=forma_esquinas())
    # The QR comes in black and white: colorize() paints the black parts with our color
    return ImageOps.colorize(img.convert("L"), black=color, white="white")


# Draws a round color sample for the color buttons. The chosen one gets a ring around it
def dibujar_muestra(color, elegido):
    imagenes = []
    # One version for light mode and one for dark mode: (ring color, outline of the circle)
    for anillo, contorno in [(TEXTO[0], color), (TEXTO[1], "#3B4056")]:
        img = Image.new("RGBA", (184, 184))  # Drawn 4 times bigger so the edges look smooth when shrunk
        lapiz = ImageDraw.Draw(img)
        lapiz.ellipse((24, 24, 160, 160), fill=color, outline=contorno, width=4)
        if elegido:
            lapiz.ellipse((2, 2, 182, 182), outline=anillo, width=8)
        imagenes.append(img)
    return ctk.CTkImage(light_image=imagenes[0], dark_image=imagenes[1], size=(46, 46))


# Function to generate QRs and save them into a folder
def crearqr(texto, nombreqr, carpeta, color="#000000", estilo="Square"):
    img = hacer_qr(texto, color, estilo)
    guardadocarpeta = Path(carpeta)
    guardadocarpeta.mkdir(parents=True, exist_ok=True)  # Creates the folder if it doesn't exist
    archivo = guardadocarpeta / f"{nombreqr}.png"
    img.save(archivo)
    return archivo


# Opens a folder in the file explorer (each operating system does it differently)
def abrir_carpeta(carpeta):
    if sys.platform == "win32":
        os.startfile(carpeta)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", carpeta])
    else:
        subprocess.Popen(["xdg-open", carpeta])


class AppQR(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=FONDO)
        self.title("QR Studio")
        self.geometry("880x620")
        self.minsize(880, 620)

        self.color = COLORES_QR[1]
        self.estilo = "Rounded"
        self.carpeta_guardada = None
        self.espera = None  # Timer used to update the preview while you type

        self.fuente_titulo = ctk.CTkFont(size=26, weight="bold")
        self.fuente_etiqueta = ctk.CTkFont(size=11, weight="bold")
        self.fuente_normal = ctk.CTkFont(size=14)
        self.fuente_boton = ctk.CTkFont(size=16, weight="bold")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.crear_encabezado()
        self.crear_formulario()
        self.crear_vista_previa()
        self.marcar_seleccion()
        self.actualizar_vista()

        # Pressing Enter also saves the QR
        self.bind("<Return>", lambda evento: self.guardar())

    # ---------- PIECES OF THE WINDOW ----------

    def crear_encabezado(self):
        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew", padx=32, pady=(28, 20))
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(encabezado, text="QR", width=48, height=48, corner_radius=14,
                     fg_color=ACENTO, text_color="white",
                     font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, rowspan=2, padx=(0, 14))
        ctk.CTkLabel(encabezado, text="QR Studio", height=30, font=self.fuente_titulo,
                     text_color=TEXTO).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(encabezado, text="Your favorite QR generator, now with style ✨", height=20,
                     text_color=TEXTO_SUAVE, font=self.fuente_normal).grid(row=1, column=1, sticky="nw")

        self.interruptor_tema = ctk.CTkSwitch(encabezado, text="Dark mode", command=self.cambiar_tema,
                                              progress_color=ACENTO, text_color=TEXTO, font=self.fuente_normal)
        self.interruptor_tema.grid(row=0, column=2, rowspan=2)
        if ctk.get_appearance_mode() == "Dark":
            self.interruptor_tema.select()

    def crear_formulario(self):
        tarjeta = self.crear_tarjeta(columna=0, espacio=(32, 12))

        self.crear_etiqueta(tarjeta, "LINK", fila=0)
        self.entrada_link = self.crear_campo(tarjeta, "https://your-link.com")
        self.entrada_link.grid(row=1, column=0, sticky="ew", padx=28)
        self.entrada_link.bind("<KeyRelease>", self.programar_vista)

        self.crear_etiqueta(tarjeta, "FILE NAME", fila=2)
        fila = self.crear_fila(tarjeta, fila=3)
        self.entrada_nombre = self.crear_campo(fila, "my-qr")
        self.entrada_nombre.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(fila, text=".png", text_color=TEXTO_SUAVE,
                     font=self.fuente_normal).grid(row=0, column=1, padx=(10, 4))

        self.crear_etiqueta(tarjeta, "SAVE IN", fila=4)
        fila = self.crear_fila(tarjeta, fila=5)
        self.entrada_carpeta = self.crear_campo(fila, "Choose a folder")
        self.entrada_carpeta.insert(0, str(Path.cwd() / "QRs"))
        self.after_idle(lambda: self.entrada_carpeta.xview("end"))
        self.entrada_carpeta.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(fila, text="Browse", width=90, height=42, corner_radius=12,
                      fg_color="transparent", hover_color=CAMPO, border_width=1, border_color=BORDE,
                      text_color=TEXTO, font=self.fuente_normal,
                      command=self.elegir_carpeta).grid(row=0, column=1, padx=(8, 0))

        # COLOR: one clickable circle for each color
        self.crear_etiqueta(tarjeta, "COLOR", fila=6)
        fila = self.crear_fila(tarjeta, fila=7, estirar=False)
        self.muestras_color = {}
        for i, color in enumerate(COLORES_QR):
            muestra = ctk.CTkLabel(fila, text="", width=46, cursor="hand2")
            muestra.grid(row=0, column=i, padx=(0, 6))
            # c=color saves the color of THIS circle, so each one remembers its own color
            muestra.bind("<Button-1>", lambda evento, c=color: self.elegir_color(c))
            self.muestras_color[color] = muestra

        # STYLE: one button for each shape
        self.crear_etiqueta(tarjeta, "STYLE", fila=8)
        fila = self.crear_fila(tarjeta, fila=9, estirar=False)
        self.botones_estilo = {}
        for i, estilo in enumerate(ESTILOS_QR):
            boton = ctk.CTkButton(fila, text=estilo, width=96, height=38, corner_radius=12,
                                  border_width=1, font=self.fuente_normal,
                                  command=lambda e=estilo: self.elegir_estilo(e))
            boton.grid(row=0, column=i, padx=(0, 8))
            self.botones_estilo[estilo] = boton

        tarjeta.grid_rowconfigure(10, weight=1)  # Pushes the tip to the bottom of the card
        ctk.CTkLabel(tarjeta, text="Tip: press Enter to save your QR", text_color=TEXTO_SUAVE,
                     font=ctk.CTkFont(size=13)).grid(row=10, column=0, sticky="sw", padx=30, pady=(0, 18))

    def crear_vista_previa(self):
        tarjeta = self.crear_tarjeta(columna=1, espacio=(12, 32))
        tarjeta.grid_rowconfigure(1, weight=1)

        self.crear_etiqueta(tarjeta, "PREVIEW", fila=0)

        # The QR sits on a white "paper" that stays white even in dark mode
        papel = ctk.CTkFrame(tarjeta, fg_color="white", corner_radius=18,
                             border_width=1, border_color=BORDE)
        papel.grid(row=1, column=0, padx=28)
        self.vista = ctk.CTkLabel(papel, text="")
        self.vista.pack(padx=8, pady=8)

        self.leyenda = ctk.CTkLabel(tarjeta, text="", text_color=TEXTO_SUAVE, font=self.fuente_normal)
        self.leyenda.grid(row=2, column=0, padx=28, pady=(10, 0))

        ctk.CTkButton(tarjeta, text="Save QR", height=48, corner_radius=14,
                      fg_color=ACENTO, hover_color=ACENTO_HOVER, font=self.fuente_boton,
                      command=self.guardar).grid(row=3, column=0, sticky="ew", padx=28, pady=(16, 8))

        fila = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila.grid(row=4, column=0, padx=28, pady=(0, 18))
        self.estado = ctk.CTkLabel(fila, text="", font=self.fuente_normal)
        self.estado.grid(row=0, column=0)
        # This button only appears after saving a QR
        self.boton_abrir = ctk.CTkButton(fila, text="Open folder", width=0, height=26,
                                         fg_color="transparent", hover_color=CAMPO, text_color=ACENTO,
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         command=lambda: abrir_carpeta(self.carpeta_guardada))

    # ---------- SMALL HELPERS TO AVOID REPEATING CODE ----------

    def crear_tarjeta(self, columna, espacio):
        tarjeta = ctk.CTkFrame(self, fg_color=TARJETA, corner_radius=20,
                               border_width=1, border_color=BORDE)
        tarjeta.grid(row=1, column=columna, sticky="nsew", padx=espacio, pady=(0, 32))
        tarjeta.grid_columnconfigure(0, weight=1)
        return tarjeta

    def crear_etiqueta(self, padre, texto, fila):
        ctk.CTkLabel(padre, text=texto, height=16, font=self.fuente_etiqueta,
                     text_color=TEXTO_SUAVE).grid(row=fila, column=0, sticky="w",
                                                  padx=30, pady=(22 if fila == 0 else 16, 8))

    def crear_fila(self, padre, fila, estirar=True):
        marco = ctk.CTkFrame(padre, fg_color="transparent")
        marco.grid(row=fila, column=0, sticky="ew", padx=28)
        if estirar:  # The first thing in the row (a text field) takes all the free space
            marco.grid_columnconfigure(0, weight=1)
        return marco

    def crear_campo(self, padre, texto_guia):
        campo = ctk.CTkEntry(padre, height=42, corner_radius=12, border_width=1,
                             fg_color=CAMPO, border_color=BORDE, text_color=TEXTO,
                             placeholder_text=texto_guia, placeholder_text_color=TEXTO_SUAVE,
                             font=self.fuente_normal)
        # The border turns purple while you are typing in the field
        campo.bind("<FocusIn>", lambda evento: campo.configure(border_color=ACENTO))
        campo.bind("<FocusOut>", lambda evento: campo.configure(border_color=BORDE))
        campo.bind("<Key>", lambda evento: campo.configure(border_color=ACENTO))
        return campo

    # ---------- WHAT HAPPENS WHEN YOU CLICK THINGS ----------

    def programar_vista(self, evento=None):
        # Waits a moment after the last key, so we don't redraw the QR on every single letter
        if self.espera:
            self.after_cancel(self.espera)
        self.espera = self.after(150, self.actualizar_vista)

    def actualizar_vista(self):
        self.espera = None
        link = self.entrada_link.get().strip()
        if link:
            img = hacer_qr(link, self.color, self.estilo)
            self.leyenda.configure(text=link if len(link) <= 38 else link[:35] + "...")
        else:
            img = hacer_qr("QR Studio", "#E4E7F0", self.estilo)  # A faded QR while the link is empty
            self.leyenda.configure(text="Type a link to see your QR come to life")
        # We keep the image in self so Python doesn't delete it
        self.imagen_vista = ctk.CTkImage(light_image=img, size=(TAMANO_VISTA, TAMANO_VISTA))
        self.vista.configure(image=self.imagen_vista)

    def marcar_seleccion(self):
        # Lights up the ring of the chosen color and paints the chosen style purple
        for color, muestra in self.muestras_color.items():
            muestra.configure(image=dibujar_muestra(color, color == self.color))
        for estilo, boton in self.botones_estilo.items():
            if estilo == self.estilo:
                boton.configure(fg_color=ACENTO, hover_color=ACENTO_HOVER,
                                border_color=ACENTO, text_color="white")
            else:
                boton.configure(fg_color=CAMPO, hover_color=BORDE,
                                border_color=BORDE, text_color=TEXTO)

    def elegir_color(self, color):
        self.color = color
        self.marcar_seleccion()
        self.actualizar_vista()

    def elegir_estilo(self, estilo):
        self.estilo = estilo
        self.marcar_seleccion()
        self.actualizar_vista()

    def elegir_carpeta(self):
        carpeta = filedialog.askdirectory(initialdir=self.entrada_carpeta.get() or ".")
        if carpeta:  # Empty if the user cancels
            self.entrada_carpeta.delete(0, "end")
            self.entrada_carpeta.insert(0, carpeta)
            self.entrada_carpeta.xview("end")

    def cambiar_tema(self):
        ctk.set_appearance_mode("dark" if self.interruptor_tema.get() else "light")

    def mostrar_error(self, mensaje, campo=None):
        self.estado.configure(text=mensaje, text_color=ERROR)
        self.boton_abrir.grid_remove()
        if campo:
            campo.configure(border_color=ERROR)

    def guardar(self):
        link = self.entrada_link.get().strip()
        nombre = self.entrada_nombre.get().strip()
        carpeta = self.entrada_carpeta.get().strip()
        for campo in (self.entrada_link, self.entrada_nombre, self.entrada_carpeta):
            campo.configure(border_color=BORDE)  # Clears the red border of old errors

        # CHECK THE INPUTS BEFORE SAVING
        if not link:
            self.mostrar_error("Type a link first", self.entrada_link)
            return
        if not nombre:
            self.mostrar_error("Give your QR a name", self.entrada_nombre)
            return
        if any(c in CARACTERES_INVALIDOS for c in nombre):
            self.mostrar_error(f"The name can't contain {CARACTERES_INVALIDOS}", self.entrada_nombre)
            return
        if not carpeta:
            self.mostrar_error("Choose a folder to save it", self.entrada_carpeta)
            return

        archivo = Path(carpeta) / f"{nombre}.png"
        if archivo.exists():
            if not messagebox.askyesno("File exists", f"{archivo.name} already exists. Replace it?"):
                return

        try:
            ruta = crearqr(link, nombre, carpeta, self.color, self.estilo)
        except OSError as error:
            self.mostrar_error(f"Couldn't save it: {error.strerror}")
            return

        self.carpeta_guardada = ruta.parent
        self.estado.configure(text=f"✓ Saved as {ruta.name}", text_color=EXITO)
        self.boton_abrir.grid(row=0, column=1, padx=(6, 0))


if __name__ == "__main__":
    ctk.set_appearance_mode("system")  # Starts in light or dark mode, like your computer
    app = AppQR()
    app.mainloop()
