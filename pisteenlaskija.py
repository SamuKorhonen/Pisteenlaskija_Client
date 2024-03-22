from tkinter import *
from PIL import ImageTk, Image
from globals import *
from tkinter.font import Font


def kirjoitaKierrosLyhenteet():
    tempY = 85
    for i in kierrosLyhenne:
        ikkunaCanvas.create_text(10, tempY, anchor="w", text=i, font=perusFontti, fill=fonttiVari)
        tempY = tempY + 38


root = Tk()

root.title("Sanghai Pisteenlaskija")
# window.geometry("1280x720")
# window.minsize(width=640, height=360)

sijaintiX = sijaintiXOletus
sijaintiY = sijaintiYOletus
perusFontti = Font(family='Arial', size=24)
isoFontti = Font(family='Arial', size=38)
pieniFontti = Font(family='Arial', size=16)
print(virhe)
pelaaja = [{'nimi':'pekka'},{'nimi':'matti'}]

# e = Tausta(window)
# e.pack(fill=BOTH, expand=YES)
# e.pack_propagate(False)

background_image = Image.open(".venv/media/tausta.png")

resized_background = background_image.resize((1280, 720), Image.ADAPTIVE)
background_width, background_height = resized_background.size
background_image2 = ImageTk.PhotoImage(resized_background)

ikkunaCanvas = Canvas(root, width=background_width, height=background_height)
ikkunaCanvas.pack()

ikkunaCanvas.create_image(0, 0, anchor="nw", image=background_image2)

# kierrosCanvas = Canvas(e, width=100, height=600)
# kierrosCanvas.pack()

ikkunaCanvasHeight = ikkunaCanvas.winfo_height()
ekaKierrosYLocation = int(0.1 * ikkunaCanvasHeight)
print(ekaKierrosYLocation)

kirjoitaKierrosLyhenteet()
ikkunaCanvas.create_text(vasenMarginaali, kokoPisteMarginaali, anchor="w", text="Kokonaispisteet:", font=perusFontti, fill=fonttiVari)

kokoPisteMarginaali = kokoPisteMarginaali + 38
for i in pelaaja:
    ikkunaCanvas.create_text(vasenMarginaali+50, kokoPisteMarginaali, anchor="w", text=i['nimi'],
                             font=perusFontti, fill=fonttiVari)
    kokoPisteMarginaali = kokoPisteMarginaali + 38


kokoPisteMarginaali = 423


# kierrosFrame = Frame(window, relief = 'raised', borderwidth=0)
# kierrosFrame.place(y= 85, anchor='w')
# text1=kierrosFrame.winfo_geometry()

# Label(kierrosFrame, text=text1, font= ('Helvetica 15')).pack()
# Label(kierrosFrame, text="K+S", font= ('Helvetica 15')).pack()

root.mainloop()
