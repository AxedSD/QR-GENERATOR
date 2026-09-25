<div align="center">

# QR Studio

**Turn any link into a stylish QR code: a desktop app made with Python.**

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![GUI: CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-6C5CE7)

**English** · [Español](README.es.md)

<img src="docs/demo.gif" alt="QR Studio demo: typing a link, changing the color and style, saving the QR and switching to dark mode">

</div>

## ✨ Features

- **Live preview**: the QR code updates while you type the link.
- **6 colors and 3 styles**: square, rounded or dots. The colors are dark on purpose, so phones can still scan them.
- **Light and dark mode**: starts like your computer and switches with one click.
- **Friendly errors**: the field with the problem turns red and a message tells you what to fix. No annoying pop-ups.
- **Safe saving**: asks before replacing a QR that has the same name.
- **Open folder**: after saving, one click opens the folder with your new QR.

## 🎨 Styles

| Square | Rounded | Dots |
| :---: | :---: | :---: |
| <img src="docs/style-square.png" width="180" alt="Square QR code"> | <img src="docs/style-rounded.png" width="180" alt="Rounded QR code"> | <img src="docs/style-dots.png" width="180" alt="QR code made of dots"> |

> 📱 Try scanning them: all three open this repository!

## 🌗 Light and dark mode

| Light | Dark |
| :---: | :---: |
| <img src="docs/light.png" alt="QR Studio in light mode"> | <img src="docs/dark.png" alt="QR Studio in dark mode"> |

## 🚀 Getting started

You need **Python 3.9 or newer** ([download it here](https://www.python.org/downloads/)).

1. Download the project:
   ```bash
   git clone https://github.com/AxedSD/QR-GENERATOR.git
   cd QR-GENERATOR
   ```
2. Install the libraries it uses:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Open the app:
   ```bash
   python qr_gui.py
   ```

> **Tip:** on macOS and Linux you may need to type `python3` instead of `python`. On Linux, if you see `No module named 'tkinter'`, install it with `sudo apt install python3-tk`.

### How to use it

1. Paste a link in **LINK**.
2. Pick a **COLOR** and a **STYLE**. The preview changes right away.
3. Give your QR a **FILE NAME** and choose where to save it (**SAVE IN**).
4. Press **Save QR** (or <kbd>Enter</kbd>). Your QR is saved as a `.png` image.

## 💻 The original terminal version

This project started as a program that runs in the terminal: [`codedexfinal.py`](codedexfinal.py). It is still here and it still works:

```bash
python codedexfinal.py
```

It asks for a folder name. Then, for every link you type, it asks for a name and saves a black and white QR (type `0` to finish).

## 📁 Project structure

```
QR-GENERATOR/
├── qr_gui.py          # QR Studio, the app with windows and buttons
├── codedexfinal.py    # The original terminal version
├── requirements.txt   # Libraries to install
├── README.md          # This page (English)
├── README.es.md       # This page (Spanish)
└── docs/              # Images for the README
```

## 🛠️ Built with

- [Python](https://www.python.org/)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter): modern-looking windows and buttons
- [qrcode](https://github.com/lincolnloop/python-qrcode): creates the QR codes
- [Pillow](https://python-pillow.org/): works with the images

## 👋 About

This was my first Python project 🐍. It started as a small terminal program and grew into a full desktop app.

Made by [@AxedSD](https://github.com/AxedSD).
