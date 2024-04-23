import functools
import tkinter.simpledialog
from tkinter import *
from PIL import ImageTk, Image
from globals import *
# from tkinter.font import Font
from tkinter import messagebox as mb
from json import load, dump
import os
# import pyglet
from tkextrafont import Font

'''
To-Do List:
- Asetukset
- Serveri yhteys
- Turnaus versio muokkaukset
- Virhe ilmoitukset ja tunnistukset esim pisteistä
    - yhteydessä palvelimeen virhe (tehdään vasta, kun päästään serveriyhteyden koodaukseen)

'''

pelaajaMaara = 5
versioNumero = 'Versio 3.0-beta'
#tkextrafont.TkExtraFont.chdir = resource_path()


# pyglet.font.add_file('media/SpecialElite-Regular.ttf')

def tallennus_nimet():
    for i in range(tallennuspaikat):
        tiedosto_nimi = f'saves/save_{i}.json'
        if os.path.isfile(tiedosto_nimi):
            with open(tiedosto_nimi, 'r') as f:
                haettu_data = load(f)
            tallennusNimi.append(haettu_data['tallennuksen_nimi'])
            f.close()
        else:
            tallennusNimi.append('')
    # print(tallennusNimi)

# def resource_path(relative_path):
#    """ Get absolute path to resource, works for dev and for PyInstaller """
#    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
#    return os.path.join(base_path, relative_path)


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

        Label(self, text='Tämä osio ei tee vielä mitään').pack()
        Label(self, text='Olethan kärsivällinen, rakennamme kovaa kyytiä').pack()


class OhjeIkkuna(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Ohjeet")
        self.geometry("600x500")

        self.frame = Frame(self)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')

        self.labels = [
            'Voit liikkua ohjelmassa nuolinäppäimillä tai käyttämällä hiirtä',
            ' ',
            'Kirjoittamalla pelaajat istumajärjestyksessä, ohjelma näyttää',
            'jakajan. Nimien jälkeen siirrytään pisteiden syöttöön painamalla "Enter"',
            'Jakaja voidaan valita nimien kirjoituksen yhteydessä painamalla',
            'nuolimäppäimiä ylös ja alas, tai hiirellä kokonaispisteiden luota',
            'Ensimmäinen pelaaja on oletuksena jakaja, jos sitä ei muuteta.',
            'Jakajan tunnistaa ympyröidystä J-kirjaimesta',
            ' ',
            'Saat pelin säännöt näkyviin painamalla "F11" (in progress)',
            'Laita pelatun kierroksen pisteet ja siirry',
            'seuraavalle kierrokselle painamalla "Enter"',
            ' ',
            'Poistu ohjeista painamalla "F1"',
            'Tallenna tai lataa peli painamalla "F4"',
            'Poistu ohjelmasta painamalla "ESC"'
        ]

        for x in range(len(self.labels)):
            self.L = Label(self.frame, text=self.labels[x])
            self.L.grid(row=x, column=0, sticky='nsew')

        self.bind('<F1>', self.destroy_window)

    def destroy_window(self, event):
        self.destroy()


class TallennusLatausIkkuna(Toplevel):
    def __init__(self, master, main_ui):
        super().__init__(master)
        self.master = master
        self.ui = main_ui
        self.title("Tallennus ja Lataus")
        self.geometry("600x500")

        self.frame = Frame(self)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')

        self.ohjeTekstit = [
            'Tallennus ja Lataus',
            ' '
            'Valitse tallennuspaikka ja sen jälkeen joko tallenna tai lataa',
            'riippuen kumman haluat tehdä',
            ' '
        ]
        for x in range(len(self.ohjeTekstit)):
            self.L = Label(self.frame, text=self.ohjeTekstit[x])
            self.L.grid(row=x, column=0, sticky='nsew')

        self.tallennusLabels = []
        current_row = len(self.ohjeTekstit) + 1
        for x in range(3):
            if tallennusNimi[x]:
                tulostus_nimi = tallennusNimi[x]
            else:
                tulostus_nimi = f'tallennuspaikka: {x}'
            label = Label(self.frame, text=tulostus_nimi)
            label.grid(row=current_row + x, column=0, sticky='nsew')
            Button(self.frame, text='Lataa', command=functools.partial(self.lataa_peli, x)
                   ).grid(row=current_row + x, column=1, sticky='nsew')
            Button(self.frame, text='tallenna', command=functools.partial(self.tallenna_peli, tiedosto=x)
                   ).grid(row=current_row + x, column=2, sticky='nsew')
            self.tallennusLabels.append(label)

        self.L = Label(self.frame, text="autotallennuspaikka")
        self.L.grid(row=current_row + 4, column=0, sticky='nsew')
        self.L = Button(self.frame, text='lataa', command=functools.partial(self.lataa_peli, 'auto'))
        self.L.grid(row=current_row + 4, column=1, sticky='nsew')

        self.bind('<F4>', self.destroy_window)

    def destroy_window(self, event):
        self.destroy()

    def lataa_peli(self, tiedosto):
        global pelaaja, pelaajaMaara, kierrosNumero, valittuKierros, valintaSijaintiX, valintaSijaintiY, jakaja
        global sarakkeenLeveys, valittu

        # avataan tiedosto
        tiedosto_nimi = f'saves/save_{tiedosto}.json'
        try:
            with open(tiedosto_nimi, 'r') as f:
                haettu_data = load(f)

            # haetaan tiedot
            pelaaja = haettu_data['pelaaja']
            pelaajaMaara = haettu_data['pelaajaMaara']
            kierrosNumero = haettu_data['kierrosNumero']
            valittuKierros = haettu_data['valittuKierros']
            valintaSijaintiX = haettu_data['valintaSijaintiX']
            valintaSijaintiY = haettu_data['valintaSijaintiY']
            jakaja = haettu_data['jakaja']
            sarakkeenLeveys = haettu_data['sarakkeenLeveys']
            valittu = haettu_data['valittu']

            # suljetaan tiedosto
            f.close()

            # nollataan näyttö ja muuttujat tarvittavalla tasolla
            self.ui.rootCanvas.delete('all')
            self.ui.kierrosLyhenneText = []
            self.ui.pelaajaText = []
            self.ui.pelaajaNimi = []
            self.ui.kierrosPisteet = []
            self.ui.kokoPisteTeksti = []
            for i_temp in range(9):
                self.ui.kierrosPisteet.append([])

            # luodaan näytön elementit uudestaan ladatun pelin tietojen pohjalta
            self.ui.muokattu_tausta = self.ui.rootCanvas.create_image(0, 0, anchor='nw', image=self.ui.uusi_tausta)
            self.ui.valintaViiva = self.ui.rootCanvas.create_line(valintaSijaintiX, valintaSijaintiY,
                                                                  valintaSijaintiX + sarakkeenLeveys, valintaSijaintiY,
                                                                  fill=fonttiVari, width=2)

            # tämä for -loop tekee kaikki pelaajakohtaiset tulostukset
            x_temp = sijaintiXOletus + (sarakkeenLeveys / 2)
            for item in range(pelaajaMaara + 1):
                temp_tx = self.ui.rootCanvas.create_text(vasenMarginaali + 30, 50, anchor='w',
                                                         text=pelaaja[item]['nimi'], font=self.ui.perusFontti,
                                                         fill=fonttiVari)
                self.ui.pelaajaText.append(temp_tx)

                temp_tx = self.ui.rootCanvas.create_text(x_temp, valintaSijaintiY - fonttiKoko,
                                                         text=pelaaja[item]['nimi'], font=self.ui.perusFontti,
                                                         fill=fonttiVari)
                self.ui.pelaajaNimi.append(temp_tx)
                x_temp += sarakkeenLeveys
                temp_tx = self.ui.rootCanvas.create_text(vasenKokoPisteNimiMarginaali, kokoPisteMarginaali,
                                                         text=pelaaja[item]['kokonaisPisteet'],
                                                         font=self.ui.perusFontti,
                                                         fill=fonttiVari)
                self.ui.kokoPisteTeksti.append(temp_tx)
                for krs in range(1, kierrosNumero + 1):
                    if krs < 9:
                        if pelaaja[item]['pisteet'][krs - 1] or krs == kierrosNumero:
                            temp_pisteet = pelaaja[item]['pisteet'][krs - 1]
                        else:
                            temp_pisteet = '0'

                        temp_tx = self.ui.rootCanvas.create_text(200, 500, text=temp_pisteet,
                                                                 font=self.ui.perusFontti, fill=fonttiVari)
                        self.ui.kierrosPisteet[krs].append(temp_tx)

            # tämä for -loop tulostaa kierroslyhenteet
            y_temp = ekaKierrosYLocation
            for item in kierrosLyhenne:
                temp_tx = self.ui.rootCanvas.create_text(10, y_temp, anchor='w', text=item,
                                                         font=self.ui.perusFontti, fill=fonttiVari)
                self.ui.kierrosLyhenneText.append(temp_tx)
                y_temp += fonttiKokoIso

            # ja lopuksi kaikki kertaalleen tulostettavat
            self.ui.kierrosNimiNyt = self.ui.rootCanvas.create_text(600, 600, text=kierros[kierrosNumero],
                                                                    font=self.ui.isoFontti, fill=fonttiVari)
            self.ui.jakajanMerkki = self.ui.rootCanvas.create_text(10, kokoPisteMarginaali + fonttiKokoIso, text='Ⓙ',
                                                                   font=self.ui.J_Fontti, fill=fonttiVari)
            self.ui.ohjeTeksti = self.ui.rootCanvas.create_text(600, 650, text='Ohjeet painamalla F1',
                                                                font=self.ui.perusFontti, fill=fonttiVari)
            self.ui.versioTeksti = self.ui.rootCanvas.create_text(versioTekstiX, versioTekstiY, text=versioNumero,
                                                                  font=self.ui.verFontti, fill=fonttiVari)
            self.ui.text_Kokopiste = self.ui.rootCanvas.create_text(vasenMarginaali, kokoPisteMarginaali, anchor='w',
                                                                    text='Kokonaispisteet:', font=self.ui.perusFontti,
                                                                    fill=fonttiVari)
            self.ui.virhe_teksti = self.ui.rootCanvas.create_text(virheenSijaintiX, virheenSijaintiY, text='',
                                                                  font=self.ui.isoFontti, fill='red')

            # kun kaikki elementit on luotu, varmistetaan pelaajien järjestys pisteiden_laskenta -funktiolla
            # ja elementtien paikka scale_objects -funktiolla
            self.ui.pisteiden_laskenta()
            self.ui.scale_objects()
            self.destroy()
        except FileNotFoundError:
            mb.showinfo('Virhe latauksessa', 'Tiedostoa ei löytynyt')
            self.lift()

    def tallenna_peli(self, tiedosto):
        Tallennettava_tiedosto = {
            'pelaaja': pelaaja,
            'pelaajaMaara': pelaajaMaara,
            'kierrosNumero': kierrosNumero,
            'valittuKierros': valittuKierros,
            'valintaSijaintiX': valintaSijaintiX,
            'valintaSijaintiY': valintaSijaintiY,
            'jakaja': jakaja,
            'sarakkeenLeveys': sarakkeenLeveys,
            'valittu': valittu
        }

        if tiedosto != 'auto':
            tallennuksen_nimi = tkinter.simpledialog.askstring('tallennuksen nimi', 'Anna tallennukselle nimi:')
            if tallennuksen_nimi:
                Tallennettava_tiedosto['tallennuksen_nimi'] = tallennuksen_nimi
                tallennusNimi[tiedosto] = tallennuksen_nimi
            else:
                Tallennettava_tiedosto['tallennuksen_nimi'] = ''
                tallennusNimi[tiedosto] = f'Nimetön {tiedosto}'
        else:
            Tallennettava_tiedosto['tallennuksen_nimi'] = 'autotallennus'

        tiedosto_nimi = f'saves/save_{tiedosto}.json'
        with open(tiedosto_nimi, 'w') as f:
            dump(Tallennettava_tiedosto, f)
        f.close()


        if self is not None:
            mb.showinfo('Tallennus onnistui', 'tiedosto tallennettu onnistuneesti')
            self.tallennusLabels[tiedosto].config(text=tallennuksen_nimi)


class PisteenlaskijaUI(Frame):
    # Käyttöliittymä CLASS, jonka sisällä luodaan visuaalinen kokonaisuus
    def __init__(self, master=None):
        # __init__ on pää funktio classin sisällä, joka suoritetaan automaattisesti
        # Ensimmäisenä luodaan tärkeimmät muuttujat ja
        super().__init__(master=master)
        self.master = master
        self.settings_window = None
        self.manual_window = None
        self.lataa_tallenna = None
        # print(fonttikansio)
        self.perusFontti = Font(file='media/SpecialElite-Regular.ttf', family=fontti, size=fonttiKoko)
        self.isoFontti = Font(family=fontti, size=fonttiKokoIso)
        self.pieniFontti = Font(family=fontti, size=fonttiKokoPieni)
        self.verFontti = Font(family=fontti, size=fonttiKokoVer)
        self.J_Fontti = Font(family=fontti, size=fonttiKokoJ)
        self.kierrosLyhenneText = []  # Tämä on kierros teksti-objektien säilömiseen tarkoitettu array
        self.pelaajaText = []  # Tämä on kokonaispisteissä näkyvien pelaajien nimien teksti objetien säilömiseen
        self.pelaajaNimi = []  # Tämä on ylhäällä nimirivillä olevia teksti-objekteja varten
        self.kierrosPisteet = []
        self.kokoPisteTeksti = []
        for i_temp in range(9):
            self.kierrosPisteet.append([])
        # print(self.kierrosPisteet)

        # ladataan ja muokataan taustakuva ikkunaan
        self.taustakuva_original = Image.open("media/tausta.bmp")
        self.taustakuva_resized = self.taustakuva_original.resize((ikkunaXScale, ikkunaYScale),
                                                                  Image.Resampling.LANCZOS)
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)
        # HUOM! RootCanvas sisältää myös tekstiobjektit
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
            self.kierrosLyhenneText.append(text)
            y_temp += fonttiKokoIso

        self.kierrosNimiNyt = self.rootCanvas.create_text(600, 600, text=kierros[0],
                                                          font=self.isoFontti, fill=fonttiVari)
        self.jakajanMerkki = self.rootCanvas.create_text(10, kokoPisteMarginaali + fonttiKokoIso, text='Ⓙ',
                                                         font=self.J_Fontti, fill=fonttiVari)
        self.ohjeTeksti = self.rootCanvas.create_text(600, 650, text='Ohjeet painamalla F1',
                                                      font=self.perusFontti, fill=fonttiVari)
        self.versioTeksti = self.rootCanvas.create_text(versioTekstiX, versioTekstiY, text=versioNumero,
                                                        font=self.verFontti, fill=fonttiVari)
        self.text_Kokopiste = self.rootCanvas.create_text(vasenMarginaali, kokoPisteMarginaali,
                                                          anchor="w", text="Kokonaispisteet:", font=self.perusFontti,
                                                          fill=fonttiVari)
        self.virhe_teksti = self.rootCanvas.create_text(500, 400, text='', font=self.isoFontti, fill='red')

        # Varmistetaan onko jotain näppäintä painettu
        # ja jos on mennään "painettu" -funktiossa varmistamaan mitä sitten tehdään
        master.bind('<KeyPress>', self.painettu)
        master.bind('<Button-1>', self.hiiren_valinta)

        self.rootCanvas.pack()
        self.pack()
        # Jos ikkunan koko muuttuu, niin skaalataan objektit muuttuneen ikkunan mukaiseksi
        master.bind("<Configure>", self.scale_objects)

    def lopeta_peli(self):
        self.master.destroy()

    def show_settings(self):
        # print("olet asetuksissa")
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = AsetuksetIkkuna(self.master)
        else:
            self.settings_window.destroy()
            return

    def show_lataa_tallenna(self):
        if self.lataa_tallenna is None or not self.lataa_tallenna.winfo_exists():
            self.lataa_tallenna = TallennusLatausIkkuna(self.master, self)
        else:
            self.lataa_tallenna.destroy()

    def show_manual(self):
        if self.manual_window is None or not self.manual_window.winfo_exists():
            self.manual_window = OhjeIkkuna(self.master)
        else:
            self.manual_window.destroy()

    def painettu(self, event=None):

        # varmistetaan mitä on painettu
        painallus = event.keysym
        kirjain = event.char
        # print(painallus)
        global valittu, valintaSijaintiY, valintaSijaintiX, pelaaja, valittuKierros, kierrosNumero

        painallus_valinnat = {
            'Right': self.liiku_oikealle,
            'Tab': self.liiku_oikealle,
            'Left': self.liiku_vasemmalle,
            'Down': self.liiku_alas,
            'Up': self.liiku_ylos,
            'F9': self.show_settings,
            'F1': self.show_manual,
            'F4': self.show_lataa_tallenna,
            'Return': self.seuraava_kierros,
            'KP_Enter': self.seuraava_kierros,
            'edit': self.edit_pelaaja_nimi,
            'Escape': self.lopeta_peli
        }

        if painallus in painallus_valinnat:
            painallus_valinnat[painallus]()
            if painallus != 'Escape':
                self.scale_objects()
        else:
            self.edit_pelaaja_nimi(kirjain)

    @staticmethod
    def liiku_oikealle():
        global valintaSijaintiX, sarakkeenLeveys, valittu
        valintaSijaintiX += sarakkeenLeveys
        valittu += 1
        if valittu > pelaajaMaara:
            valintaSijaintiX = sijaintiXOletus
            valittu = 0

    @staticmethod
    def liiku_vasemmalle():
        global valintaSijaintiX, valittu
        valintaSijaintiX = valintaSijaintiX - sarakkeenLeveys
        valittu = valittu - 1
        if valittu < 0:
            valintaSijaintiX = sijaintiXOletus + (pelaajaMaara * sarakkeenLeveys)
            valittu = pelaajaMaara

    @staticmethod
    def liiku_ylos():
        global valittuKierros, valintaSijaintiY, kierrosNumero, jakaja
        if kierrosNumero == 0:
            jakaja = jakaja - 1
            if jakaja < 0:
                jakaja = pelaajaMaara
            for item in range(len(pelaaja)):
                if item == jakaja:
                    pelaaja[item]['jakaja'] = True
                else:
                    pelaaja[item]['jakaja'] = False
        elif kierrosNumero < 9:
            valittuKierros = valittuKierros - 1
            valintaSijaintiY = valintaSijaintiY - fonttiKokoIso
            if valittuKierros < 1:
                valittuKierros = kierrosNumero
                valintaSijaintiY = sijaintiYOletus + (kierrosNumero * fonttiKokoIso)
        else:
            valittuKierros = valittuKierros - 1
            valintaSijaintiY = valintaSijaintiY - fonttiKokoIso
            if valittuKierros < 1:
                valittuKierros = 8
                valintaSijaintiY = sijaintiYOletus + (8 * fonttiKokoIso)

    @staticmethod
    def liiku_alas():
        global valittuKierros, valintaSijaintiY, kierrosNumero, jakaja, pelaajaMaara
        if kierrosNumero == 0:
            jakaja += 1
            if jakaja > pelaajaMaara:
                jakaja = 0
            for item in range(len(pelaaja)):
                if item == jakaja:
                    pelaaja[item]['jakaja'] = True
                else:
                    pelaaja[item]['jakaja'] = False
        elif kierrosNumero < 9:
            valittuKierros += 1
            valintaSijaintiY += fonttiKokoIso
            if valittuKierros > kierrosNumero:
                valittuKierros = 1
                valintaSijaintiY = sijaintiYOletus + fonttiKokoIso
        else:
            valittuKierros += 1
            valintaSijaintiY += fonttiKokoIso
            if valittuKierros > 8:
                valittuKierros = 1
                valintaSijaintiY = sijaintiYOletus + fonttiKokoIso

    def edit_pelaaja_nimi(self, kirjain):
        global pelaaja, valittuKierros, valittu

        if valittuKierros == 0:
            if kirjain == "\b":
                temp_nimi = pelaaja[valittu]['nimi'][:-1]
            else:
                temp_nimi = pelaaja[valittu]['nimi'] + kirjain
                # print(len(temp_nimi))
                if len(temp_nimi) > 12:
                    temp_nimi = temp_nimi[:-1]

            pelaaja[valittu]['nimi'] = temp_nimi
            self.rootCanvas.itemconfig(self.pelaajaText[valittu], text=temp_nimi)
            self.rootCanvas.itemconfig(self.pelaajaNimi[valittu], text=temp_nimi)
            # print(temp_nimi)
        else:
            if kirjain == "\b":
                temp_pisteet = str(pelaaja[valittu]['pisteet'][valittuKierros - 1])[:-1]
                # if not temp_pisteet:
                # temp_pisteet = '0'

            elif kirjain.isdigit():
                temp_pisteet = str(pelaaja[valittu]['pisteet'][valittuKierros - 1]) + kirjain
            else:
                return

            pelaaja[valittu]['pisteet'][valittuKierros - 1] = temp_pisteet
            self.rootCanvas.itemconfig(self.kierrosPisteet[int(valittuKierros)][int(valittu)], text=temp_pisteet)
            if valittuKierros < kierrosNumero:
                self.pisteiden_laskenta()
            # print(pelaaja[valittu], valittuKierros)

    def hiiren_valinta(self, event):
        global valittu, valittuKierros, valintaSijaintiY, valintaSijaintiX, jakaja, pelaaja
        hiiri_x = event.x
        hiiri_y = event.y
        ikkuna_x = self.master.winfo_width()
        ikkuna_y = self.master.winfo_height()
        sijainti_x_oletus_scaled = ikkuna_x * (sijaintiXOletus / ikkunaXScale)
        sijainti_y_oletus_scaled = ikkuna_y * ((sijaintiYOletus - fonttiKokoIso) / ikkunaYScale)
        fontti_koko_iso_scaled = ikkuna_y * (fonttiKokoIso / ikkunaYScale)
        sarakkeen_leveys_scaled = ikkuna_x * (sarakkeenLeveys / ikkunaXScale)
        koko_piste_marginaali_scaled = ikkuna_y * ((kokoPisteMarginaali + (fonttiKokoIso / 2)) / ikkunaYScale)
        vasen_koko_piste_marginaali_scaled = ikkuna_x * (vasenKokoPisteMarginaali / ikkunaXScale)

        if hiiri_x > sijainti_x_oletus_scaled and koko_piste_marginaali_scaled > hiiri_y > sijainti_y_oletus_scaled:
            # print('Olet pistetaulussa')
            temp_x = sijainti_x_oletus_scaled + sarakkeen_leveys_scaled
            for int in range(pelaajaMaara + 1):
                if hiiri_x < temp_x:
                    # print('olet pelaajan ' + str(int) + ' kohdalla')
                    temp_y = sijainti_y_oletus_scaled + fontti_koko_iso_scaled
                    for kierros_int in range(kierrosNumero + 1):
                        if hiiri_y < temp_y:
                            # print('olet kierroksen ' + str(kierros_int) + ' kohdalla')
                            valittu = int
                            valittuKierros = kierros_int
                            valintaSijaintiX = sijaintiXOletus + (valittu * sarakkeenLeveys)
                            valintaSijaintiY = sijaintiYOletus + (valittuKierros * fonttiKokoIso)
                            self.scale_objects()
                            break
                        else:
                            temp_y += fontti_koko_iso_scaled
                    break
                else:
                    temp_x += sarakkeen_leveys_scaled
        elif hiiri_x < vasen_koko_piste_marginaali_scaled and hiiri_y > koko_piste_marginaali_scaled:
            # print('olet määrittämässä jakajaa')
            temp_y = koko_piste_marginaali_scaled + fontti_koko_iso_scaled
            for int in range(pelaajaMaara + 1):
                if hiiri_y < temp_y:
                    pelaajan_nimi = self.rootCanvas.itemcget(self.pelaajaText[int], 'text')
                    for item in range(len(pelaaja)):
                        if pelaaja[item]['nimi'] == pelaajan_nimi:
                            jakaja = item
                    # print('olet jakaja paikalla ' + str(int))
                    for item in range(len(pelaaja)):
                        if item == jakaja:
                            pelaaja[item]['jakaja'] = True
                        else:
                            pelaaja[item]['jakaja'] = False
                    self.scale_objects()
                    break
                else:
                    temp_y += fontti_koko_iso_scaled

    def seuraava_kierros(self):

        global kierrosNumero, pelaaja, pelaajaMaara, valintaSijaintiX, valintaSijaintiY, sarakkeenLeveys
        global valittuKierros, virhe, jakaja

        self.virheen_tarkistus()
        if virhe:
            # print("virhe on: " + str(virhe))
            self.virheen_tulostus(virhe)

        if virhe == 0:
            self.rootCanvas.itemconfig(self.virhe_teksti, text='')
            if kierrosNumero < 9:
                self.rootCanvas.itemconfig(self.kierrosNimiNyt, text=kierros[kierrosNumero + 1])
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
                # print(kierros_numero_oikea, pelaaja[0]['pisteet'][0])
                jakaja_loydetty = False
                for item in range(len(pelaaja)):
                    temp_item = self.rootCanvas.create_text(x_temp, y_temp, text='',
                                                            font=self.perusFontti, fill=fonttiVari)
                    temp_item2 = self.rootCanvas.create_text(vasenMarginaali, kokoPisteMarginaali, text='',
                                                             font=self.perusFontti, fill=fonttiVari)
                    self.kierrosPisteet[kierrosNumero].append(temp_item)
                    self.kokoPisteTeksti.append(temp_item2)
                    x_temp += sarakkeenLeveys
                    if pelaaja[item]['jakaja']:
                        jakaja_loydetty = True
                if not jakaja_loydetty:
                    pelaaja[0]['jakaja'] = True

            elif kierrosNumero < 9:
                kierrosNumero += 1
                if kierrosNumero < 9:
                    # print(self.kierrosPisteet)
                    valintaSijaintiY = fonttiKokoIso * kierrosNumero + sijaintiYOletus
                    valittuKierros = kierrosNumero
                    x_temp = sijaintiXOletus + (sarakkeenLeveys / 2)
                    y_temp = ekaKierrosYLocation + (fonttiKokoIso * kierrosNumero)
                    jakaja += 1
                    if jakaja > pelaajaMaara:
                        jakaja = 0
                    for item in range(len(pelaaja)):
                        temp_item = self.rootCanvas.create_text(x_temp, y_temp, text='',
                                                                font=self.perusFontti, fill=fonttiVari)
                        self.kierrosPisteet[kierrosNumero].append(temp_item)
                        if not pelaaja[item]['pisteet'][kierrosNumero - 2]:
                            self.rootCanvas.itemconfig(self.kierrosPisteet[kierrosNumero - 1][item], text='0')
                        if item == jakaja:
                            pelaaja[item]['jakaja'] = True
                        else:
                            pelaaja[item]['jakaja'] = False
                        x_temp += sarakkeenLeveys
                elif kierrosNumero == 9:
                    for item in range(len(pelaaja)):
                        if not pelaaja[item]['pisteet'][kierrosNumero - 2]:
                            self.rootCanvas.itemconfig(self.kierrosPisteet[kierrosNumero - 1][item], text='0')
                self.pisteiden_laskenta()
                TallennusLatausIkkuna.tallenna_peli(None, 'auto')
            else:
                self.uusi_peli()

    def jarjesta_pelaajat(self):
        global pelaaja
        sorted_pelaaja = sorted(pelaaja, key=lambda x: x['kokonaisPisteet'])
        for sija, item in enumerate(sorted_pelaaja, start=1):
            item['sijoitus'] = str(sija)
        # print(pelaaja, sorted_pelaaja)

        for item in range(len(self.pelaajaText)):
            self.rootCanvas.itemconfig(self.pelaajaText[item], text=sorted_pelaaja[item]['nimi'])
            self.rootCanvas.itemconfig(self.kokoPisteTeksti[item], text=sorted_pelaaja[item]['kokonaisPisteet'])

    def pisteiden_laskenta(self):
        # kokonaispisteiden laskenta
        # global pelaaja

        for item in pelaaja:
            koko_piste = 0
            for item2 in range(kierrosNumero - 1):
                if item['pisteet'][item2]:
                    koko_piste += int(item['pisteet'][item2])
            item['kokonaisPisteet'] = str(koko_piste)
        self.jarjesta_pelaajat()

    def uusi_peli(self):
        global pelaajaMaara, pelaaja, kierrosNumero, valittuKierros, valintaSijaintiY, valintaSijaintiX
        global jakaja, sarakkeenLeveys, valittu
        print('tähän tulisi uuden pelin koodi')
        print('Kyllä tykkään, selkeä ja helppolukuinen sekä hyvin kommentoitu :) T:Cave')

        pelaajaMaara = 5
        kierrosNumero = 0
        valittuKierros = 0
        valintaSijaintiX = sijaintiXOletus
        valintaSijaintiY = sijaintiYOletus
        sarakkeenLeveys = (ikkunaXScale - sijaintiXOletus) / (pelaajaMaara + 1)
        valittu = 0
        jakaja = 0

        pelaaja_nimet_temp = [item['nimi'] for item in pelaaja]
        for item in range(4):
            pelaaja_nimet_temp.append('')
        pelaaja = []
        for player in range(pelaajaMaara + 1):
            if pelaaja_nimet_temp[player]:
                if player == 0:
                    temp_pelaaja = {'nimi': pelaaja_nimet_temp[player], 'pisteet': ['', '', '', '', '', '', '', ''],
                                    'jakaja': True}
                else:
                    temp_pelaaja = {'nimi': pelaaja_nimet_temp[player], 'pisteet': ['', '', '', '', '', '', '', ''],
                                    'jakaja': False}
            else:
                if player == 0:
                    temp_pelaaja = {'nimi': pelaaja_nimet_temp[player], 'pisteet': ['', '', '', '', '', '', '', ''],
                                    'jakaja': True}
                else:
                    temp_pelaaja = {'nimi': pelaaja_nimet_temp[player], 'pisteet': ['', '', '', '', '', '', '', ''],
                                    'jakaja': False}
            pelaaja.append(temp_pelaaja)
        self.rootCanvas.delete('all')
        self.pelaajaText = []
        self.pelaajaNimi = []
        self.kierrosLyhenneText = []
        self.kierrosPisteet = []
        self.kokoPisteTeksti = []
        for i_temp in range(9):
            self.kierrosPisteet.append([])

        self.muokattu_tausta = self.rootCanvas.create_image(0, 0, anchor='nw', image=self.uusi_tausta)
        self.valintaViiva = self.rootCanvas.create_line(valintaSijaintiX, valintaSijaintiY,
                                                        valintaSijaintiX + sarakkeenLeveys, valintaSijaintiY,
                                                        fill=fonttiVari, width=2)
        for item in range(pelaajaMaara + 1):
            temp_text = self.rootCanvas.create_text(vasenMarginaali + 30, 50, anchor="w", text=pelaaja[item]['nimi'],
                                                    font=self.perusFontti, fill=fonttiVari)
            self.pelaajaText.append(temp_text)

        x_temp = valintaSijaintiX + (sarakkeenLeveys / 2)
        for item in range(pelaajaMaara + 1):
            temp_text = self.rootCanvas.create_text(x_temp, valintaSijaintiY - fonttiKoko, text=pelaaja[item]['nimi'],
                                                    font=self.perusFontti, fill=fonttiVari)
            x_temp += sarakkeenLeveys
            self.pelaajaNimi.append(temp_text)

        y_temp = ekaKierrosYLocation
        for it in kierrosLyhenne:
            text = self.rootCanvas.create_text(10, y_temp, anchor="w", text=it, font=self.perusFontti, fill=fonttiVari)
            self.kierrosLyhenneText.append(text)
            y_temp += fonttiKokoIso

        self.kierrosNimiNyt = self.rootCanvas.create_text(600, 600, text=kierros[0],
                                                          font=self.isoFontti, fill=fonttiVari)
        self.jakajanMerkki = self.rootCanvas.create_text(10, kokoPisteMarginaali + fonttiKokoIso, text='Ⓙ',
                                                         font=self.J_Fontti, fill=fonttiVari)
        self.ohjeTeksti = self.rootCanvas.create_text(600, 650, text='Ohjeet painamalla F1',
                                                      font=self.perusFontti, fill=fonttiVari)
        self.versioTeksti = self.rootCanvas.create_text(versioTekstiX, versioTekstiY, text=versioNumero,
                                                        font=self.verFontti, fill=fonttiVari)
        self.text_Kokopiste = self.rootCanvas.create_text(vasenMarginaali, kokoPisteMarginaali,
                                                          anchor="w", text="Kokonaispisteet:", font=self.perusFontti,
                                                          fill=fonttiVari)
        self.virhe_teksti = self.rootCanvas.create_text(500, 400, text='', font=self.isoFontti, fill='red')

        self.scale_objects()

    @staticmethod
    def virheen_tarkistus():

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
            pelaaja_temp = [item['nimi'] for item in pelaaja]  # 1
            pelaaja_temp = [item for item in pelaaja_temp if item]  # 2
            pelaaja_temp_set = set(pelaaja_temp)  # 3
            if len(pelaaja_temp) > len(pelaaja_temp_set):  # 4
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
            kierros_pisteet_temp = [item['pisteet'] for item in pelaaja]  # 1
            kierros_pisteet_temp = [[row[z] for row in kierros_pisteet_temp] for z
                                    in range(len(kierros_pisteet_temp[0]))]  # 2
            kierros_pisteet_temp = kierros_pisteet_temp[:kierrosNumero]  # 3
            # print(kierros_pisteet_temp)

            for kierros_nyt in kierros_pisteet_temp:  # 4
                voittaja = sum(item == '' or item == '0' for item in kierros_nyt)
                # print(voittaja)
                if voittaja != 1:
                    virhe = 1
                for piste in kierros_nyt:  # 5
                    # print(piste)
                    if piste == '':
                        piste = 0
                    if int(piste) > 200 or int(piste) == 1:
                        virhe = 2

    def virheen_tulostus(self, virhe_numero):

        valinnat = {
            1: 'Et ole syöttänyt kaikille pisteitä',
            2: 'Tarkista pisteet',
            3: 'Pelaajia on liian vähän',
            4: 'Nimet ovat samanlaiset'
        }
        # print("olen tulostuksessa ja virhe_numero on " + str(virhe_numero) + " ja teksti on" + valinnat[virhe_numero])
        if virhe_numero in valinnat:
            self.rootCanvas.itemconfig(self.virhe_teksti, text=valinnat[virhe_numero])

    @staticmethod
    def on_jakaja(pelaaja_nimi):
        jakaja_func = False
        for item in pelaaja:
            if item['nimi'] == pelaaja_nimi:
                jakaja_func = item['jakaja']
        return jakaja_func

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
        fontti_koko_ver_scaled = ikkuna_korkeus_scaled * (fonttiKokoVer / ikkunaYScale)
        valinta_sijainti_x_scaled = ikkuna_leveys_scaled * (valintaSijaintiX / ikkunaXScale)
        valinta_sijainti_y_scaled = ikkuna_korkeus_scaled * (valintaSijaintiY / ikkunaYScale)
        nimi_sijainti_y_scaled = ikkuna_korkeus_scaled * (sijaintiYOletus / ikkunaYScale)
        sarakkeen_leveys_scaled = ikkuna_leveys_scaled * (sarakkeenLeveys / ikkunaXScale)
        sijainti_x_oletus_scaled = ikkuna_leveys_scaled * (sijaintiXOletus / ikkunaXScale)
        virheen_sijainti_x_scaled = ikkuna_leveys_scaled * (virheenSijaintiX / ikkunaXScale)
        virheen_sijainti_y_scaled = ikkuna_korkeus_scaled * (virheenSijaintiY / ikkunaYScale)
        kierros_nimi_x_scaled = ikkuna_leveys_scaled * (kierrosNimiX / ikkunaXScale)
        kierros_nimi_y_scaled = ikkuna_korkeus_scaled * (kierrosNimiY / ikkunaYScale)
        ohje_teksti_x_scaled = ikkuna_leveys_scaled * (ohjeTekstiX / ikkunaXScale)
        ohje_teksti_y_scaled = ikkuna_korkeus_scaled * (ohjeTekstiY / ikkunaYScale)
        jakajan_merkki_x_scaled = ikkuna_leveys_scaled * (fonttiKokoVer / ikkunaXScale)
        versio_teksti_x_scaled = ikkuna_leveys_scaled * (versioTekstiX / ikkunaXScale)
        versio_teksti_y_scaled = ikkuna_korkeus_scaled * (versioTekstiY / ikkunaYScale)
        fontti_koko_j_scaled = ikkuna_korkeus_scaled * (fonttiKokoJ / ikkunaYScale)

        # Update font -objects to correct size:
        self.perusFontti = Font(family=fontti, size=int(fontti_koko_scaled))
        self.isoFontti = Font(family=fontti, size=int(fontti_koko_iso_scaled))
        self.pieniFontti = Font(family=fontti, size=int(fontti_koko_pieni_scaled))
        self.verFontti = Font(family=fontti, size=int(fontti_koko_ver_scaled))
        self.J_Fontti = Font(family=fontti, size=int(fontti_koko_j_scaled))

        # update texts based of the updated variables above
        y_temp = eka_kierros_y_location_scaled
        for item in range(len(self.kierrosLyhenneText)):
            self.rootCanvas.coords(self.kierrosLyhenneText[item], vasen_marginaali_scaled, y_temp)
            self.rootCanvas.itemconfig(self.kierrosLyhenneText[item], font=self.pieniFontti)
            y_temp += fontti_koko_iso_scaled

        y_temp = koko_piste_marginaali_scaled + fontti_koko_iso_scaled
        for item in range(len(self.pelaajaText)):
            self.rootCanvas.coords(self.pelaajaText[item], vasen_kokopiste_nimi_marginaali_scaled, y_temp)
            self.rootCanvas.itemconfig(self.pelaajaText[item], font=self.perusFontti)
            if kierrosNumero == 0:
                if jakaja == item:
                    self.rootCanvas.coords(self.jakajanMerkki, jakajan_merkki_x_scaled, y_temp)
                    self.rootCanvas.itemconfig(self.jakajanMerkki, font=self.J_Fontti)
            else:
                if self.on_jakaja(self.rootCanvas.itemcget(self.pelaajaText[item], 'text')):
                    self.rootCanvas.coords(self.jakajanMerkki, jakajan_merkki_x_scaled, y_temp)
                    self.rootCanvas.itemconfig(self.jakajanMerkki, font=self.J_Fontti)
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
            self.rootCanvas.itemconfig(item, font=self.perusFontti)
            y_temp += fontti_koko_iso_scaled

        self.rootCanvas.coords(self.kierrosNimiNyt, kierros_nimi_x_scaled, kierros_nimi_y_scaled)
        self.rootCanvas.itemconfig(self.kierrosNimiNyt, font=self.isoFontti)
        self.rootCanvas.coords(self.ohjeTeksti, ohje_teksti_x_scaled, ohje_teksti_y_scaled)
        self.rootCanvas.itemconfig(self.ohjeTeksti, font=self.perusFontti)
        self.rootCanvas.coords(self.valintaViiva, valinta_sijainti_x_scaled, valinta_sijainti_y_scaled,
                               valinta_sijainti_x_scaled + sarakkeen_leveys_scaled, valinta_sijainti_y_scaled)
        self.rootCanvas.coords(self.text_Kokopiste, vasen_marginaali_scaled, koko_piste_marginaali_scaled)
        self.rootCanvas.itemconfig(self.text_Kokopiste, font=self.perusFontti)
        self.rootCanvas.coords(self.virhe_teksti, virheen_sijainti_x_scaled, virheen_sijainti_y_scaled)
        self.rootCanvas.itemconfig(self.virhe_teksti, font=self.isoFontti)
        self.rootCanvas.coords(self.versioTeksti, versio_teksti_x_scaled, versio_teksti_y_scaled)
        self.rootCanvas.itemconfig(self.versioTeksti, font=self.verFontti)
        self.rootCanvas.configure(height=ikkuna_korkeus_scaled, width=ikkuna_leveys_scaled)
        self.taustakuva_resized = self.taustakuva_original.resize((ikkuna_leveys_scaled, ikkuna_korkeus_scaled),
                                                                  Image.Resampling.LANCZOS)
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)
        self.rootCanvas.itemconfig(self.muokattu_tausta, image=self.uusi_tausta)


# super simple window creation, which get all objects from Pisteenlaskija -class
root = Tk()
tallennus_nimet()
root.title("Sanghai Pisteenlaskija")
root.geometry("1280x720")
pelaaja = []
for i in range(pelaajaMaara + 1):
    if i == 0:
        temp = {'nimi': '', 'pisteet': ['', '', '', '', '', '', '', ''], 'jakaja': True}
    else:
        temp = {'nimi': '', 'pisteet': ['', '', '', '', '', '', '', ''], 'jakaja': False}
    pelaaja.append(temp)

PisteenlaskijaUI(root)
root.mainloop()
