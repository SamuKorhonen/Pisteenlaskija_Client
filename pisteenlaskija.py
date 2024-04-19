from tkinter import *
from PIL import ImageTk, Image
from globals import *
from tkinter.font import Font

pelaajaMaara = 5


class PisteenlaskijaUI(Frame):
    # Käyttöliittymä CLASS, jonka sisällä luodaan visuaalinen kokonaisuus
    def __init__(self, master=None):
        # __init__ on pää funktio classin sisällä, joka suoritetaan automaattisesti
        # Ensimmäisenä luodaan tärkeimmät muuttujat ja
        super().__init__(master=master)
        self.master = master
        self.pack()
        self.perusFontti = Font(family='Arial', size=fonttiKoko)
        self.isoFontti = Font(family='Arial', size=fonttiKokoIso)
        self.pieniFontti = Font(family='Arial', size=fonttiKokoPieni)
        self.nimi_var = StringVar()
        self.kierrosText = []       # Tämä on kierros teksti-objektien säilömiseen tarkoitettu array
        self.pelaajaText = []       # Tämä on kokonaispisteissä näkyvien pelaajien nimien teksti objetien säilömiseen
        self.pelaajaNimi = []       # Tämä on ylhäällä nimirivillä olevia teksti-objekteja varten
        self.kierrosPisteet = []
        self.kokoPisteTeksti = []
        for i_temp in range(9):
            self.kierrosPisteet.append([])
        print(self.kierrosPisteet)

        # ladataan ja muokataan taustakuva ikkunaan
        self.taustakuva_original = Image.open("media/tausta.bmp")
        self.taustakuva_resized = self.taustakuva_original.resize((ikkunaXScale, ikkunaYScale),
                                                                  Image.Resampling.LANCZOS)
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)
        # HUOM! RootCanvas sisältää myös pääsääntöisesti tekstiobjektit
        self.rootCanvas = Canvas(self.master, width=ikkunaXScale, height=ikkunaYScale)
        self.muokattu_tausta = self.rootCanvas.create_image(0, 0, anchor="nw", image=self.uusi_tausta)

        self.valintaViiva = self.rootCanvas.create_line(valintaSijaintiX, valintaSijaintiY,
                                                        valintaSijaintiX + sarakkeenLeveys, valintaSijaintiY,
                                                        fill=fonttiVari, width=2)

        # Luodaan teksti-objektit pelaajaText, pelaajaNimi ja kierrosText Arraytten sisälle
        for item in range(pelaajaMaara + 1):
            temp_text = self.rootCanvas.create_text(vasenMarginaali + 30, 50, anchor="w", text='',
                                                    font=self.perusFontti, fill=fonttiVari)
            self.pelaajaText.append(temp_text)

        x_temp = valintaSijaintiX + (sarakkeenLeveys / 2)
        for item in range(pelaajaMaara + 1):
            temp_text = self.rootCanvas.create_text(x_temp, valintaSijaintiY - fonttiKoko, text='',
                                                    font=self.perusFontti, fill=fonttiVari)
            x_temp += sarakkeenLeveys
            self.pelaajaNimi.append(temp_text)

        y_temp = ekaKierrosYLocation
        for it in kierrosLyhenne:
            text = self.rootCanvas.create_text(10, y_temp, anchor="w", text=it, font=self.perusFontti, fill=fonttiVari)
            self.kierrosText.append(text)
            y_temp += fonttiKokoIso

        self.text_Kokopiste = self.rootCanvas.create_text(vasenMarginaali, kokoPisteMarginaali,
                                                          anchor="w", text="Kokonaispisteet:", font=self.perusFontti,
                                                          fill=fonttiVari)

        # Varmistetaan onko jotain näppäintä painettu
        # ja jos on mennään "painettu" -funktiossa varmistamaan mitä sitten tehdään
        master.bind('<KeyPress>', self.painettu)

        self.rootCanvas.pack()
        self.pack()

        # Jos ikkunan koko muuttuu, niin skaalataan objektit muuttuneen ikkunan mukaiseksi
        master.bind("<Configure>", self.scale_objects)

    def painettu(self, event=None):

        # varmistetaan mitä on painettu
        painallus = event.keysym
        kirjain = event.char
        print(painallus)
        global valittu
        global valintaSijaintiX
        global valintaSijaintiY
        global pelaaja
        global valittuKierros
        global kierrosNumero

        if painallus == "Right" or painallus == "Tab":
            # self.set_name()
            valintaSijaintiX += sarakkeenLeveys
            valittu += 1
            if valittu > pelaajaMaara:
                valintaSijaintiX = sijaintiXOletus
                valittu = 0
            self.scale_objects()
        elif painallus == "Left":
            # self.set_name()
            valintaSijaintiX = valintaSijaintiX - sarakkeenLeveys
            valittu = valittu - 1
            if valittu < 0:
                valintaSijaintiX = sijaintiXOletus + (pelaajaMaara * sarakkeenLeveys)
                valittu = pelaajaMaara
            self.scale_objects()
        elif painallus == "Down":
            valittuKierros += 1
            valintaSijaintiY += fonttiKokoIso
            if valittuKierros > kierrosNumero:
                valittuKierros = 0
                valintaSijaintiY = sijaintiYOletus
            self.scale_objects()
        elif painallus == "Up":
            valittuKierros = valittuKierros - 1
            valintaSijaintiY = valintaSijaintiY - fonttiKokoIso
            if valittuKierros < 0:
                valittuKierros = kierrosNumero
                valintaSijaintiY = sijaintiYOletus
            self.scale_objects()

        elif painallus == "Return" or painallus == "KP_Enter":
            self.seuraava_kierros()
            self.scale_objects()
        else:
            if valittuKierros == 0:
                if kirjain == "\b":
                    temp_nimi = pelaaja[valittu]['nimi'][:-1]
                else:
                    temp_nimi = pelaaja[valittu]['nimi'] + kirjain

                pelaaja[valittu]['nimi'] = temp_nimi
                self.rootCanvas.itemconfig(self.pelaajaText[valittu], text=temp_nimi)
                self.rootCanvas.itemconfig(self.pelaajaNimi[valittu], text=temp_nimi)
                print(temp_nimi)
            else:
                if kirjain == "\b":
                    temp_pisteet = str(pelaaja[valittu]['pisteet'][valittuKierros-1])[:-1]
                    if not temp_pisteet:
                        temp_pisteet = '0'

                elif kirjain.isdigit():
                    temp_pisteet = str(pelaaja[valittu]['pisteet'][valittuKierros-1]) + kirjain
                else:
                    return

                pelaaja[valittu]['pisteet'][valittuKierros-1] = temp_pisteet
                self.rootCanvas.itemconfig(self.kierrosPisteet[valittuKierros][valittu], text=temp_pisteet)
                print(pelaaja[valittu], valittuKierros)

    def seuraava_kierros(self):

        global kierrosNumero
        global pelaaja
        global pelaajaMaara
        global valintaSijaintiY
        global valintaSijaintiX
        global sarakkeenLeveys
        global valittuKierros

        if kierrosNumero == 0:
            pelaaja = [item for item in pelaaja if item['nimi']]
            self.pelaajaText = [item for item in self.pelaajaText if self.rootCanvas.itemconfig(item)['text'][4]]
            self.pelaajaNimi = [item for item in self.pelaajaNimi if self.rootCanvas.itemconfig(item)['text'][4]]
            pelaajaMaara = len(pelaaja)-1
            sarakkeenLeveys = (ikkunaXScale - sijaintiXOletus) / (pelaajaMaara + 1)
            kierrosNumero += 1
            valintaSijaintiY += fonttiKokoIso
            valintaSijaintiX = sijaintiXOletus + (sarakkeenLeveys*valittu)
            valittuKierros += 1
            x_temp = sijaintiXOletus + (sarakkeenLeveys / 2)
            y_temp = ekaKierrosYLocation + (fonttiKokoIso * kierrosNumero)
            kierros_numero_oikea = kierrosNumero-1
            print(kierros_numero_oikea, pelaaja[0]['pisteet'][0])
            for item in range(len(pelaaja)):
                temp_item = self.rootCanvas.create_text(x_temp, y_temp, text='',
                                                        font=self.perusFontti, fill=fonttiVari)
                temp_item2 = self.rootCanvas.create_text(vasenMarginaali, kokoPisteMarginaali, text='',
                                                         font=self.perusFontti, fill=fonttiVari)
                self.kierrosPisteet[kierrosNumero].append(temp_item)
                self.kokoPisteTeksti.append(temp_item2)
                x_temp += sarakkeenLeveys
        elif kierrosNumero < 9:
            kierrosNumero += 1
            valintaSijaintiY = fonttiKokoIso*kierrosNumero + sijaintiYOletus
            valittuKierros = kierrosNumero
            self.pisteiden_laskenta()
            x_temp = sijaintiXOletus + (sarakkeenLeveys / 2)
            y_temp = ekaKierrosYLocation + (fonttiKokoIso * kierrosNumero)
            # kierros_numero_oikea = kierrosNumero - 1
            # print(kierros_numero_oikea, pelaaja[0]['pisteet'][0])
            for item in range(len(pelaaja)):
                temp_item = self.rootCanvas.create_text(x_temp, y_temp, text='',
                                                        font=self.perusFontti, fill=fonttiVari)
                self.kierrosPisteet[kierrosNumero].append(temp_item)
                x_temp += sarakkeenLeveys
            for item in range(len(pelaaja)):
                self.rootCanvas.itemconfig(self.kokoPisteTeksti[item], text=pelaaja[item]['kokonaisPisteet'])

        print(self.pelaajaText, kierrosNumero, pelaajaMaara, sarakkeenLeveys)

    def pisteiden_laskenta(self):
        # kokonaispisteiden laskenta

        for item in pelaaja:
            kokoPiste = 0
            for item2 in item['pisteet']:
                if item2:
                    kokoPiste += int(item2)
            item['kokonaisPisteet'] = kokoPiste
            print(item['kokonaisPisteet'])

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
        valinta_sijainti_x_scaled = ikkuna_leveys_scaled * (valintaSijaintiX / ikkunaXScale)
        valinta_sijainti_y_scaled = ikkuna_korkeus_scaled * (valintaSijaintiY / ikkunaYScale)
        nimi_sijainti_y_scaled = ikkuna_korkeus_scaled * (sijaintiYOletus / ikkunaYScale)
        sarakkeen_leveys_scaled = ikkuna_leveys_scaled * (sarakkeenLeveys / ikkunaXScale)
        sijainti_x_oletus_scaled = ikkuna_leveys_scaled * (sijaintiXOletus / ikkunaXScale)

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

        x_temp = sijainti_x_oletus_scaled + (sarakkeen_leveys_scaled / 2)
        for item in range(len(self.pelaajaNimi)):
            self.rootCanvas.coords(self.pelaajaNimi[item], x_temp,
                                   nimi_sijainti_y_scaled - fontti_koko_scaled)
            self.rootCanvas.itemconfig(self.pelaajaNimi[item], font=self.perusFontti)
            x_temp += sarakkeen_leveys_scaled

        x_temp = sijainti_x_oletus_scaled + (sarakkeen_leveys_scaled / 2)
        y_temp = eka_kierros_y_location_scaled - fontti_koko_iso_scaled
        print(self.kierrosPisteet)
        for item in self.kierrosPisteet:
            for item2 in item:
                self.rootCanvas.coords(item2, x_temp, y_temp)
                self.rootCanvas.itemconfig(item2, font=self.perusFontti)
                x_temp += sarakkeen_leveys_scaled
            x_temp = sijainti_x_oletus_scaled + (sarakkeen_leveys_scaled / 2)
            y_temp += fontti_koko_iso_scaled

        self.rootCanvas.coords(self.valintaViiva, valinta_sijainti_x_scaled, valinta_sijainti_y_scaled,
                               valinta_sijainti_x_scaled + sarakkeen_leveys_scaled, valinta_sijainti_y_scaled)
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
for i in range(pelaajaMaara + 1):
    temp = {'nimi': '', 'pisteet': ['', '', '', '', '', '', '', '']}
    pelaaja.append(temp)
PisteenlaskijaUI(root)
root.mainloop()
