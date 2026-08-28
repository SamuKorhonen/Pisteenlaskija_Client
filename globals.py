pelaajaMaara: int = 6
jakajanSijainti: int = 600
jakaja: int = 0
pisteMaara: int = 0
valittu: int = 0
kierrosNumero: int = 0
valittuKierros: int = 0
# hiiri: int = 0
virhe: int = 0
# ohjeet: int = False
# laatikkoX: int = 0
# laatikkoY: int = 0
# laatikonLeveys: int = 200
# syotto = False


fonttiKoko: int = 40
fonttiKokoIso: int = 78
fonttiKokoVirhe: int = 45
fonttiKokoPieni: int = 30
fonttiKokoVer: int = 18
fonttiKokoJ: int = 30
ikkunaXScale: int = 1920
ikkunaYScale: int = 1080
vasenMarginaali: int = 10
vasenKokoPisteNimiMarginaali: int = 55
vasenKokoPisteMarginaali: int = 400
ylaMarginaali: int = 45
kokoPisteMarginaali: int = 650
sijaintiXOletus: int = 170
sijaintiYOletus: int = 96
kierrosMaara: int = 8
tallennuspaikat: int = 3
tallennusNimi: list[str] = []
fonttiVari: str = '#383eB8'
virheenSijaintiX: int = 1250
virheenSijaintiY: int = 928
kierrosNimiX: int = 1250
kierrosNimiY: int = 675
ohjeTekstiX: int = 1250
ohjeTekstiY: int = 750
versioTekstiX: int = 1800
versioTekstiY: int = 1050
fontti: str = 'Special Elite'
rivivali: int = 57

sarakkeenLeveys: float = (ikkunaXScale - sijaintiXOletus) / (pelaajaMaara + 1)

valintaSijaintiY: int = sijaintiYOletus
valintaSijaintiX: int = sijaintiXOletus

ikkuna_leveys: int = 1280
ikkuna_korkeus: int = 720
ekaKierrosYLocation: int = 110

kierros: list[str] = ['Kirjoita pelaajien nimet', 'Kahdet kolmoset', 'Suora ja kolmoset', 'Kaksi suoraa',
                      'Kolmet kolmoset', 'Suora ja kahdet kolmoset', 'Kaksi suoraa ja kolmoset',
                      'kolme suoraa', 'Neljät kolmoset', 'Peli loppu']

kierrosLyhenne: list[str] = ['2xK', 'S&K', '2xS', '3xK', 'S&2xK', '2xS&K', '3xS', '4xK']
peliLoppuTekstit: list[str] = ['Peli Loppu!', 'Voittajalle onnittelut', 'ja häviäjille parempaa onnea ensi kertaan',
                               'Aloita uusi peli painamalla \'Enter\'']

# fontti = 'Arial'
