import tkinter as tk
from tkinter.font import Font

pelaajaMaara = 5
jakajanSijainti = 600
jakaja = 0
pisteMaara = 0
valittu = 0
kierrosNumero = 0
valittuKierros = 0
hiiri = 0
virhe = False
ohjeet = False
tallennuksenKasittely = False
laatikkoX = 0
laatikkoY = 0
laatikonLeveys = 200
syotto = False
sarakkeenLeveys = 200

fonttiKoko = 57
fonttiKokoIso = 95
fonttiKokoPieni = 55
fonttiKokoVer = 20
ikkunaX = 1280
ikkunaY = 720
vasenMarginaali = 5
ylaMarginaali = 50
kokoPisteMarginaali = 423
sijaintiXOletus = 170
sijaintiYOletus = 50
kierrosMaara = 8
tallennuspaikat = 9
fonttiVari = '#383eB8'

kierros = ['Kirjoita pelaajien nimet', 'Kahdet kolmoset', 'Suora ja kolmoset', 'Kaksi suoraa',
           'Kolmet kolmoset', 'Suora ja kahdet kolmoset', 'Kaksi suoraa ja kolmoset',
           'kolme suoraa', 'Neljät kolmoset']

kierrosLyhenne = ['2xK', 'S&K', '2xS', '3xK', 'S&2xK', '2xS&K', '3xS', '4xK']
