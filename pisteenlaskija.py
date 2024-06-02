import datetime
import functools
import tkinter.simpledialog
import tkinter as tk
from PIL import ImageTk, Image
import globals as gl
import requests
from tkinter import messagebox as mb
from json import load, dump, dumps
# from os import path as os.path
import os.path
# import pyglet
from tkextrafont import Font
from typing import Optional

'''
TODO List:
- Asetukset
- Serveri yhteys
- Turnaus versio muokkaukset
- Virhe ilmoitukset ja tunnistukset esim pisteistä
    - yhteydessä palvelimeen virhe (tehdään vasta, kun päästään serveriyhteyden koodaukseen)
    
'''

# pelaajaMaara = 6
versioNumero = 'Versio 3.0-beta'

# tkextrafont.TkExtraFont.chdir = resource_path()


# pyglet.font.add_file('media/SpecialElite-Regular.ttf')

def tallennus_nimet() -> None:
    for tallennus in range(gl.tallennuspaikat):
        tiedosto_nimi = f'saves/save_{tallennus}.json'
        if os.path.isfile(tiedosto_nimi):
            with open(tiedosto_nimi, 'r') as f:
                haettu_data = load(f)
            gl.tallennusNimi.append(haettu_data['tallennuksen_nimi'])
            f.close()
        else:
            gl.tallennusNimi.append('')
    # print(gl.tallennusNimi)


def lue_asetukset() -> dict:
    asetus_local: dict = {'fonttiVari': gl.fonttiVari, 'fonttiKoko': 100, 'datanLahetys': True}
    with open('media/settings.json') as tiedosto:
        asetukset_tiedosto = load(tiedosto)
    asetus_local['fonttiVari'] = asetukset_tiedosto['fonttiVari']
    asetus_local['fonttiKoko'] = asetukset_tiedosto['fonttiKoko']
    asetus_local['datanLahetys'] = asetukset_tiedosto['datanLahetys']
    return asetus_local


class AsetuksetIkkuna(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Settings")
        # self.overrideredirect(True)
        self.geometry("300x200")

        self.frame_grid = tk.Frame(self)
        self.frame_labels = tk.Frame(self)
        self.checkbox_setting_datanlahetys_var = tk.BooleanVar()

        self.label_setting_fonttivari = tk.Label(self.frame_grid, text="Fonttiväri")
        self.label_setting_fonttivari.grid(row=0, column=0)
        self.entry_setting_fonttivari = tk.Entry(self.frame_grid)
        self.entry_setting_fonttivari.insert(0, asetus['fonttiVari'])
        self.entry_setting_fonttivari.grid(row=0, column=1)
        self.label_setting_fonttikoko = tk.Label(self.frame_grid, text="fonttiKoko:")
        self.label_setting_fonttikoko.grid(row=1, column=0)
        self.entry_setting_fonttikoko = tk.Entry(self.frame_grid)
        self.entry_setting_fonttikoko.insert(0, asetus['fonttiKoko'])
        self.entry_setting_fonttikoko.grid(row=1, column=1)
        self.label_setting_datanlahetys = tk.Label(self.frame_grid, text="Salli pisteiden tilastointi")
        self.label_setting_datanlahetys.grid(row=2, column=0)
        self.checkbox_setting_datanlahetys = tk.Checkbutton(self.frame_grid,
                                                            variable=self.checkbox_setting_datanlahetys_var)
        self.checkbox_setting_datanlahetys_var.set(asetus['datanLahetys'])
        self.checkbox_setting_datanlahetys.grid(row=2, column=1)

        self.save_button = tk.Button(self.frame_grid, text='Tallenna', command=self.tallenna_asetukset)
        self.save_button.grid(row=3, column=1)

        # tk.Label(self.frame_labels, text='Tämä osio ei tee vielä mitään').pack()
        # tk.Label(self.frame_labels, text='Olethan kärsivällinen, rakennamme kovaa kyytiä').pack()
        self.frame_grid.pack()
        self.frame_labels.pack()

    def tallenna_asetukset(self) -> None:
        with open('media/settings.json', 'r') as f:
            local_asetus = load(f)

        asetus['fonttiVari'] = local_asetus['fonttiVari'] = self.entry_setting_fonttivari.get() or gl.fonttiVari

        local_fontti_koko: int = int(self.entry_setting_fonttikoko.get())
        try:
            local_fontti_koko = min(max(local_fontti_koko, 10), 200)
        except ValueError:
            local_fontti_koko: int = 100

        asetus['fonttiKoko'] = local_asetus['fonttiKoko'] = local_fontti_koko
        asetus['datanLahetys'] = local_asetus['datanLahetys'] = self.checkbox_setting_datanlahetys_var.get()

        with open('media/settings.json', 'w') as f:
            dump(local_asetus, f)
        self.destroy()


class OhjeIkkuna(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Ohjeet")
        self.geometry("600x500")

        self.frame = tk.Frame(self)
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
            'Saat ohjelman asetukset näkyviin painamalla "F9"'
            'Laita pelatun kierroksen pisteet ja siirry',
            'seuraavalle kierrokselle painamalla "Enter"',
            ' ',
            'Poistu ohjeista painamalla "F1"',
            'Tallenna tai lataa peli painamalla "F4"',
            'Poistu ohjelmasta painamalla "ESC"'
        ]

        for label_number, label in enumerate(self.labels):
            self.L = tk.Label(self.frame, text=label)
            self.L.grid(row=label_number, column=0, sticky='nsew')

        self.bind('<F1>', self.destroy_window)

    def destroy_window(self, *_: tk.Event) -> None:
        self.destroy()


class TallennusLatausIkkuna(tk.Toplevel):
    def __init__(self, master, main_ui):
        super().__init__(master)
        self.master = master
        self.ui = main_ui
        self.title("Tallennus ja Lataus")
        self.geometry("600x500")

        self.frame = tk.Frame(self)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')

        self.ohjeTekstit = [
            'Tallennus ja Lataus',
            ' '
            'Valitse tallennuspaikka ja sen jälkeen joko tallenna tai lataa',
            'riippuen kumman haluat tehdä',
            ' '
        ]
        for label_number, label in enumerate(self.ohjeTekstit):
            self.L = tk.Label(self.frame, text=label)
            self.L.grid(row=label_number, column=0, sticky='nsew')

        self.tallennusLabels = []
        current_row = len(self.ohjeTekstit) + 1
        for tallenus_nimi_var, tallenus_nimi_name in enumerate(gl.tallennusNimi):
            tulostus_nimi = tallenus_nimi_name if tallenus_nimi_name else f'tallennuspaikka: {tallenus_nimi_var}'
            label = tk.Label(self.frame, text=tulostus_nimi)
            label.grid(row=current_row + tallenus_nimi_var, column=0, sticky='nsew')
            tk.Button(self.frame, text='Lataa', command=functools.partial(self.lataa_peli, tallenus_nimi_var)
                      ).grid(row=current_row + tallenus_nimi_var, column=1, sticky='nsew')
            tk.Button(self.frame, text='tallenna', command=functools.partial(self.tallenna_peli,
                                                                             tiedosto=tallenus_nimi_var)
                      ).grid(row=current_row + tallenus_nimi_var, column=2, sticky='nsew')
            self.tallennusLabels.append(label)

        self.L = tk.Label(self.frame, text="autotallennuspaikka")
        self.L.grid(row=current_row + 4, column=0, sticky='nsew')
        self.L = tk.Button(self.frame, text='lataa', command=functools.partial(self.lataa_peli, 'auto'))
        self.L.grid(row=current_row + 4, column=1, sticky='nsew')

        self.bind('<F4>', self.destroy_window)

    def destroy_window(self, *_: tk.Event) -> None:
        self.destroy()

    def lataa_peli(self, tiedosto) -> None:
        global pelaaja

        # avataan tiedosto
        tiedosto_nimi = f'saves/save_{tiedosto}.json'
        try:
            with open(tiedosto_nimi, 'r') as f:
                haettu_data = load(f)

            # haetaan tiedot
            pelaaja = haettu_data['pelaaja']
            gl.pelaajaMaara = haettu_data['pelaajaMaara']
            gl.kierrosNumero = haettu_data['kierrosNumero']
            gl.valittuKierros = haettu_data['valittuKierros']
            gl.valintaSijaintiX = haettu_data['valintaSijaintiX']
            gl.valintaSijaintiY = haettu_data['valintaSijaintiY']
            gl.jakaja = haettu_data['jakaja']
            gl.sarakkeenLeveys = haettu_data['sarakkeenLeveys']
            gl.valittu = haettu_data['valittu']

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
            self.ui.valintaViiva = self.ui.rootCanvas.create_line(gl.valintaSijaintiX, gl.valintaSijaintiY,
                                                                  gl.valintaSijaintiX + gl.sarakkeenLeveys,
                                                                  gl.valintaSijaintiY,
                                                                  fill=asetus['fonttiVari'], width=2)

            # tämä for -loop tekee kaikki pelaajakohtaiset tulostukset
            x_temp = gl.sijaintiXOletus + (gl.sarakkeenLeveys / 2)
            for item in range(gl.pelaajaMaara + 1):
                temp_tx = self.ui.rootCanvas.create_text(gl.vasenMarginaali + 30, 50, anchor='w',
                                                         text=pelaaja[item]['nimi'], font=self.ui.perusFontti,
                                                         fill=asetus['fonttiVari'])
                self.ui.pelaajaText.append(temp_tx)

                temp_tx = self.ui.rootCanvas.create_text(x_temp, gl.valintaSijaintiY - gl.fonttiKoko,
                                                         text=pelaaja[item]['nimi'], font=self.ui.perusFontti,
                                                         fill=asetus['fonttiVari'], anchor='center')
                self.ui.pelaajaNimi.append(temp_tx)
                x_temp += gl.sarakkeenLeveys
                temp_tx = self.ui.rootCanvas.create_text(gl.vasenKokoPisteNimiMarginaali, gl.kokoPisteMarginaali,
                                                         text=pelaaja[item]['kokonaisPisteet'],
                                                         font=self.ui.perusFontti,
                                                         fill=asetus['fonttiVari'])
                self.ui.kokoPisteTeksti.append(temp_tx)
                for krs in range(1, gl.kierrosNumero + 1):
                    if krs < 9:
                        if pelaaja[item]['pisteet'][krs - 1] or krs == gl.kierrosNumero:
                            temp_pisteet = pelaaja[item]['pisteet'][krs - 1]
                        else:
                            temp_pisteet = '0'

                        temp_tx = self.ui.rootCanvas.create_text(200, 500, text=temp_pisteet, anchor='n',
                                                                 font=self.ui.perusFontti, fill=asetus['fonttiVari'])
                        self.ui.kierrosPisteet[krs].append(temp_tx)

            # tämä for -loop tulostaa kierroslyhenteet
            y_temp = gl.ekaKierrosYLocation
            for item in gl.kierrosLyhenne:
                temp_tx = self.ui.rootCanvas.create_text(10, y_temp, anchor='nw', text=item,
                                                         font=self.ui.perusFontti, fill=asetus['fonttiVari'])
                self.ui.kierrosLyhenneText.append(temp_tx)
                y_temp += gl.rivivali

            # ja lopuksi kaikki kertaalleen tulostettavat
            self.ui.kierrosNimiNyt = self.ui.rootCanvas.create_text(600, 600, text=gl.kierros[gl.kierrosNumero],
                                                                    font=self.ui.isoFontti, fill=asetus['fonttiVari'])
            self.ui.jakajanMerkki = self.ui.rootCanvas.create_text(10, gl.kokoPisteMarginaali + gl.rivivali, text='Ⓙ',
                                                                   font=self.ui.J_Fontti, fill=asetus['fonttiVari'])
            self.ui.ohjeTeksti = self.ui.rootCanvas.create_text(600, 650, text='Ohjeet painamalla F1',
                                                                font=self.ui.perusFontti, fill=asetus['fonttiVari'])
            self.ui.versioTeksti = self.ui.rootCanvas.create_text(gl.versioTekstiX, gl.versioTekstiY,
                                                                  text=versioNumero, font=self.ui.verFontti,
                                                                  fill=asetus['fonttiVari'])
            self.ui.text_Kokopiste = self.ui.rootCanvas.create_text(gl.vasenMarginaali, gl.kokoPisteMarginaali,
                                                                    anchor='w', text='Kokonaispisteet:',
                                                                    font=self.ui.perusFontti, fill=asetus['fonttiVari'])
            self.ui.virhe_teksti = self.ui.rootCanvas.create_text(gl.virheenSijaintiX, gl.virheenSijaintiY, text='',
                                                                  font=self.ui.isoFontti, fill='red')

            # kun kaikki elementit on luotu, varmistetaan pelaajien järjestys pisteiden_laskenta -funktiolla
            # ja elementtien paikka scale_objects -funktiolla
            self.ui.pisteiden_laskenta()
            self.ui.scale_objects()
            self.destroy()
        except FileNotFoundError:
            mb.showinfo('Virhe latauksessa', 'Tiedostoa ei löytynyt')
            self.lift()

    def tallenna_peli(self: Optional, tiedosto) -> None:
        tallennettava_tiedosto = {
            'pelaaja': pelaaja,
            'pelaajaMaara': gl.pelaajaMaara,
            'kierrosNumero': gl.kierrosNumero,
            'valittuKierros': gl.valittuKierros,
            'valintaSijaintiX': gl.valintaSijaintiX,
            'valintaSijaintiY': gl.valintaSijaintiY,
            'jakaja': gl.jakaja,
            'sarakkeenLeveys': gl.sarakkeenLeveys,
            'valittu': gl.valittu
        }
        tallennuksen_nimi = 'default'
        if tiedosto != 'auto':
            tallennuksen_nimi = tkinter.simpledialog.askstring('tallennuksen nimi', 'Anna tallennukselle nimi:')
            if tallennuksen_nimi:
                tallennettava_tiedosto['tallennuksen_nimi'] = tallennuksen_nimi
                gl.tallennusNimi[tiedosto] = tallennuksen_nimi
            else:
                tallennettava_tiedosto['tallennuksen_nimi'] = ''
                gl.tallennusNimi[tiedosto] = f'Nimetön {tiedosto}'
        else:
            tallennettava_tiedosto['tallennuksen_nimi'] = 'autotallennus'

        tiedosto_nimi = f'saves/save_{tiedosto}.json'
        with open(tiedosto_nimi, 'w') as f:
            dump(tallennettava_tiedosto, f)
        f.close()

        if self is not None:
            mb.showinfo('Tallennus onnistui', 'tiedosto tallennettu onnistuneesti')
            self.tallennusLabels[tiedosto].config(text=tallennuksen_nimi)
            self.destroy()


class PisteenlaskijaUI(tk.Frame):
    # Käyttöliittymä CLASS, jonka sisällä luodaan visuaalinen kokonaisuus
    def __init__(self, master=None):
        # __init__ on pää funktio classin sisällä, joka suoritetaan automaattisesti
        # Ensimmäisenä luodaan tärkeimmät muuttujat ja
        super().__init__(master=master)
        self.master = master
        self.settings_window = None
        self.manual_window = None
        self.lataa_tallenna = None
        self.game_id: str = self.create_gameid()
        # print(fonttikansio)
        self.perusFontti: Font = Font(file='media/SpecialElite-Regular.ttf', family=gl.fontti,
                                      size=int(gl.fonttiKoko*(asetus['fonttiKoko']/100)))
        self.isoFontti: Font = Font(family=gl.fontti, size=int(gl.fonttiKokoIso*(asetus['fonttiKoko']/100)))
        self.pieniFontti: Font = Font(family=gl.fontti, size=int(gl.fonttiKokoPieni*(asetus['fonttiKoko']/100)))
        self.verFontti: Font = Font(family=gl.fontti, size=int(gl.fonttiKokoVer*(asetus['fonttiKoko']/100)))
        self.J_Fontti: Font = Font(family=gl.fontti, size=int(gl.fonttiKokoJ*(asetus['fonttiKoko']/100)))
        self.virheFontti: Font = Font(family=gl.fontti, size=int(gl.fonttiKokoVirhe*(asetus['fonttiKoko']/100)))
        self.kierrosLyhenneText: list[int] = []  # Tämä on kierros teksti-objektien säilömiseen tarkoitettu array
        self.pelaajaText: list[int] = []  # Tämä on kokonaispisteissä näkyvien nimien teksti objetien säilömiseen
        self.pelaajaNimi: list[int] = []  # Tämä on ylhäällä nimirivillä olevia teksti-objekteja varten
        self.kierrosPisteet: list[list[int]] = []
        self.kokoPisteTeksti: list[int] = []
        for i_temp in range(9):
            self.kierrosPisteet.append([])
        # print(self.kierrosPisteet)

        # ladataan ja muokataan taustakuva ikkunaan
        self.taustakuva_original: Image = Image.open("media/tausta.bmp")
        self.taustakuva_resized: Image = self.taustakuva_original.resize((gl.ikkunaXScale, gl.ikkunaYScale),
                                                                         Image.Resampling.LANCZOS)
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)
        # HUOM! RootCanvas sisältää myös tekstiobjektit
        self.rootCanvas = tk.Canvas(self.master, width=gl.ikkunaXScale, height=gl.ikkunaYScale)
        self.muokattu_tausta = self.rootCanvas.create_image(0, 0, anchor="nw", image=self.uusi_tausta)

        self.valintaViiva: int = self.rootCanvas.create_line(gl.valintaSijaintiX, gl.valintaSijaintiY,
                                                             gl.valintaSijaintiX + gl.sarakkeenLeveys,
                                                             gl.valintaSijaintiY,
                                                             fill=asetus['fonttiVari'], width=2)

        # Luodaan teksti-objektit pelaajaText, pelaajaNimi ja kierrosText Arraytten sisälle
        for item in range(gl.pelaajaMaara + 1):
            temp_text = self.rootCanvas.create_text(gl.vasenMarginaali + 30, 50, anchor="w", text='',
                                                    font=self.perusFontti, fill=asetus['fonttiVari'])
            self.pelaajaText.append(temp_text)

        x_temp = gl.valintaSijaintiX + (gl.sarakkeenLeveys / 2)
        for item in range(gl.pelaajaMaara + 1):
            temp_text = self.rootCanvas.create_text(x_temp, gl.valintaSijaintiY - gl.fonttiKoko, text='',
                                                    anchor='center', font=self.perusFontti, fill=asetus['fonttiVari'])
            x_temp += gl.sarakkeenLeveys
            self.pelaajaNimi.append(temp_text)

        y_temp = gl.ekaKierrosYLocation
        for it in gl.kierrosLyhenne:
            text = self.rootCanvas.create_text(10, y_temp, anchor="nw", text=it,
                                               font=self.perusFontti, fill=asetus['fonttiVari'])
            self.kierrosLyhenneText.append(text)
            y_temp += gl.rivivali

        self.kierrosNimiNyt: int = self.rootCanvas.create_text(600, 600, text=gl.kierros[0],
                                                               font=self.isoFontti, fill=asetus['fonttiVari'])
        self.jakajanMerkki: int = self.rootCanvas.create_text(10, gl.kokoPisteMarginaali + gl.rivivali, text='Ⓙ',
                                                              font=self.J_Fontti, fill=asetus['fonttiVari'])
        self.ohjeTeksti: int = self.rootCanvas.create_text(600, 650, text='Ohjeet painamalla F1',
                                                           font=self.perusFontti, fill=asetus['fonttiVari'])
        self.versioTeksti: int = self.rootCanvas.create_text(gl.versioTekstiX, gl.versioTekstiY, text=versioNumero,
                                                             font=self.verFontti, fill=asetus['fonttiVari'])
        self.text_Kokopiste: int = self.rootCanvas.create_text(gl.vasenMarginaali, gl.kokoPisteMarginaali,
                                                               anchor="w", text="Kokonaispisteet:",
                                                               font=self.perusFontti,
                                                               fill=asetus['fonttiVari'])
        self.virhe_teksti: int = self.rootCanvas.create_text(500, 400, text='', font=self.virheFontti, fill='red')

        # Varmistetaan onko jotain näppäintä painettu
        # ja jos on mennään "painettu" -funktiossa varmistamaan mitä sitten tehdään
        master.bind('<KeyPress>', self.painettu)
        master.bind('<Button-1>', self.hiiren_valinta)

        self.rootCanvas.pack()
        self.pack()
        # Jos ikkunan koko muuttuu, niin skaalataan objektit muuttuneen ikkunan mukaiseksi
        master.bind("<Configure>", self.scale_objects)

    def lopeta_peli(self) -> None:
        self.master.destroy()

    def show_settings(self) -> None:
        # print("olet asetuksissa")
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = AsetuksetIkkuna(self.master)
        else:
            self.settings_window.destroy()
            return

    def show_lataa_tallenna(self) -> None:
        if self.lataa_tallenna is None or not self.lataa_tallenna.winfo_exists():
            self.lataa_tallenna = TallennusLatausIkkuna(self.master, self)
        else:
            self.lataa_tallenna.destroy()

    def show_manual(self) -> None:
        if self.manual_window is None or not self.manual_window.winfo_exists():
            self.manual_window = OhjeIkkuna(self.master)
        else:
            self.manual_window.destroy()

    def painettu(self, event=None) -> None:

        # varmistetaan mitä on painettu
        painallus: str = event.keysym
        kirjain: str = event.char

        # print(asetus['fonttiVari'])

        # Lista mitä on voitu painaa ja mihin funktioon sen mukaisesti liikutaan
        painallus_valinnat = {
            'Right': self.liiku_oikealle,
            'Tab': self.liiku_oikealle,
            'Left': self.liiku_vasemmalle,
            'Down': self.liiku_alas,
            'Up': self.liiku_ylos,
            'F9': self.show_settings,
            'F11': self.show_saannot,
            'F1': self.show_manual,
            'F4': self.show_lataa_tallenna,
            'Return': self.seuraava_kierros,
            'KP_Enter': self.seuraava_kierros,
            'edit': self.edit_pelaaja_nimi,
            'Escape': self.lopeta_peli
        }

        # Määritetään menemään oikeaan funktioon tai jos ei erikseen määritetty, niin mene kirjoitukseen
        painallus_valinnat.get(painallus, lambda: self.edit_pelaaja_nimi(kirjain))()
        # Varmista, että kaikki on piirretty oikein, ellei ohjelmaa sammutettu
        self.scale_objects() if painallus != 'Escape' else None

    @staticmethod
    def liiku_oikealle() -> None:
        # Siirrä valintoja yhden paikan, tai sarakkeen verran oikealle
        gl.valintaSijaintiX += gl.sarakkeenLeveys
        gl.valittu += 1
        if gl.valittu > gl.pelaajaMaara:
            gl.valintaSijaintiX = gl.sijaintiXOletus
            gl.valittu = 0

    @staticmethod
    def liiku_vasemmalle() -> None:
        # global valintaSijaintiX, valittu
        gl.valintaSijaintiX = gl.valintaSijaintiX - gl.sarakkeenLeveys
        gl.valittu = gl.valittu - 1
        if gl.valittu < 0:
            gl.valintaSijaintiX = gl.sijaintiXOletus + (gl.pelaajaMaara * gl.sarakkeenLeveys)
            gl.valittu = gl.pelaajaMaara

    @staticmethod
    def liiku_ylos() -> None:
        # global valittuKierros, valintaSijaintiY, kierrosNumero, jakaja
        if gl.kierrosNumero == 0:
            gl.jakaja = gl.jakaja - 1
            if gl.jakaja < 0:
                gl.jakaja = gl.pelaajaMaara
            for item in range(len(pelaaja)):
                if item == gl.jakaja:
                    pelaaja[item]['jakaja'] = True
                else:
                    pelaaja[item]['jakaja'] = False
        elif gl.kierrosNumero < 9:
            gl.valittuKierros = gl.valittuKierros - 1
            gl.valintaSijaintiY = gl.valintaSijaintiY - gl.rivivali
            if gl.valittuKierros < 1:
                gl.valittuKierros = gl.kierrosNumero
                gl.valintaSijaintiY = gl.sijaintiYOletus + (gl.kierrosNumero * gl.rivivali)
        else:
            gl.valittuKierros = gl.valittuKierros - 1
            gl.valintaSijaintiY = gl.valintaSijaintiY - gl.rivivali
            if gl.valittuKierros < 1:
                gl.valittuKierros = 8
                gl.valintaSijaintiY = gl.sijaintiYOletus + (8 * gl.rivivali)

    @staticmethod
    def liiku_alas() -> None:
        # global valittuKierros, valintaSijaintiY, kierrosNumero, jakaja, pelaajaMaara
        if gl.kierrosNumero == 0:
            gl.jakaja += 1
            if gl.jakaja > gl.pelaajaMaara:
                gl.jakaja = 0
            for item in range(len(pelaaja)):
                if item == gl.jakaja:
                    pelaaja[item]['jakaja'] = True
                else:
                    pelaaja[item]['jakaja'] = False
        elif gl.kierrosNumero < 9:
            gl.valittuKierros += 1
            gl.valintaSijaintiY += gl.rivivali
            if gl.valittuKierros > gl.kierrosNumero:
                gl.valittuKierros = 1
                gl.valintaSijaintiY = gl.sijaintiYOletus + gl.rivivali
        else:
            gl.valittuKierros += 1
            gl.valintaSijaintiY += gl.rivivali
            if gl.valittuKierros > 8:
                gl.valittuKierros = 1
                gl.valintaSijaintiY = gl.sijaintiYOletus + gl.rivivali

    @staticmethod
    def show_saannot() -> None:
        os.startfile('media\\saannot.pdf', 'open')

    def edit_pelaaja_nimi(self, kirjain: str) -> None:
        if gl.valittuKierros == 0:
            if kirjain == "\b":
                temp_nimi = pelaaja[gl.valittu]['nimi'][:-1]
            else:
                temp_nimi = pelaaja[gl.valittu]['nimi'] + kirjain
                # print(len(temp_nimi))
                if len(temp_nimi) > 12:
                    temp_nimi = temp_nimi[:-1]

            pelaaja[gl.valittu]['nimi'] = temp_nimi
            self.rootCanvas.itemconfig(self.pelaajaText[gl.valittu], text=temp_nimi)
            self.rootCanvas.itemconfig(self.pelaajaNimi[gl.valittu], text=temp_nimi)
            # print(temp_nimi)
        else:
            if kirjain == "\b":
                temp_pisteet = str(pelaaja[gl.valittu]['pisteet'][gl.valittuKierros - 1])[:-1]

            elif kirjain.isdigit():
                temp_pisteet = str(pelaaja[gl.valittu]['pisteet'][gl.valittuKierros - 1]) + kirjain
                if len(temp_pisteet) > 3:
                    temp_pisteet = temp_pisteet[:-1]
            else:
                return

            pelaaja[gl.valittu]['pisteet'][gl.valittuKierros - 1] = temp_pisteet
            self.rootCanvas.itemconfig(self.kierrosPisteet[int(gl.valittuKierros)][int(gl.valittu)], text=temp_pisteet)
            self.pisteiden_laskenta() if gl.valittuKierros < gl.kierrosNumero else None

    def hiiren_valinta(self, event: tk.Event) -> None:
        # global valittu, valittuKierros, valintaSijaintiY, valintaSijaintiX, jakaja, pelaaja
        hiiri_x = event.x
        hiiri_y = event.y
        ikkuna_x = self.master.winfo_width()
        ikkuna_y = self.master.winfo_height()
        sijainti_x_oletus_scaled = ikkuna_x * (gl.sijaintiXOletus / gl.ikkunaXScale)
        sijainti_y_oletus_scaled = ikkuna_y * ((gl.sijaintiYOletus - gl.rivivali) / gl.ikkunaYScale)
        sarakkeen_leveys_scaled = ikkuna_x * (gl.sarakkeenLeveys / gl.ikkunaXScale)
        koko_piste_marginaali_scaled = ikkuna_y * ((gl.kokoPisteMarginaali + (gl.rivivali / 2)) / gl.ikkunaYScale)
        vasen_koko_piste_marginaali_scaled = ikkuna_x * (gl.vasenKokoPisteMarginaali / gl.ikkunaXScale)
        rivivali_scaled = ikkuna_y * (gl.rivivali / gl.ikkunaYScale)

        if hiiri_x > sijainti_x_oletus_scaled and koko_piste_marginaali_scaled > hiiri_y > sijainti_y_oletus_scaled:
            # print('Olet pistetaulussa')
            temp_x = sijainti_x_oletus_scaled + sarakkeen_leveys_scaled
            for integer in range(gl.pelaajaMaara + 1):
                if hiiri_x < temp_x:
                    # print('olet pelaajan ' + str(int) + ' kohdalla')
                    temp_y = sijainti_y_oletus_scaled + rivivali_scaled
                    for kierros_int in range(gl.kierrosNumero + 1):
                        if hiiri_y < temp_y:
                            # print('olet kierroksen ' + str(kierros_int) + ' kohdalla')
                            gl.valittu = integer
                            gl.valittuKierros = kierros_int
                            gl.valintaSijaintiX = gl.sijaintiXOletus + (gl.valittu * gl.sarakkeenLeveys)
                            gl.valintaSijaintiY = gl.sijaintiYOletus + (gl.valittuKierros * gl.rivivali)
                            self.scale_objects()
                            break
                        else:
                            temp_y += rivivali_scaled
                    break
                else:
                    temp_x += sarakkeen_leveys_scaled
        elif hiiri_x < vasen_koko_piste_marginaali_scaled and hiiri_y > koko_piste_marginaali_scaled:
            # print('olet määrittämässä jakajaa')
            temp_y = koko_piste_marginaali_scaled + rivivali_scaled
            for integer in range(gl.pelaajaMaara + 1):
                if hiiri_y < temp_y:
                    pelaajan_nimi = self.rootCanvas.itemcget(self.pelaajaText[integer], 'text')
                    for item in range(len(pelaaja)):
                        if pelaaja[item]['nimi'] == pelaajan_nimi:
                            gl.jakaja = item
                    # print('olet jakaja paikalla ' + str(int))
                    for item in range(len(pelaaja)):
                        if item == gl.jakaja:
                            pelaaja[item]['jakaja'] = True
                        else:
                            pelaaja[item]['jakaja'] = False
                    self.scale_objects()
                    break
                else:
                    temp_y += rivivali_scaled

    def seuraava_kierros(self) -> None:

        global pelaaja

        self.virheen_tarkistus()
        self.virheen_tulostus(gl.virhe) if gl.virhe else None

        if gl.virhe == 0:
            self.rootCanvas.itemconfig(self.virhe_teksti, text='')
            if gl.kierrosNumero < 9:
                self.rootCanvas.itemconfig(self.kierrosNimiNyt, text=gl.kierros[gl.kierrosNumero + 1])
            if gl.kierrosNumero == 0:
                pelaaja = [item for item in pelaaja if item['nimi']]
                self.pelaajaText = [item for item in self.pelaajaText if self.rootCanvas.itemconfig(item)['text'][4]]
                self.pelaajaNimi = [item for item in self.pelaajaNimi if self.rootCanvas.itemconfig(item)['text'][4]]
                gl.pelaajaMaara = len(pelaaja) - 1
                gl.sarakkeenLeveys = (gl.ikkunaXScale - gl.sijaintiXOletus) / (gl.pelaajaMaara + 1)
                gl.kierrosNumero += 1
                if gl.valittu > gl.pelaajaMaara:
                    gl.valittu = gl.pelaajaMaara
                gl.valintaSijaintiY += gl.rivivali
                gl.valintaSijaintiX = gl.sijaintiXOletus + (gl.sarakkeenLeveys * gl.valittu)
                gl.valittuKierros += 1
                x_temp = gl.sijaintiXOletus + (gl.sarakkeenLeveys / 2)
                y_temp = gl.ekaKierrosYLocation + (gl.rivivali * gl.kierrosNumero)
                jakaja_loydetty = False
                for item in pelaaja:
                    temp_item = self.rootCanvas.create_text(x_temp, y_temp, text='', anchor='n',
                                                            font=self.perusFontti, fill=asetus['fonttiVari'])
                    temp_item2 = self.rootCanvas.create_text(gl.vasenMarginaali, gl.kokoPisteMarginaali, text='',
                                                             font=self.perusFontti, fill=asetus['fonttiVari'])
                    self.kierrosPisteet[gl.kierrosNumero].append(temp_item)
                    self.kokoPisteTeksti.append(temp_item2)
                    x_temp += gl.sarakkeenLeveys
                    # jos jakajaa ei ole vielä löydetty, niin katsotaan onko tämä jakaja
                    jakaja_loydetty = item['jakaja'] if not jakaja_loydetty else jakaja_loydetty
                pelaaja[0]['jakaja'] = True if not jakaja_loydetty else pelaaja[0]['jakaja']

            elif gl.kierrosNumero < 9:
                gl.kierrosNumero += 1
                if gl.kierrosNumero < 9:
                    gl.valintaSijaintiY = gl.rivivali * gl.kierrosNumero + gl.sijaintiYOletus
                    gl.valittuKierros = gl.kierrosNumero
                    x_temp = gl.sijaintiXOletus + (gl.sarakkeenLeveys / 2)
                    y_temp = gl.ekaKierrosYLocation + (gl.rivivali * gl.kierrosNumero)
                    gl.jakaja += 1
                    gl.jakaja = 0 if gl.jakaja > gl.pelaajaMaara else gl.jakaja
                    for item_number, item in enumerate(pelaaja):
                        temp_item = self.rootCanvas.create_text(x_temp, y_temp, text='', anchor='n',
                                                                font=self.perusFontti, fill=asetus['fonttiVari'])
                        self.kierrosPisteet[gl.kierrosNumero].append(temp_item)
                        if not item['pisteet'][gl.kierrosNumero - 2]:
                            self.rootCanvas.itemconfig(self.kierrosPisteet[gl.kierrosNumero - 1][item_number], text='0')
                        item['jakaja'] = item_number == gl.jakaja
                        x_temp += gl.sarakkeenLeveys
                elif gl.kierrosNumero == 9:
                    for item_number, item in enumerate(pelaaja):
                        if not item['pisteet'][gl.kierrosNumero - 2]:
                            self.rootCanvas.itemconfig(self.kierrosPisteet[gl.kierrosNumero - 1][item_number], text='0')
                    self.laheta_pisteet_palvelimelle()
                self.pisteiden_laskenta()
                TallennusLatausIkkuna.tallenna_peli(None, 'auto')
            else:
                self.uusi_peli()
            self.scale_objects()

    def jarjesta_pelaajat(self) -> None:
        global pelaaja
        sorted_pelaaja = sorted(pelaaja, key=lambda x: int(x['kokonaisPisteet']))
        for sija, item in enumerate(sorted_pelaaja, start=1):
            item['sijoitus'] = str(sija)

        for item in range(len(self.pelaajaText)):
            self.rootCanvas.itemconfig(self.pelaajaText[item], text=sorted_pelaaja[item]['nimi'])
            self.rootCanvas.itemconfig(self.kokoPisteTeksti[item], text=sorted_pelaaja[item]['kokonaisPisteet'])

    def pisteiden_laskenta(self) -> None:
        # kokonaispisteiden laskenta
        global pelaaja

        for item in pelaaja:
            koko_piste = 0
            for item2 in range(gl.kierrosNumero - 1):
                if item['pisteet'][item2]:
                    koko_piste += int(item['pisteet'][item2])
                else:
                    item['pisteet'][item2] = '0'
            item['kokonaisPisteet'] = str(koko_piste)
        self.jarjesta_pelaajat()

    def uusi_peli(self) -> None:
        # global pelaajaMaara, pelaaja, kierrosNumero, valittuKierros, valintaSijaintiY, valintaSijaintiX
        # global jakaja, sarakkeenLeveys, valittu
        global pelaaja
        print('tähän tulisi uuden pelin koodi')
        print('Kyllä tykkään, selkeä ja helppolukuinen sekä hyvin kommentoitu :) T:Cave')

        gl.pelaajaMaara = 6
        gl.kierrosNumero = 0
        gl.valittuKierros = 0
        gl.valintaSijaintiX = gl.sijaintiXOletus
        gl.valintaSijaintiY = gl.sijaintiYOletus
        gl.sarakkeenLeveys = (gl.ikkunaXScale - gl.sijaintiXOletus) / (gl.pelaajaMaara + 1)
        gl.valittu = 0
        gl.jakaja = 0

        pelaaja_nimet_temp = [item['nimi'] for item in pelaaja]
        for item in range(4):
            pelaaja_nimet_temp.append('')
        pelaaja = []
        for player in range(gl.pelaajaMaara + 1):
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
        self.valintaViiva = self.rootCanvas.create_line(gl.valintaSijaintiX, gl.valintaSijaintiY,
                                                        gl.valintaSijaintiX + gl.sarakkeenLeveys, gl.valintaSijaintiY,
                                                        fill=asetus['fonttiVari'], width=2)
        for item in range(gl.pelaajaMaara + 1):
            temp_text = self.rootCanvas.create_text(gl.vasenMarginaali + 30, 50, anchor="w", text=pelaaja[item]['nimi'],
                                                    font=self.perusFontti, fill=asetus['fonttiVari'])
            self.pelaajaText.append(temp_text)

        x_temp = gl.valintaSijaintiX + (gl.sarakkeenLeveys / 2)
        for item in range(gl.pelaajaMaara + 1):
            temp_text = self.rootCanvas.create_text(x_temp, gl.valintaSijaintiY - gl.fonttiKoko,
                                                    text=pelaaja[item]['nimi'], anchor='center',
                                                    font=self.perusFontti, fill=asetus['fonttiVari'])
            x_temp += gl.sarakkeenLeveys
            self.pelaajaNimi.append(temp_text)

        y_temp = gl.ekaKierrosYLocation
        for it in gl.kierrosLyhenne:
            text = self.rootCanvas.create_text(10, y_temp, anchor="nw", text=it,
                                               font=self.perusFontti, fill=asetus['fonttiVari'])
            self.kierrosLyhenneText.append(text)
            y_temp += gl.rivivali

        self.kierrosNimiNyt = self.rootCanvas.create_text(600, 600, text=gl.kierros[0],
                                                          font=self.isoFontti, fill=asetus['fonttiVari'])
        self.jakajanMerkki = self.rootCanvas.create_text(10, gl.kokoPisteMarginaali + gl.rivivali, text='Ⓙ',
                                                         font=self.J_Fontti, fill=asetus['fonttiVari'])
        self.ohjeTeksti = self.rootCanvas.create_text(600, 650, text='Ohjeet painamalla F1',
                                                      font=self.perusFontti, fill=asetus['fonttiVari'])
        self.versioTeksti = self.rootCanvas.create_text(gl.versioTekstiX, gl.versioTekstiY, text=versioNumero,
                                                        font=self.verFontti, fill=asetus['fonttiVari'])
        self.text_Kokopiste = self.rootCanvas.create_text(gl.vasenMarginaali, gl.kokoPisteMarginaali,
                                                          anchor="w", text="Kokonaispisteet:", font=self.perusFontti,
                                                          fill=asetus['fonttiVari'])
        self.virhe_teksti = self.rootCanvas.create_text(500, 400, text='', font=self.isoFontti, fill='red')

        self.scale_objects()

    def laheta_pisteet_palvelimelle(self) -> None:
        if asetus['datanLahetys']:
            print('olet lähettämässä pisteitä palvelimelle')

            game_id = self.create_gameid()
            self.pisteiden_laskenta()
            lahetettava_pelaaja: list[str: int] = []
            for player in pelaaja:
                player_temp = {'Name': player['nimi'],
                               'Points': {str(i): int(j) for i, j in enumerate(player['pisteet'], 1)}}
                player_temp['Points']['Total'] = int(player['kokonaisPisteet'])
                lahetettava_pelaaja.append(player_temp)

            tallennettava_tiedosto: object = {
                'client_version': versioNumero,
                'Players': lahetettava_pelaaja
            }

            print(tallennettava_tiedosto)

            tiedosto_nimi = f'saves/{game_id}.json'
            with open(tiedosto_nimi, 'w') as file:
                dump(tallennettava_tiedosto, file)
            file.close()

            lahetettava_tiedosto = {
                'data': tallennettava_tiedosto,
                'name': game_id
            }
            api_key: str = 'pisteenlaskija2024versio3'
            server_url: str = 'http://192.168.1.100:5000/api/data'
            lahetettava_tiedosto_json = dumps(lahetettava_tiedosto)
            try:
                response = requests.post(server_url, data=lahetettava_tiedosto_json, headers={
                    'Content-Type': 'application/json', 'X-API-KEY': api_key})
                os.remove(tiedosto_nimi) if response.status_code == 200 else None
            except Exception as e:
                print(e)
                mb.showinfo('Virhe palvelinyhteydessä', f'Palvelin yhteydessä ilmaantui virhe {e}')

    @staticmethod
    def create_gameid() -> str:
        aika_nyt = datetime.datetime.now()
        return aika_nyt.strftime("%Y%m%d%H%M%S")

    @staticmethod
    def virheen_tarkistus() -> None:

        # global virhe

        gl.virhe = 0

        # tarkista pelaajat, jos alle 3 tai löytyy saman nimisiä pelaajia, niin luodaan virhe
        if gl.kierrosNumero == 0:
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
                gl.virhe = 4

            if len(pelaaja_temp) < 3:
                gl.virhe = 3
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
            kierros_pisteet_temp = kierros_pisteet_temp[:gl.kierrosNumero]  # 3
            # print(kierros_pisteet_temp)

            for kierros_nyt in kierros_pisteet_temp:  # 4
                voittaja = sum(item == '' or item == '0' for item in kierros_nyt)
                # print(voittaja)
                if voittaja > 1:
                    gl.virhe = 1
                elif voittaja < 1:
                    gl.virhe = 2
                for piste in kierros_nyt:  # 5
                    # print(piste)
                    if piste == '':
                        piste = 0
                    if int(piste) > 200 or int(piste) == 1:
                        gl.virhe = 2

    def virheen_tulostus(self, virhe_numero: int) -> None:

        valinnat = {
            1: 'Et ole syöttänyt kaikille pisteitä',
            2: 'Tarkista pisteet',
            3: 'Pelaajia on liian vähän',
            4: 'Nimet ovat liian samanlaiset'
        }
        # print("olen tulostuksessa ja virhe_numero on " + str(virhe_numero) + " ja teksti on" + valinnat[virhe_numero])
        if virhe_numero in valinnat:
            self.rootCanvas.itemconfig(self.virhe_teksti, text=valinnat[virhe_numero])

    @staticmethod
    def on_jakaja(pelaaja_nimi: str) -> bool:
        jakaja_func = False
        for item in pelaaja:
            if item['nimi'] == pelaaja_nimi:
                jakaja_func = item['jakaja']
        return jakaja_func

    def scale_objects(self, *_: tk.Event) -> None:
        # For scaling update the screen_width and screen_height variables
        ikkuna_leveys_scaled = self.master.winfo_width()
        ikkuna_korkeus_scaled = self.master.winfo_height()

        # Updated Locations:
        eka_kierros_y_location_scaled = ikkuna_korkeus_scaled * (gl.ekaKierrosYLocation / gl.ikkunaYScale)
        koko_piste_marginaali_scaled = ikkuna_korkeus_scaled * (gl.kokoPisteMarginaali / gl.ikkunaYScale)
        vasen_marginaali_scaled = ikkuna_leveys_scaled * (gl.vasenMarginaali / gl.ikkunaXScale)
        vasen_kokopiste_nimi_marginaali_scaled = (ikkuna_leveys_scaled *
                                                  (gl.vasenKokoPisteNimiMarginaali / gl.ikkunaXScale))
        vasen_kokopiste_piste_marginaali_scaled = ikkuna_leveys_scaled * (gl.vasenKokoPisteMarginaali / gl.ikkunaXScale)
        fontti_koko_iso_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoIso / gl.ikkunaYScale)
        fontti_koko_scaled = ikkuna_korkeus_scaled * (gl.fonttiKoko / gl.ikkunaYScale)
        fontti_koko_pieni_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoPieni / gl.ikkunaYScale)
        fontti_koko_ver_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoVer / gl.ikkunaYScale)
        valinta_sijainti_x_scaled = ikkuna_leveys_scaled * (gl.valintaSijaintiX / gl.ikkunaXScale)
        valinta_sijainti_y_scaled = ikkuna_korkeus_scaled * (gl.valintaSijaintiY / gl.ikkunaYScale)
        nimi_sijainti_y_scaled = ikkuna_korkeus_scaled * (gl.sijaintiYOletus / gl.ikkunaYScale)
        sarakkeen_leveys_scaled = ikkuna_leveys_scaled * (gl.sarakkeenLeveys / gl.ikkunaXScale)
        sijainti_x_oletus_scaled = ikkuna_leveys_scaled * (gl.sijaintiXOletus / gl.ikkunaXScale)
        virheen_sijainti_x_scaled = ikkuna_leveys_scaled * (gl.virheenSijaintiX / gl.ikkunaXScale)
        virheen_sijainti_y_scaled = ikkuna_korkeus_scaled * (gl.virheenSijaintiY / gl.ikkunaYScale)
        kierros_nimi_x_scaled = ikkuna_leveys_scaled * (gl.kierrosNimiX / gl.ikkunaXScale)
        kierros_nimi_y_scaled = ikkuna_korkeus_scaled * (gl.kierrosNimiY / gl.ikkunaYScale)
        ohje_teksti_x_scaled = ikkuna_leveys_scaled * (gl.ohjeTekstiX / gl.ikkunaXScale)
        ohje_teksti_y_scaled = ikkuna_korkeus_scaled * (gl.ohjeTekstiY / gl.ikkunaYScale)
        jakajan_merkki_x_scaled = ikkuna_leveys_scaled * (gl.fonttiKokoJ / gl.ikkunaXScale)
        versio_teksti_x_scaled = ikkuna_leveys_scaled * (gl.versioTekstiX / gl.ikkunaXScale)
        versio_teksti_y_scaled = ikkuna_korkeus_scaled * (gl.versioTekstiY / gl.ikkunaYScale)
        fontti_koko_j_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoJ / gl.ikkunaYScale)
        fontti_koko_virhe_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoVirhe / gl.ikkunaYScale)
        rivivali_scaled = ikkuna_korkeus_scaled * (gl.rivivali / gl.ikkunaYScale)

        # Update font -objects to correct size:
        self.perusFontti = Font(family=gl.fontti, size=int(fontti_koko_scaled*(asetus['fonttiKoko']/100)))
        self.isoFontti = Font(family=gl.fontti, size=int(fontti_koko_iso_scaled*(asetus['fonttiKoko']/100)))
        self.pieniFontti = Font(family=gl.fontti, size=int(fontti_koko_pieni_scaled*(asetus['fonttiKoko']/100)))
        self.verFontti = Font(family=gl.fontti, size=int(fontti_koko_ver_scaled*(asetus['fonttiKoko']/100)))
        self.J_Fontti = Font(family=gl.fontti, size=int(fontti_koko_j_scaled*(asetus['fonttiKoko']/100)))
        self.virheFontti = Font(family=gl.fontti, size=int(fontti_koko_virhe_scaled*(asetus['fonttiKoko']/100)))

        # update texts based of the updated variables above
        y_temp = eka_kierros_y_location_scaled
        for item in range(len(self.kierrosLyhenneText)):
            self.rootCanvas.coords(self.kierrosLyhenneText[item], vasen_marginaali_scaled, y_temp)
            self.rootCanvas.itemconfig(self.kierrosLyhenneText[item], font=self.pieniFontti, fill=asetus['fonttiVari'])
            y_temp += rivivali_scaled

        y_temp = koko_piste_marginaali_scaled + rivivali_scaled
        for item in range(len(self.pelaajaText)):
            self.rootCanvas.coords(self.pelaajaText[item], vasen_kokopiste_nimi_marginaali_scaled, y_temp)
            self.rootCanvas.itemconfig(self.pelaajaText[item], font=self.perusFontti, fill=asetus['fonttiVari'])
            if gl.kierrosNumero == 0:
                if gl.jakaja == item:
                    self.rootCanvas.coords(self.jakajanMerkki, jakajan_merkki_x_scaled, y_temp)
                    self.rootCanvas.itemconfig(self.jakajanMerkki, font=self.J_Fontti, fill=asetus['fonttiVari'])
            else:
                if self.on_jakaja(self.rootCanvas.itemcget(self.pelaajaText[item], 'text')):
                    self.rootCanvas.coords(self.jakajanMerkki, jakajan_merkki_x_scaled, y_temp)
                    self.rootCanvas.itemconfig(self.jakajanMerkki, font=self.J_Fontti, fill=asetus['fonttiVari'])
            y_temp += rivivali_scaled

        x_temp = sijainti_x_oletus_scaled + (sarakkeen_leveys_scaled / 2)
        for item in range(len(self.pelaajaNimi)):
            self.rootCanvas.coords(self.pelaajaNimi[item], x_temp,
                                   nimi_sijainti_y_scaled - (fontti_koko_scaled/2))
            self.rootCanvas.itemconfig(self.pelaajaNimi[item], font=self.perusFontti, fill=asetus['fonttiVari'])
            x_temp += sarakkeen_leveys_scaled

        x_temp = sijainti_x_oletus_scaled + (sarakkeen_leveys_scaled / 2)
        y_temp = eka_kierros_y_location_scaled - rivivali_scaled
        # print(self.kierrosPisteet)
        for item in self.kierrosPisteet:
            for item2 in item:
                self.rootCanvas.coords(item2, x_temp, y_temp)
                self.rootCanvas.itemconfig(item2, font=self.perusFontti, fill=asetus['fonttiVari'])
                x_temp += sarakkeen_leveys_scaled
            x_temp = sijainti_x_oletus_scaled + (sarakkeen_leveys_scaled / 2)
            y_temp += rivivali_scaled

        y_temp = koko_piste_marginaali_scaled + rivivali_scaled
        for item in self.kokoPisteTeksti:
            self.rootCanvas.coords(item, vasen_kokopiste_piste_marginaali_scaled, y_temp)
            self.rootCanvas.itemconfig(item, font=self.perusFontti, fill=asetus['fonttiVari'])
            y_temp += rivivali_scaled

        self.rootCanvas.coords(self.kierrosNimiNyt, kierros_nimi_x_scaled, kierros_nimi_y_scaled)
        self.rootCanvas.itemconfig(self.kierrosNimiNyt, font=self.isoFontti, fill=asetus['fonttiVari'])
        self.rootCanvas.coords(self.ohjeTeksti, ohje_teksti_x_scaled, ohje_teksti_y_scaled)
        self.rootCanvas.itemconfig(self.ohjeTeksti, font=self.perusFontti, fill=asetus['fonttiVari'])
        self.rootCanvas.coords(self.valintaViiva, valinta_sijainti_x_scaled, valinta_sijainti_y_scaled,
                               valinta_sijainti_x_scaled + sarakkeen_leveys_scaled, valinta_sijainti_y_scaled)
        self.rootCanvas.itemconfig(self.valintaViiva, fill=asetus['fonttiVari'])
        self.rootCanvas.coords(self.text_Kokopiste, vasen_marginaali_scaled, koko_piste_marginaali_scaled)
        self.rootCanvas.itemconfig(self.text_Kokopiste, font=self.perusFontti, fill=asetus['fonttiVari'])
        self.rootCanvas.coords(self.virhe_teksti, virheen_sijainti_x_scaled, virheen_sijainti_y_scaled)
        self.rootCanvas.itemconfig(self.virhe_teksti, font=self.virheFontti)
        self.rootCanvas.coords(self.versioTeksti, versio_teksti_x_scaled, versio_teksti_y_scaled)
        self.rootCanvas.itemconfig(self.versioTeksti, font=self.verFontti, fill=asetus['fonttiVari'])
        self.rootCanvas.configure(height=ikkuna_korkeus_scaled, width=ikkuna_leveys_scaled)
        self.taustakuva_resized = self.taustakuva_original.resize((ikkuna_leveys_scaled, ikkuna_korkeus_scaled),
                                                                  Image.Resampling.LANCZOS)
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)
        self.rootCanvas.itemconfig(self.muokattu_tausta, image=self.uusi_tausta)


# super simple window creation, which get all objects from Pisteenlaskija -class
root = tk.Tk()
tallennus_nimet()
root.title("Sanghai Pisteenlaskija")
root.geometry("1280x720")

asetus: dict = lue_asetukset()
pelaaja = [{
    'nimi': '',
    'pisteet': ['', '', '', '', '', '', '', ''],
    'jakaja': pelaaja_numero == 0
} for pelaaja_numero in range(gl.pelaajaMaara + 1)]

PisteenlaskijaUI(root)
root.mainloop()
