from tkinter import *
from PIL import ImageTk, Image
from globals import *
from tkinter.font import Font

'''
To-Do List:
- Loput tekstit näyttöön
- tallennus ja lataus
- Asetukset
- Serveri yhteys
- Turnaus versio muokkaukset
- Virhe ilmoitukset ja tunnistukset esim pisteistä
    - Pisteissä virheet
    - Pelaajamäärässä virhe
    - yhteydessä palvelimeen virhe
    
- Ohje näyttö
- Lisää näyttöön versio tieto
- Nimien lyhennys
- Hiiren käyttö
- Jakajan hallinta
- Pelaajien järjestäminen pistejärjestykseen
- 
'''

pelaajaMaara = 5


class AsetuksetIkkuna(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Settings")
        # self.overrideredirect(True)
        self.geometry("300x200")

        self.label = Label(self, text="Setting 1:")
        self.label.pack()

        self.entry = Entry(self)
        self.entry.pack()


class PisteenlaskijaUI(Frame):
    # Käyttöliittymä CLASS, jonka sisällä luodaan visuaalinen kokonaisuus
    def __init__(self, master=None):
        # __init__ on pää funktio classin sisällä, joka suoritetaan automaattisesti
        # Ensimmäisenä luodaan tärkeimmät muuttujat ja
        super().__init__(master=master)
        self.master = master
        self.pack()
        self.settings_window = None
        self.perusFontti = Font(family='Arial', size=fonttiKoko)
        self.isoFontti = Font(family='Arial', size=fonttiKokoIso)
        self.pieniFontti = Font(family='Arial', size=fonttiKokoPieni)
        self.nimi_var = StringVar()
        self.kierrosText = []  # Tämä on kierros teksti-objektien säilömiseen tarkoitettu array
        self.pelaajaText = []  # Tämä on kokonaispisteissä näkyvien pelaajien nimien teksti objetien säilömiseen
        self.pelaajaNimi = []  # Tämä on ylhäällä nimirivillä olevia teksti-objekteja varten
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
        master.bind('<Button-1>', self.hiiren_valinta)

        self.rootCanvas.pack()
        self.pack()

        # Jos ikkunan koko muuttuu, niin skaalataan objektit muuttuneen ikkunan mukaiseksi
        master.bind("<Configure>", self.scale_objects)

    def show_settings(self):
        # print("olet asetuksissa")
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = AsetuksetIkkuna(self.master)
        else:
            self.settings_window.destroy()

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
        elif painallus == "F9":
            self.show_settings()

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
                # print(temp_nimi)
            else:
                if kirjain == "\b":
                    temp_pisteet = str(pelaaja[valittu]['pisteet'][valittuKierros - 1])[:-1]
                    if not temp_pisteet:
                        temp_pisteet = '0'

                elif kirjain.isdigit():
                    temp_pisteet = str(pelaaja[valittu]['pisteet'][valittuKierros - 1]) + kirjain
                else:
                    return

                pelaaja[valittu]['pisteet'][valittuKierros - 1] = temp_pisteet
                self.rootCanvas.itemconfig(self.kierrosPisteet[valittuKierros][valittu], text=temp_pisteet)
                # print(pelaaja[valittu], valittuKierros)

    def hiiren_valinta(self, event):
        hiiri_x = event.x
        hiiri_y = event.y
        print(hiiri_x, hiiri_y)
        '''
        Koodia jossa tunnistetaan missä Hiiri on näytöllä pikseleistä. HUOM! Tässä kohtaa täytyy huomoioida ikkunan 
        skaalautuvuus, jolloin tarvitsee myös tehdä suhteellinen laskenta eri osien koosta.
        '''

    def seuraava_kierros(self):

        global kierrosNumero
        global pelaaja
        global pelaajaMaara
        global valintaSijaintiY
        global valintaSijaintiX
        global sarakkeenLeveys
        global valittuKierros
        global virhe

        self.virheen_tarkistus()
        if virhe:
            print("virhe on: " + str(virhe))

        if virhe == 0:
            if kierrosNumero == 0:
                pelaaja = [item for item in pelaaja if item['nimi']]
                self.pelaajaText = [item for item in self.pelaajaText if self.rootCanvas.itemconfig(item)['text'][4]]
                self.pelaajaNimi = [item for item in self.pelaajaNimi if self.rootCanvas.itemconfig(item)['text'][4]]
                pelaajaMaara = len(pelaaja) - 1
                sarakkeenLeveys = (ikkunaXScale - sijaintiXOletus) / (pelaajaMaara + 1)
                kierrosNumero += 1
                valintaSijaintiY += fonttiKokoIso
                valintaSijaintiX = sijaintiXOletus + (sarakkeenLeveys * valittu)
                valittuKierros += 1
                x_temp = sijaintiXOletus + (sarakkeenLeveys / 2)
                y_temp = ekaKierrosYLocation + (fonttiKokoIso * kierrosNumero)
                kierros_numero_oikea = kierrosNumero - 1
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
                valintaSijaintiY = fonttiKokoIso * kierrosNumero + sijaintiYOletus
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

        # print(self.pelaajaText, kierrosNumero, pelaajaMaara, sarakkeenLeveys)

    def pisteiden_laskenta(self):
        # kokonaispisteiden laskenta

        for item in pelaaja:
            kokoPiste = 0
            for item2 in item['pisteet']:
                if item2:
                    kokoPiste += int(item2)
            item['kokonaisPisteet'] = kokoPiste
            print(item['kokonaisPisteet'])

    def virheen_tarkistus(self):

        global virhe

        virhe = 0

        # tarkista pelaajat, jos alle 3 tai löytyy saman nimisiä pelaajia, niin luodaan virhe
        if kierrosNumero == 0:
            '''
            Alla tapahtuu seuraavat toiminnot:
            1. luodaan array pelaajien nimistä
            2. otetaan arraysta poist tyhjät nimet (huom välilyönti ei ole tyhjä)
            3. luodaan lista arraysta, jossa ei voi olla duplikaatteja
            4. lopuksi vertaamalla kaikkien nimien määrää erillaisten nimien määrään tiedetään onko duplikaatteja
            '''
            pelaaja_temp = [item['nimi'] for item in pelaaja]       # 1
            pelaaja_temp = [item for item in pelaaja_temp if item]  # 2
            pelaaja_temp_set = set(pelaaja_temp)                    # 3
            if len(pelaaja_temp) > len(pelaaja_temp_set):           # 4
                virhe = 4

            if len(pelaaja_temp) < 3:
                virhe = 3
        else:
            '''
            tarkistetaan voittajien määrä per kierros. Jos eri määrä kuin 1, niin annetaan virhe.
            alla kuvaus mitä tapahtuu:
            1. ensiksi haetaan pisteet pelaaja objektista
            2. sitten muotoillaan ne kierroksittaisiin arrayhyn
            3. ja lopuksi karsitaan pois tulevat kierrokset
            4. sen jälkeen tarkistetaan kierros kierrokselta, kuinka monta nolla tulosta sieltä löytyy
            5. lopulta tarkistetaan vielä noilta kierroksilta, että pisteet ovat uskottavia
            '''
            kierros_pisteet_temp = [item['pisteet'] for item in pelaaja]                # 1
            kierros_pisteet_temp = [[row[i] for row in kierros_pisteet_temp] for i
                                    in range(len(kierros_pisteet_temp[0]))]             # 2
            kierros_pisteet_temp = kierros_pisteet_temp[:kierrosNumero]                 # 3
            print(kierros_pisteet_temp)

            for kierros_nyt in kierros_pisteet_temp:                                    # 4
                voittaja = sum(item == '' or item == '0' for item in kierros_nyt)
                print(voittaja)
                if voittaja != 1:
                    virhe = 1
                for piste in kierros_nyt:                                               # 5
                    print(piste)
                    if piste == '':
                        piste = 0
                    if int(piste) > 200 or int(piste) == 1:
                        virhe = 1

    def scale_objects(self, event=None):
        # For scaling update the screen_width and screen_height variables
        ikkuna_leveys_scaled = self.master.winfo_width()
        ikkuna_korkeus_scaled = self.master.winfo_height()

        # Updated Locations:
        eka_kierros_y_location_scaled = ikkuna_korkeus_scaled * (ekaKierrosYLocation / ikkunaYScale)
        koko_piste_marginaali_scaled = ikkuna_korkeus_scaled * (kokoPisteMarginaali / ikkunaYScale)
        vasen_marginaali_scaled = ikkuna_leveys_scaled * (vasenMarginaali / ikkunaXScale)
        vasen_kokopiste_nimi_marginaali_scaled = ikkuna_leveys_scaled * (vasenKokoPisteNimiMarginaali / ikkunaXScale)
        vasen_kokopiste_piste_marginaali_scaled = ikkuna_leveys_scaled * (vasenKokoPisteMarginaali / ikkunaXScale)
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
        # print(self.kierrosPisteet)
        for item in self.kierrosPisteet:
            for item2 in item:
                self.rootCanvas.coords(item2, x_temp, y_temp)
                self.rootCanvas.itemconfig(item2, font=self.perusFontti)
                x_temp += sarakkeen_leveys_scaled
            x_temp = sijainti_x_oletus_scaled + (sarakkeen_leveys_scaled / 2)
            y_temp += fontti_koko_iso_scaled

        y_temp = koko_piste_marginaali_scaled + fontti_koko_iso_scaled
        for item in self.kokoPisteTeksti:
            self.rootCanvas.coords(item, vasen_kokopiste_piste_marginaali_scaled, y_temp)
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
