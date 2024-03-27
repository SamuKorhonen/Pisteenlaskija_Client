from tkinter import *
from PIL import ImageTk, Image
from globals import *
from tkinter.font import Font

# Create default values


class PisteenlaskijaUI(Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.master = master
        self.pack()

        self.perusFontti = Font(family='Arial', size=fonttiKoko)
        self.isoFontti = Font(family='Arial', size=fonttiKokoIso)
        self.pieniFontti = Font(family='Arial', size=fonttiKokoPieni)

        self.nimi_var = StringVar()

        self.kierrosText = []
        self.pelaajaText = []
        self.ikkunaKorkeus = ikkuna_korkeus
        self.ikkunaLeveys = ikkuna_leveys


        self.taustakuva_original = Image.open("media/tausta.bmp")
        self.taustakuva_resized = self.taustakuva_original.resize((ikkunaXScale, ikkunaYScale),
                                                                  Image.Resampling.LANCZOS)
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)

        self.rootCanvas = Canvas(self.master, width=ikkunaXScale, height=ikkunaYScale)
        self.muokattu_tausta = self.rootCanvas.create_image(0, 0, anchor="nw", image=self.uusi_tausta)

        self.valintaViiva = self.rootCanvas.create_line(valintaSijaintiX, valintaSijaintiY, valintaSijaintiX+sarakkeenLeveys, valintaSijaintiY, fill=fonttiVari, width=2)

        for i in range(pelaajaMaara):
            temp = self.rootCanvas.create_text(vasenMarginaali + 30, 50, anchor="w", text='',
                                           font=self.perusFontti, fill=fonttiVari)
            self.pelaajaText.append(temp)

        y_temp = ekaKierrosYLocation
        for i in kierrosLyhenne:
            text = self.rootCanvas.create_text(10, y_temp, anchor="w", text=i, font=self.perusFontti, fill=fonttiVari)
            self.kierrosText.append(text)
            y_temp += fonttiKokoIso

        self.text_Kokopiste = self.rootCanvas.create_text(vasenMarginaali, kokoPisteMarginaali,
                                                          anchor="w", text="Kokonaispisteet:", font=self.perusFontti,
                                                          fill=fonttiVari)

        self.pelaajaTemp = {}
        self.pelaajaUusiTemp = Entry(self.rootCanvas, textvariable=self.nimi_var)
        self.pelaajaUusiTemp.place(x=-100, y=-100)
        self.pelaajaUusiTemp.focus_set()
        # self.pelaajaUusiTemp.pack()

        self.pelaajaNimi = self.rootCanvas.create_text(valintaSijaintiX+(sarakkeenLeveys/2), valintaSijaintiY-fonttiKoko,
                                                       text="", font=self.perusFontti, fill=fonttiVari)
        master.bind('<KeyPress>', self.update_pelaaja_nimi)

        master.bind('<Return>', self.set_name)

        '''
        y_temp = kokoPisteMarginaali + fonttiKokoIso
        for i in pelaaja:
            text = self.rootCanvas.create_text(vasenMarginaali + 30, y_temp, anchor="w", text=i['nimi'],
                                               font=self.perusFontti, fill=fonttiVari)
            self.pelaajaText.append(text)
            y_temp += fonttiKokoIso
        '''

        self.rootCanvas.pack()
        self.pack()

        master.bind("<Configure>", self.scale_objects)

    def update_pelaaja_nimi(self, event=None):
        self.rootCanvas.itemconfig(self.pelaajaNimi, text=self.pelaajaUusiTemp.get())

    def set_name(self, event=None):
        # self.pelaajaTemp['nimi'] = self.nimi_var.get()
        pelaaja[valittu]['nimi'] = self.nimi_var.get()

        self.rootCanvas.itemconfig(self.pelaajaText[valittu], text=pelaaja[valittu]['nimi'])
        self.scale_objects()

        self.pelaajaTemp = {}
        # self.nimi_var = ''
        print(pelaaja)

        self.pelaajaUusiTemp.delete(0, END)
        self.rootCanvas.itemconfig(self.pelaajaNimi, text=self.pelaajaUusiTemp.get())
        self.pelaajaUusiTemp.place(x=-100, y=-100)

    def scale_objects(self, event=None):
        # For scaling update the screen_width and screen_height variables
        ikkuna_leveys_scaled = self.master.winfo_width()
        ikkuna_korkeus_scaled = self.master.winfo_height()


        # Updated Locations:
        eka_kierros_y_location_scaled = ikkuna_korkeus_scaled * (ekaKierrosYLocation / ikkunaYScale)
        koko_piste_marginaali_scaled = ikkuna_korkeus_scaled * (kokoPisteMarginaali / ikkunaYScale)
        vasen_marginaali_scaled = ikkuna_leveys_scaled * (vasenMarginaali / ikkunaXScale)
        vasen_kokopiste_nimi_marginaali_scaled = ikkuna_leveys_scaled * (vasenKokoPisteNimiMarginaali / ikkunaXScale)
        fontti_koko_iso_scaled = ikkuna_korkeus_scaled * (fonttiKokoIso / ikkunaYScale)
        fontti_koko_scaled = ikkuna_korkeus_scaled * (fonttiKoko / ikkunaYScale)
        fontti_koko_pieni_scaled = ikkuna_korkeus_scaled * (fonttiKokoPieni / ikkunaYScale)
        valinta_sijainti_x_scaled = ikkuna_leveys_scaled * (valintaSijaintiX/ikkunaXScale)
        valinta_sijainti_y_scaled = ikkuna_korkeus_scaled * (valintaSijaintiY/ikkunaYScale)
        sarakkeen_leveys_scaled = ikkuna_leveys_scaled * (sarakkeenLeveys / ikkunaXScale)

        # Update font -objects to correct size:
        self.perusFontti = Font(family='Arial', size=int(fontti_koko_scaled))
        self.isoFontti = Font(family='Arial', size=int(fontti_koko_iso_scaled))
        self.pieniFontti = Font(family='Arial', size=int(fontti_koko_pieni_scaled))

        # update texts based of the updated variables above
        y_temp = eka_kierros_y_location_scaled
        for item in range(len(self.kierrosText)):
            self.rootCanvas.coords(self.kierrosText[item], vasen_marginaali_scaled, y_temp)
            self.rootCanvas.itemconfig(self.kierrosText[item], font=self.pieniFontti)
            y_temp += fontti_koko_iso_scaled

        y_temp = koko_piste_marginaali_scaled + fontti_koko_iso_scaled
        for item in range(len(self.pelaajaText)):
            self.rootCanvas.coords(self.pelaajaText[item], vasen_kokopiste_nimi_marginaali_scaled, y_temp)
            self.rootCanvas.itemconfig(self.pelaajaText[item], font=self.perusFontti)
            y_temp += fontti_koko_iso_scaled

        self.rootCanvas.coords(self.valintaViiva, valinta_sijainti_x_scaled, valinta_sijainti_y_scaled,
                               valinta_sijainti_x_scaled+sarakkeen_leveys_scaled, valinta_sijainti_y_scaled)
        self.rootCanvas.coords(self.text_Kokopiste, vasen_marginaali_scaled, koko_piste_marginaali_scaled)
        self.rootCanvas.itemconfig(self.text_Kokopiste, font=self.perusFontti)
        self.rootCanvas.configure(height=ikkuna_korkeus_scaled, width=ikkuna_leveys_scaled)
        self.taustakuva_resized = self.taustakuva_original.resize((ikkuna_leveys_scaled, ikkuna_korkeus_scaled),
                                                                  Image.Resampling.LANCZOS)
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)
        self.rootCanvas.itemconfig(self.muokattu_tausta, image=self.uusi_tausta)


# super simple window creation, which get all objects from Pisteenlaskija -class
root = Tk()
root.title("Sanghai Pisteenlaskija")
root.geometry("1280x720")
pelaaja = []
for i in range(pelaajaMaara+1):
    temp = {'nimi': ''}
    pelaaja.append(temp)
PisteenlaskijaUI(root)
root.mainloop()
