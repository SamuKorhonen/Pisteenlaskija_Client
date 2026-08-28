# cython: language_level = 3

import datetime
import functools
import logging
import tkinter.simpledialog
import tkinter as tk
from PIL import ImageTk, Image
import globals as gl
import requests
from tkinter import messagebox as mb
from tkinter import font as tkFont
from json import load, dump, dumps
import os.path
import threading
from typing import Optional

cdef str versioNumero = "3"
cdef list tallennusNimi = []
cdef dict asetus = {}
cdef str api_key = ''
cdef list pelaaja = []
cdef bint pisteiden_lahetys_teksti_nakyvissa = False

# Try to import tkextrafont, if not available set to False
cdef bint tkextrafont_available = False
try:
    import tkextrafont as Font
    tkextrafont_available = True
except ImportError:
    tkextrafont_available = False
except Exception as e:
    print("Tuntematon virhe fontin lataamista varten", str(e))
    print("Fonttia ei pysty lataamaan kirjastovirheen vuoksi")

def tallennus_nimet() -> None:
    cdef int tallennus
    cdef str tiedosto_nimi
    cdef dict haettu_data
    for tallennus in range(gl.tallennuspaikat):
        tiedosto_nimi = f'saves/save_{tallennus}.json'
        if os.path.isfile(tiedosto_nimi):
            with open(tiedosto_nimi, 'r') as f:
                haettu_data = load(f)
            gl.tallennusNimi.append(haettu_data['tallennuksen_nimi'])
        else:
            gl.tallennusNimi.append('')

def lue_asetukset() -> dict:
    cdef dict asetus_local = {
        'fonttiVari': gl.fonttiVari,
        'fonttiKoko': 100,
        'datanLahetys': True,
        'palvelinOsoite': 'localhost',
        'api': "pisteenlaskija2024versio3"
    }
    cdef dict asetukset_tiedosto
    with open('media/settings.json') as tiedosto:
        asetukset_tiedosto = load(tiedosto)
    asetus_local['fonttiVari'] = asetukset_tiedosto['fonttiVari']
    asetus_local['fonttiKoko'] = asetukset_tiedosto['fonttiKoko']
    asetus_local['datanLahetys'] = asetukset_tiedosto['datanLahetys']
    asetus_local['palvelinOsoite'] = asetukset_tiedosto['palvelinOsoite']
    asetus_local['api'] = asetukset_tiedosto['api']
    return asetus_local

class AsetuksetIkkuna(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Settings")
        self.geometry("300x200")

        self.frame_grid = tk.Frame(self)
        self.frame_labels = tk.Frame(self)
        self.checkbox_setting_datanlahetys_var = tk.BooleanVar()

        self.settings_list = [
            {"label": "Fonttiväri", "name": "fonttiVari", "type": "entry", "value": asetus['fonttiVari']},
            {"label": "Fonttikoko:", "name": "fonttiKoko", "type": "entry", "value": asetus['fonttiKoko']},
            {"label": "Salli pisteiden tilastointi", "name": "datanLahetys",
             "type": "checkbox", "value": asetus['datanLahetys']},
            {"label": "Palvelimen Osoite", "name": "palvelinOsoite",
             "type": "entry", "value": asetus['palvelinOsoite']},
        ]

        self.variables = {}

        # Create settings widgets
        cdef int i
        cdef dict setting
        cdef str label_text, entry_text
        for i, setting in enumerate(self.settings_list):
            label_text = setting["label"]
            label = tk.Label(self.frame_grid, text=label_text)
            label.grid(row=i, column=0)
            if setting["type"] == "entry":
                entry_text = setting["value"]
                entry = tk.Entry(self.frame_grid)
                entry.insert(0, entry_text)
                entry.grid(row=i, column=1)
                self.variables[setting["name"]] = entry
            elif setting["type"] == "checkbox":
                var = tk.BooleanVar()
                var.set(setting["value"])
                checkbox = tk.Checkbutton(self.frame_grid, variable=var)
                checkbox.grid(row=i, column=1)
                self.variables[setting["name"]] = var

        self.save_button = tk.Button(self.frame_grid, text='Tallenna', command=self.tallenna_asetukset)
        self.save_button.grid(row=len(self.settings_list), column=1)

        self.frame_grid.pack()
        self.frame_labels.pack()

    def tallenna_asetukset(self) -> None:
        cdef dict local_asetus
        cdef str local_fontti_vari
        cdef int local_fontti_koko

        with open('media/settings.json', 'r') as f:
            local_asetus = load(f)

        if self.variables['fonttiVari'].get():
            local_fontti_vari = self.variables['fonttiVari'].get()
        else:
            local_fontti_vari = gl.fonttiVari

        try:
            example_label = tk.Label(self.frame_labels, text='', foreground=local_fontti_vari)
            example_label.destroy()
            asetus['fonttiVari'] = local_asetus['fonttiVari'] = local_fontti_vari
        except Exception as e:
            print(e)
            mb.showinfo('Virhe Fonttivärissä',
                        'Aseta fontti väri joko yleisellä värin nimellä englanniksi (esim "red") '
                        'tai hexa koodilla (esim. "#383eB8")')

        try:
            local_fontti_koko = min(max(int(self.variables['fonttiKoko'].get()), 10), 200)
        except ValueError:
            local_fontti_koko = 100
            mb.showerror("Virhe fontti koon asettamisessa",
                         "Fontti koon täytyy olla välillä 40 - 200 ja "
                         "sen täytyy olla numero arvo.\nNumeroarvo tarkoittaa, "
                         "kuinka isoja fontit ovat suhteessa oletusarvoon, "
                         "eli 100. Näin ollen esimrekiksi fontti koko 50 "
                         "tarkoittaa fonttien olevan kooltaan puolet siitä mitä se "
                         "on normaalisti. \nFontti koko palautettu"
                         " arvoon 100, koska valittua asetusta ei voitu tallentaa.")

        asetus['fonttiKoko'] = local_asetus['fonttiKoko'] = local_fontti_koko
        asetus['datanLahetys'] = local_asetus['datanLahetys'] = self.variables['datanLahetys'].get()
        asetus['palvelinOsoite'] = local_asetus['palvelinOsoite'] = (self.variables['palvelinOsoite'].get()
                                                                     or 'localhost')

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

        cdef int label_number
        cdef str label
        for label_number, label in enumerate(self.labels):
            L = tk.Label(self.frame, text=label)
            L.grid(row=label_number, column=0, sticky='nsew')

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
            ' ',
            'Valitse tallennuspaikka ja sen jälkeen joko tallenna tai lataa',
            'riippuen kumman haluat tehdä',
            ' ',
        ]
        cdef int current_row
        cdef str label_text
        for label_number, label in enumerate(self.ohjeTekstit):
            L = tk.Label(self.frame, text=label)
            L.grid(row=label_number, column=0, sticky='nsew')

        self.tallennusLabels = []
        current_row = len(self.ohjeTekstit) + 1
        cdef int tallenus_nimi_var
        cdef str tallenus_nimi_name, tulostus_nimi, tiedosto_nimi
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

        L = tk.Label(self.frame, text="autotallennuspaikka")
        L.grid(row=current_row + 4, column=0, sticky='nsew')
        L = tk.Button(self.frame, text='lataa', command=functools.partial(self.lataa_peli, 'auto'))
        L.grid(row=current_row + 4, column=1, sticky='nsew')

        self.bind('<F4>', self.destroy_window)

    def destroy_window(self, *_: tk.Event) -> None:
        self.destroy()

    def lataa_peli(self, tiedosto) -> None:
        global pelaaja
        cdef str tiedosto_nimi
        cdef dict haettu_data
        cdef int item
        tiedosto_nimi = f'saves/save_{tiedosto}.json'
        try:
            with open(tiedosto_nimi, 'r') as f:
                haettu_data = load(f)
            pelaaja = haettu_data['pelaaja']
            gl.pelaajaMaara = haettu_data['pelaajaMaara']
            gl.kierrosNumero = haettu_data['kierrosNumero']
            gl.valittuKierros = haettu_data['valittuKierros']
            gl.valintaSijaintiX = haettu_data['valintaSijaintiX']
            gl.valintaSijaintiY = haettu_data['valintaSijaintiY']
            gl.jakaja = haettu_data['jakaja']
            gl.sarakkeenLeveys = haettu_data['sarakkeenLeveys']
            gl.valittu = haettu_data['valittu']

            self.ui.rootCanvas.delete('all')
            self.ui.kierrosLyhenneText = []
            self.ui.pelaajaText = []
            self.ui.pelaajaNimi = []
            self.ui.kierrosPisteet = []
            self.ui.kokoPisteTeksti = []
            for i_temp in range(9):
                self.ui.kierrosPisteet.append([])

            self.ui.muokattu_tausta = self.ui.rootCanvas.create_image(0, 0, anchor='nw', image=self.ui.uusi_tausta)
            self.ui.valintaViiva = self.ui.rootCanvas.create_line(gl.valintaSijaintiX, gl.valintaSijaintiY,
                                                                  gl.valintaSijaintiX + gl.sarakkeenLeveys,
                                                                  gl.valintaSijaintiY,
                                                                  fill=asetus['fonttiVari'], width=2)

            x_temp = int(gl.sijaintiXOletus + (gl.sarakkeenLeveys / 2))
            y_temp = gl.valintaSijaintiY - gl.fonttiKoko
            for item in range(gl.pelaajaMaara + 1):
                temp_tx = self.ui.rootCanvas.create_text(gl.vasenMarginaali + 30, 50, anchor='w',
                                                         text=pelaaja[item]['nimi'], font=self.ui.perusFontti,
                                                         fill=asetus['fonttiVari'])
                self.ui.pelaajaText.append(temp_tx)

                temp_tx = self.ui.rootCanvas.create_text(x_temp, y_temp,
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
                    if pelaaja[item]['pisteet'][krs - 1] or krs == gl.kierrosNumero:
                        temp_pisteet = pelaaja[item]['pisteet'][krs - 1]
                    else:
                        temp_pisteet = '0'
                    temp_tx = self.ui.rootCanvas.create_text(200, 500, text=temp_pisteet, anchor='n',
                                                             font=self.ui.perusFontti, fill=asetus['fonttiVari'])
                    self.ui.kierrosPisteet[krs].append(temp_tx)

            y_temp = gl.ekaKierrosYLocation
            for item in gl.kierrosLyhenne:
                temp_tx = self.ui.rootCanvas.create_text(10, y_temp, anchor='nw', text=item,
                                                     font=self.ui.perusFontti, fill=asetus['fonttiVari'])
                self.ui.kierrosLyhenneText.append(temp_tx)
                y_temp += gl.rivivali

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
                                                                   anchor='w', text="Kokonaispisteet:",
                                                                   font=self.ui.perusFontti,
                                                                   fill=asetus['fonttiVari'])
            self.ui.virhe_teksti = self.ui.rootCanvas.create_text(gl.virheenSijaintiX, gl.virheenSijaintiY, text='',
                                                                  font=self.ui.isoFontti, fill='red')
            self.ui.pisteiden_lahetys_teksti = self.ui.rootCanvas.create_text(800, gl.versioTekstiY, text='',
                                                                             font=self.ui.verFontti,
                                                                             fill='green')

            self.ui.pisteiden_laskenta()
            self.ui.scale_objects()
            self.destroy()
        except FileNotFoundError:
            mb.showinfo('Virhe latauksessa', 'Tiedostoa ei löytynyt')
            self.lift()

    def tallenna_peli(self: Optional, tiedosto) -> None:
        cdef str tallennuksen_nimi
        cdef list lahetettava_pelaaja
        cdef dict player
        cdef dict player_temp
        cdef str game_id
        cdef str tiedosto_nimi
        cdef str tallennettava_tiedosto_json

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

        if self:
            mb.showinfo('Tallennus onnistui', 'tiedosto tallennettu onnistuneesti')
            self.tallennusLabels[tiedosto].config(text=tallennuksen_nimi)
            self.destroy()
            app.lataa_tallenna = None

class PisteenlaskijaUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.master = master
        self.settings_window = None
        self.manual_window = None
        self.lataa_tallenna = None
        self.game_id: str = self.create_gameid()

        self.perusFontti: Font = self.load_font(int(gl.fonttiKoko))
        self.isoFontti: Font = self.load_font(int(gl.fonttiKokoIso * (asetus['fonttiKoko'] / 100)))
        self.pieniFontti: Font = self.load_font(int(gl.fonttiKokoPieni * (asetus['fonttiKoko'] / 100)))
        self.verFontti: Font = self.load_font(int(gl.fonttiKokoVer * (asetus['fonttiKoko'] / 100)))
        self.J_Fontti: Font = self.load_font(int(gl.fonttiKokoJ * (asetus['fonttiKoko'] / 100)))
        self.virheFontti: Font = self.load_font(int(gl.fonttiKokoVirhe * (asetus['fonttiKoko'] / 100)))

        self.kierrosLyhenneText: list[int] = []
        self.pelaajaText: list[int] = []
        self.pelaajaNimi: list[int] = []
        self.kierrosPisteet: list[list[int]] = []
        self.kokoPisteTeksti: list[int] = []
        for i_temp in range(9):
            self.kierrosPisteet.append([])

        self.taustakuva_original: Image = Image.open("media/tausta.bmp")
        self.taustakuva_resized: Image = self.taustakuva_original.resize((gl.ikkunaXScale, gl.ikkunaYScale),
                                                                         Image.Resampling.LANCZOS)
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)
        self.rootCanvas = tk.Canvas(self.master, width=gl.ikkunaXScale, height=gl.ikkunaYScale)
        self.muokattu_tausta = self.rootCanvas.create_image(0, 0, anchor="nw", image=self.uusi_tausta)

        self.valintaViiva: int = self.rootCanvas.create_line(gl.valintaSijaintiX, gl.valintaSijaintiY,
                                                             gl.valintaSijaintiX + gl.sarakkeenLeveys,
                                                             gl.valintaSijaintiY,
                                                             fill=asetus['fonttiVari'], width=2)

        cdef int x_temp = gl.valintaSijaintiX + (gl.sarakkeenLeveys / 2)
        cdef int y_temp = gl.ekaKierrosYLocation
        cdef int item
        for item in range(gl.pelaajaMaara + 1):
            temp_text = self.rootCanvas.create_text(gl.vasenMarginaali + 30, 50, anchor="w", text='',
                                                    font=self.perusFontti, fill=asetus['fonttiVari'])
            self.pelaajaText.append(temp_text)

            temp_text = self.rootCanvas.create_text(x_temp, gl.valintaSijaintiY - gl.fonttiKoko, text='',
                                                    anchor='center', font=self.perusFontti, fill=asetus['fonttiVari'])
            x_temp += gl.sarakkeenLeveys
            self.pelaajaNimi.append(temp_text)

        for item in gl.kierrosLyhenne:
            text = self.rootCanvas.create_text(10, y_temp, anchor="nw", text=item,
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
                                                               anchor="w", text="Kokonaispisteet:",
                                                               font=self.perusFontti,
                                                               fill=asetus['fonttiVari'])
        self.virhe_teksti = self.rootCanvas.create_text(500, 400, text='', font=self.virheFontti, fill='red')
        self.pisteiden_lahetys_teksti = self.rootCanvas.create_text(800, gl.versioTekstiY, text='',
                                                                         font=self.verFontti,
                                                                         fill='green')

        self.master.bind('<KeyPress>', self.painettu)
        self.master.bind('<Button-1>', self.hiiren_valinta)

        self.rootCanvas.pack()
        self.pack()
        self.master.bind("<Configure>", self.scale_objects)

    @staticmethod
    def load_font(font_size: int):
        cdef int load_font_size = int(font_size * (asetus['fonttiKoko'] / 100))
        try:
            return tkFont.Font(family=gl.fontti, size=load_font_size)
        except Exception as e:
            print("järjestelmäfontin tuonti epäonnistui", str(e))

        if tkextrafont_available:
            return Font(file="media/SpecialElite-Regular.ttf", family=gl.fontti, size=load_font_size)
        else:
            return tkFont.Font(family="Arial", size=load_font_size)

    def lopeta_peli(self) -> None:
        self.master.destroy()

    def show_settings(self) -> None:
        if self.settings_window is None:
            self.settings_window = AsetuksetIkkuna(self.master)
        else:
            self.settings_window.destroy()
            self.settings_window = None
            return

    def show_lataa_tallenna(self) -> None:
        if self.lataa_tallenna is None:
            self.lataa_tallenna = TallennusLatausIkkuna(self.master, self)
        else:
            self.lataa_tallenna.destroy()
            self.lataa_tallenna = None

    def show_manual(self) -> None:
        if self.manual_window is None:
            self.manual_window = OhjeIkkuna(self.master)
        else:
            self.manual_window.destroy()
            self.manual_window = None

    def painettu(self, event=None) -> None:
        cdef str painallus = event.keysym
        cdef str kirjain = event.char
        cdef dict painallus_valinnat

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

        painallus_valinnat.get(painallus, lambda: self.edit_pelaaja_nimi(kirjain))()
        self.scale_objects() if painallus != 'Escape' else None

    @staticmethod
    def liiku_oikealle() -> None:
        gl.valintaSijaintiX += gl.sarakkeenLeveys
        gl.valittu += 1
        if gl.valittu > gl.pelaajaMaara:
            gl.valintaSijaintiX = gl.sijaintiXOletus
            gl.valittu = 0

    @staticmethod
    def liiku_vasemmalle() -> None:
        gl.valintaSijaintiX -= gl.sarakkeenLeveys
        gl.valittu -= 1
        if gl.valittu < 0:
            gl.valintaSijaintiX = gl.sijaintiXOletus + (gl.pelaajaMaara * gl.sarakkeenLeveys)
            gl.valittu = gl.pelaajaMaara

    @staticmethod
    def liiku_ylos() -> None:
        if gl.kierrosNumero == 0:
            gl.jakaja -= 1
            if gl.jakaja < 0:
                gl.jakaja = gl.pelaajaMaara
            for item in range(len(pelaaja)):
                if item == gl.jakaja:
                    pelaaja[item]['jakaja'] = True
                else:
                    pelaaja[item]['jakaja'] = False
        elif gl.kierrosNumero < 9:
            gl.valittuKierros -= 1
            gl.valintaSijaintiY -= gl.rivivali
            if gl.valittuKierros < 1:
                gl.valittuKierros = gl.kierrosNumero
                gl.valintaSijaintiY = gl.sijaintiYOletus + (gl.kierrosNumero * gl.rivivali)
        else:
            gl.valittuKierros -= 1
            gl.valintaSijaintiY -= gl.rivivali
            if gl.valittuKierros < 1:
                gl.valittuKierros = 8
                gl.valintaSijaintiY = gl.sijaintiYOletus + (8 * gl.rivivali)

    @staticmethod
    def liiku_alas() -> None:
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
        cdef int item
        cdef str temp_nimi
        if gl.valittuKierros == 0:
            if kirjain == "\b":
                temp_nimi = pelaaja[gl.valittu]['nimi'][:-1]
            else:
                temp_nimi = pelaaja[gl.valittu]['nimi'] + kirjain
                if len(temp_nimi) > 12:
                    temp_nimi = temp_nimi[:-1]

            pelaaja[gl.valittu]['nimi'] = temp_nimi
            self.rootCanvas.itemconfig(self.pelaajaText[gl.valittu], text=temp_nimi)
            self.rootCanvas.itemconfig(self.pelaajaNimi[gl.valittu], text=temp_nimi)
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
            if gl.kierrosNumero == 9:
                self.laheta_pisteet_taustalla()

    def hiiren_valinta(self, event: tk.Event) -> None:
        cdef int hiiri_x = event.x
        cdef int hiiri_y = event.y
        cdef int ikkuna_x = self.master.winfo_width()
        cdef int ikkuna_y = self.master.winfo_height()
        cdef int sijainti_x_oletus_scaled = ikkuna_x * (gl.sijaintiXOletus / gl.ikkunaXScale)
        cdef int sijainti_y_oletus_scaled = ikkuna_y * ((gl.sijaintiYOletus - gl.rivivali) / gl.ikkunaYScale)
        cdef int sarakkeen_leveys_scaled = ikkuna_x * (gl.sarakkeenLeveys / gl.ikkunaXScale)
        cdef int koko_piste_marginaali_scaled = ikkuna_y * ((gl.kokoPisteMarginaali + (gl.rivivali / 2)) / gl.ikkunaYScale)
        cdef int vasen_koko_piste_marginaali_scaled = ikkuna_x * (gl.vasenKokoPisteMarginaali / gl.ikkunaXScale)
        cdef int rivivali_scaled = ikkuna_y * (gl.rivivali / gl.ikkunaYScale)

        if hiiri_x > sijainti_x_oletus_scaled and koko_piste_marginaali_scaled > hiiri_y > sijainti_y_oletus_scaled:
            temp_x = sijainti_x_oletus_scaled + sarakkeen_leveys_scaled
            for integer in range(gl.pelaajaMaara + 1):
                if hiiri_x < temp_x:
                    temp_y = sijainti_y_oletus_scaled + rivivali_scaled
                    for kierros_int in range(gl.kierrosNumero + 1):
                        if hiiri_y < temp_y:
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
            temp_y = koko_piste_marginaali_scaled + rivivali_scaled
            for integer in range(gl.pelaajaMaara + 1):
                if hiiri_y < temp_y:
                    pelaajan_nimi = self.rootCanvas.itemcget(self.pelaajaText[integer], 'text')
                    for item in range(len(pelaaja)):
                        if pelaaja[item]['nimi'] == pelaajan_nimi:
                            gl.jakaja = item
                    gl.jakaja = item
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
        if gl.virhe:
            self.virheen_tulostus(gl.virhe)
            return

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
                self.laheta_pisteet_taustalla()
        else:
            self.uusi_peli()
        self.scale_objects()

    def jarjesta_pelaajat(self) -> None:
        sorted_pelaaja = sorted(pelaaja, key=lambda x: int(x['kokonaisPisteet']))
        for sija, item in enumerate(sorted_pelaaja, start=1):
            item['sijoitus'] = str(sija)

        for item in range(len(self.pelaajaText)):
            self.rootCanvas.itemconfig(self.pelaajaText[item], text=sorted_pelaaja[item]['nimi'])
            self.rootCanvas.itemconfig(self.kokoPisteTeksti[item], text=sorted_pelaaja[item]['kokonaisPisteet'])

    def pisteiden_laskenta(self) -> None:
        cdef int koko_piste
        cdef int item2
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
                    temp_pelaaja = {'nimi': pelaaja_nimet_temp[player], 'pisteet': ['', '', '', '', '', '', ''],
                                    'jakaja': True}
                else:
                    temp_pelaaja = {'nimi': pelaaja_nimet_temp[player], 'pisteet': ['', '', '', '', '', '', ''],
                                    'jakaja': False}
            else:
                if player == 0:
                    temp_pelaaja = {'nimi': pelaaja_nimet_temp[player], 'pisteet': ['', '', '', '', '', '', ''],
                                    'jakaja': True}
                else:
                    temp_pelaaja = {'nimi': pelaaja_nimet_temp[player], 'pisteet': ['', '', '', '', '', '', ''],
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
                                                    text=pelaaja[item]['nimi'], font=self.perusFontti,
                                                    fill=asetus['fonttiVari'], anchor='center')
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
                                                               anchor="w", text="Kokonaispisteet:",
                                                               font=self.perusFontti,
                                                               fill=asetus['fonttiVari'])
        self.virhe_teksti = self.rootCanvas.create_text(500, 400, text='', font=self.virheFontti, fill='red')
        self.pisteiden_lahetys_teksti = self.rootCanvas.create_text(800, gl.versioTekstiY, text='',
                                                                         font=self.verFontti,
                                                                         fill='green')
        if pisteiden_lahetys_teksti_nakyvissa:
            self.rootCanvas.itemconfig(self.pisteiden_lahetys_teksti, text='Lähetetään pisteitä')
        self.scale_objects()

    def laheta_pisteet_taustalla(self) -> None:
        global pisteiden_lahetys_teksti_nakyvissa
        if asetus['datanLahetys']:
            self.rootCanvas.itemconfig(self.pisteiden_lahetys_teksti, text='Lähetetään pisteitä')
            pisteiden_lahetys_teksti_nakyvissa = True
            self.scale_objects()
            pisteiden_lahetys = threading.Thread(target=self.laheta_pisteet_palvelimelle)
            pisteiden_lahetys.start()

    def laheta_pisteet_palvelimelle(self) -> None:
        global pisteiden_lahetys_teksti_nakyvissa
        global api_key
        print('olet lähettämässä pisteitä palvelimelle')
        if api_key == "pisteenlaskija2024versio3" or "" or None:
            server_url: str = f'http://{asetus["palvelinOsoite"]}/api/data'
            print("Api kysely")
            print(f'Vanha Api avain: {api_key}')

            try:
                response = requests.post(server_url, headers={'versio': versioNumero, 'X-API-KEY': api_key},
                                         timeout=10)
                if response.status_code == 200:
                    api_key = response.text
                print(f'Uusi Api avain: {api_key}')
                with open('media/settings.json', 'r') as f:
                    api_temp = load(f)
                api_temp['api'] = api_key
                with open('media/settings.json', 'w') as f:
                    dump(api_temp, f)
            except Exception as e:
                print(e)

        if api_key != "pisteenlaskija2024versio3" or "" or None:
            game_id = self.create_gameid()
            self.pisteiden_laskenta()
            try:
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

                tiedosto_nimi = f'statistic/{game_id}.json'
                with open(tiedosto_nimi, 'w') as file:
                    dump(tallennettava_tiedosto, file)

                lahetettava_tiedosto = {
                    'data': tallennettava_tiedosto,
                    'name': game_id
                }
                server_url: str = f'http://{asetus["palvelinOsoite"]}/api/data'
                lahetettava_tiedosto_json = dumps(lahetettava_tiedosto)
            except Exception as e:
                mb.showinfo(title='Jotain meni vikaan', message=f'tiedoston muodostuksessa ilmeni virhe {e}')
                return
            try:
                response = requests.post(server_url, data=lahetettava_tiedosto_json, headers={
                    'Content-Type': 'application/json', 'X-API-KEY': api_key})
                if response.status_code == 200:
                    os.remove(tiedosto_nimi)
                    print("pisteet lähetetty")
                    self.rootCanvas.itemconfig(self.pisteiden_lahetys_teksti, text='')
                else:
                    print(response.status_code)
                    self.rootCanvas.itemconfig(self.pisteiden_lahetys_teksti,
                                               text=f'palvelin yhteydessä virhe {response.status_code}')

                self.scale_objects()
            except Exception as e:
                print(e)
                mb.showinfo('Virhe palvelinyhteydessä', f'Palvelin yhteydessä ilmaantui virhe {e}')
            for file in os.listdir('statistic'):
                lahetys = self.laheta_odottavat_pisteet(file)
                if lahetys != '200':
                    print(lahetys)
        pisteiden_lahetys_teksti_nakyvissa = False

    @staticmethod
    def laheta_odottavat_pisteet(tiedosto) -> str:
        global api_key
        with open(f'statistic/{tiedosto}', 'r') as file:
            data = load(file)
        tiedosto_nimi = os.path.splitext(tiedosto)[0]
        lahetettava_tiedosto = {'data': data, 'name': tiedosto_nimi}
        server_url: str = f'http://{asetus["palvelinOsoite"]}/api/data'
        lahetettava_tiedosto_json = dumps(lahetettava_tiedosto)
        try:
            response = requests.post(server_url, data=lahetettava_tiedosto_json, headers={
                'Content-Type': 'application/json', 'X-API-KEY': api_key})
            if response.status_code == 200:
                os.remove(f'statistic/{tiedosto_nimi}.json')
            return str(response.status_code)
        except Exception as e:
            print(e)
            return str(e)

    @staticmethod
    def create_gameid() -> str:
        aika_nyt = datetime.datetime.now()
        return aika_nyt.strftime("%Y%m%d%H%M%S")

    @staticmethod
    def virheen_tarkistus() -> None:
        global virhe
        virhe = 0
        if gl.kierrosNumero == 0:
            if gl.pelaajaMaara < 3:
                virhe = 3
            pelaaja_temp = [item['nimi'] for item in pelaaja]
            pelaaja_temp = [item for item in pelaaja_temp if item]
            pelaaja_temp_set = set(pelaaja_temp)
            if len(pelaaja_temp) > len(pelaaja_temp_set):
                virhe = 4

        else:
            kierros_pisteet_temp = [item['pisteet'] for item in pelaaja]
            kierros_pisteet_temp = [[row[z] for row in kierros_pisteet_temp] for z
                                    in range(len(kierros_pisteet_temp[0]))]
            kierros_pisteet_temp = kierros_pisteet_temp[:gl.kierrosNumero]
            for kierros_nyt in kierros_pisteet_temp:
                voittaja = sum(item == '' or item == '0' for item in kierros_nyt)
                if voittaja > 1:
                    virhe = 1
                elif voittaja < 1:
                    virhe = 2
                for piste in kierros_nyt:
                    if piste == '':
                        piste = 0
                    if int(piste) > 200 or int(piste) == 1:
                        virhe = 2

    def virheen_tulostus(self, virhe_numero: int) -> None:
        valinnat = {
            1: 'Et ole syöttänyt kaikille pisteitä',
            2: 'Tarkista pisteet',
            3: 'Pelaajia on liian vähän',
            4: 'Nimet ovat liian samanlaiset'
        }
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
        cdef int ikkuna_leveys_scaled = self.master.winfo_width()
        cdef int ikkuna_korkeus_scaled = self.master.winfo_height()
        cdef int eka_kierros_y_location_scaled = ikkuna_korkeus_scaled * (gl.ekaKierrosYLocation / gl.ikkunaYScale)
        cdef int koko_piste_marginaali_scaled = ikkuna_korkeus_scaled * (gl.kokoPisteMarginaali / gl.ikkunaYScale)
        cdef int vasen_marginaali_scaled = ikkuna_leveys_scaled * (gl.vasenMarginaali / gl.ikkunaXScale)
        cdef int vasen_kokopiste_nimi_marginaali_scaled = (ikkuna_leveys_scaled *
                                                  (gl.vasenKokoPisteNimiMarginaali / gl.ikkunaXScale))
        cdef int vasen_kokopiste_piste_marginaali_scaled = ikkuna_leveys_scaled * (gl.vasenKokoPisteMarginaali / gl.ikkunaXScale)
        cdef int fontti_koko_iso_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoIso / gl.ikkunaYScale)
        cdef int fontti_koko_scaled = ikkuna_korkeus_scaled * (gl.fonttiKoko / gl.ikkunaYScale)
        cdef int fontti_koko_pieni_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoPieni / gl.ikkunaYScale)
        cdef int fontti_koko_ver_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoVer / gl.ikkunaYScale)
        cdef int fontti_koko_j_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoJ / gl.ikkunaYScale)
        cdef int fontti_koko_virhe_scaled = ikkuna_korkeus_scaled * (gl.fonttiKokoVirhe / gl.ikkunaYScale)
        cdef int valinta_sijainti_x_scaled = ikkuna_leveys_scaled * (gl.valintaSijaintiX / gl.ikkunaXScale)
        cdef int valinta_sijainti_y_scaled = ikkuna_korkeus_scaled * (gl.valintaSijaintiY / gl.ikkunaYScale)
        cdef int nimi_sijainti_y_scaled = ikkuna_korkeus_scaled * (gl.sijaintiYOletus / gl.ikkunaYScale)
        cdef int sarakkeen_leveys_scaled = ikkuna_leveys_scaled * (gl.sarakkeenLeveys / gl.ikkunaXScale)
        cdef int sijainti_x_oletus_scaled = ikkuna_leveys_scaled * (gl.sijaintiXOletus / gl.ikkunaXScale)
        cdef int virheen_sijainti_x_scaled = ikkuna_leveys_scaled * (gl.virheenSijaintiX / gl.ikkunaXScale)
        cdef int virheen_sijainti_y_scaled = ikkuna_korkeus_scaled * (gl.virheenSijaintiY / gl.ikkunaYScale)
        cdef int kierros_nimi_x_scaled = ikkuna_leveys_scaled * (gl.kierrosNimiX / gl.ikkunaXScale)
        cdef int kierros_nimi_y_scaled = ikkuna_korkeus_scaled * (gl.kierrosNimiY / gl.ikkunaYScale)
        cdef int ohje_teksti_x_scaled = ikkuna_leveys_scaled * (gl.ohjeTekstiX / gl.ikkunaXScale)
        cdef int ohje_teksti_y_scaled = ikkuna_korkeus_scaled * (gl.ohjeTekstiY / gl.ikkunaYScale)
        cdef int jakajan_merkki_x_scaled = ikkuna_leveys_scaled * (gl.fonttiKokoJ / gl.ikkunaXScale)
        cdef int versio_teksti_x_scaled = ikkuna_leveys_scaled * (gl.versioTekstiX / gl.ikkunaXScale)
        cdef int versio_teksti_y_scaled = ikkuna_korkeus_scaled * (gl.versioTekstiY / gl.ikkunaYScale)
        cdef int rivivali_scaled = ikkuna_korkeus_scaled * (gl.rivivali / gl.ikkunaYScale)

        self.perusFontti = self.load_font(fontti_koko_scaled)
        self.isoFontti = self.load_font(fontti_koko_iso_scaled)
        self.pieniFontti = self.load_font(fontti_koko_pieni_scaled)
        self.verFontti = self.load_font(fontti_koko_ver_scaled)
        self.J_Fontti = self.load_font(fontti_koko_j_scaled)
        self.virheFontti = self.load_font(fontti_koko_virhe_scaled)

        cdef int y_temp = eka_kierros_y_location_scaled
        cdef int item
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
                                   nimi_sijainti_y_scaled - (fontti_koko_scaled / 2))
            self.rootCanvas.itemconfig(self.pelaajaNimi[item], font=self.perusFontti, fill=asetus['fonttiVari'])
            x_temp += sarakkeen_leveys_scaled

        x_temp = sijainti_x_oletus_scaled + (sarakkeen_leveys_scaled / 2)
        y_temp = eka_kierros_y_location_scaled - rivivali_scaled
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
        self.rootCanvas.coords(self.pisteiden_lahetys_teksti, virheen_sijainti_x_scaled, versio_teksti_y_scaled)
        self.rootCanvas.itemconfig(self.pisteiden_lahetys_teksti, font=fontti_koko_ver_scaled)
        self.rootCanvas.configure(height=ikkuna_korkeus_scaled, width=ikkuna_leveys_scaled)
        self.taustakuva_resized = self.taustakuva_original.resize((ikkuna_leveys_scaled, ikkuna_korkeus_scaled),
                                                                 Image.Resampling.NEAREST)
        self.uusi_tausta = ImageTk.PhotoImage(self.taustakuva_resized)
        self.rootCanvas.itemconfig(self.muokattu_tausta, image=self.uusi_tausta)

# Super simple window creation, which get all objects from Pisteenlaskija -class
root = tk.Tk()
tallennus_nimet()
root.title("Sanghai Pisteenlaskija")
root.geometry("1280x720")
pisteiden_lahetys_teksti_nakyvissa = False

asetus: dict = lue_asetukset()
api_key = asetus['api']
pelaaja = [{
    'nimi': '',
    'pisteet': ['', '', '', '', '', '', ''],
    'jakaja': pelaaja_numero == 0
} for pelaaja_numero in range(gl.pelaajaMaara + 1)]

app = PisteenlaskijaUI(root)
root.mainloop()
