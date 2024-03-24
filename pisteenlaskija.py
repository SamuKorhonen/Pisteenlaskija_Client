from tkinter import *
from PIL import ImageTk, Image
from globals import *
from tkinter.font import Font


class PisteenlaskijaUI(Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.master = master
        self.pack()

        self.perusFontti = Font(family='Arial', size=fonttiKoko)
        self.isoFontti = Font(family='Arial', size=fonttiKokoIso)
        self.pieniFontti = Font(family='Arial', size=fonttiKokoPieni)

        self.kierrosText = []

        self.taustakuva_original = Image.open(".venv/media/tausta.png")
        self.taustakuva_resized = self.taustakuva_original.resize((ikkuna_leveys, ikkuna_korkeus))
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)

        self.rootCanvas = Canvas(self.master, width=ikkuna_leveys, height=ikkuna_korkeus)
        self.muokattu_tausta = self.rootCanvas.create_image(0, 0, anchor="nw", image=self.uusi_tausta)

        y_temp = ekaKierrosYLocation
        for i in kierrosLyhenne:
            text = self.rootCanvas.create_text(10, y_temp, anchor="w", text=i, font=self.perusFontti, fill=fonttiVari)
            self.kierrosText.append(text)
            y_temp += fonttiKokoIso

        self.text_Kokopiste = self.rootCanvas.create_text(vasenMarginaali, kokoPisteMarginaali,
                                                          anchor="w", text="Kokonaispisteet", font=self.perusFontti,
                                                          fill=fonttiVari)

        self.rootCanvas.pack()
        self.pack()

        master.bind("<Configure>", self.scale_objects)

    def scale_objects(self, event=None):
        # For scaling update the screen_width and screen_height variables
        ikkuna_leveys_scaled = self.master.winfo_width()
        ikkuna_korkeus_scaled = self.master.winfo_height()

        # Updated Locations:
        eka_kierros_y_location_scaled = int(0.12 * ikkuna_korkeus_scaled)
        koko_piste_marginaali_scaled = int(ikkuna_korkeus_scaled * (423 / 720))
        fontti_koko_iso_scaled = int(ikkuna_korkeus_scaled * (38 / 720))
        fontti_koko_scaled = int(ikkuna_korkeus_scaled * (24 / 720))
        fontti_koko_pieni_scaled = int(ikkuna_korkeus_scaled * (16 / 720))

        # Update font -objects to correct size:
        self.perusFontti = Font(family='Arial', size=fontti_koko_scaled)
        self.isoFontti = Font(family='Arial', size=fontti_koko_iso_scaled)
        self.pieniFontti = Font(family='Arial', size=fontti_koko_pieni_scaled)

        # update texts based of the updated variables above
        y_temp = eka_kierros_y_location_scaled
        for item in range(len(self.kierrosText)):
            self.rootCanvas.coords(self.kierrosText[item], vasenMarginaali, y_temp)
            self.rootCanvas.itemconfig(self.kierrosText[item], font=self.perusFontti)
            y_temp += fontti_koko_iso_scaled

        self.rootCanvas.coords(self.text_Kokopiste, vasenMarginaali, koko_piste_marginaali_scaled)
        self.rootCanvas.itemconfig(self.text_Kokopiste, font=self.perusFontti)
        self.taustakuva_resized = self.taustakuva_original.resize((ikkuna_leveys_scaled, ikkuna_korkeus_scaled))
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)
        self.rootCanvas.itemconfig(self.muokattu_tausta, image=self.uusi_tausta)


# super simple window creation, which get all objects from Pisteenlaskija -class
root = Tk()
root.title("Sanghai Pisteenlaskija")
root.geometry("1280x720")
pelaaja = [{'nimi': 'pekka'}, {'nimi': 'matti'}]
PisteenlaskijaUI(root)
root.mainloop()
