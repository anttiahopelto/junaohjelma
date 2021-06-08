import tkinter.messagebox
import webbrowser
from tkinter import *

import folium
import requests

# Lista jonne junaoliot tallennetaan
juna_lista = []


# Luokka junalle
class Juna:

    # Konstruktorim joka asettaa junan attribuutit
    def __init__(self, numero, lahto, tyyppi, ajossa, peruttu, vauhti, koordinaatit):
        self.numero = numero
        self.lahto = lahto
        self.tyyppi = tyyppi
        self.ajossa = ajossa
        self.peruttu = peruttu
        self.vauhti = vauhti
        self.koordinaatit = koordinaatit


# Hakee oikean juna olion listasta. Purkkaratkaisu, koska tkinterillä ei onnistununt viisaampi ratkaisu
def hae_numerolla(valinta):
    for juna in juna_lista:
        if juna.numero == valinta.get():
            return juna


# Funktio, joka luo pudotusvalikon, josta voi valita aikaisempia hakuja tarkasteltavaksi. Funkiota kutsutaan, joka kerta
# kun käyttäjä painaa hakee jonkin junan tiedot
def luo_pudotusovalikko():
    numero_lista = []
    for juna in juna_lista:
        numero_lista.append(juna.numero)

    valinta = IntVar()
    pudotusValikko = OptionMenu(root, valinta, *numero_lista, command=lambda x: esita_tiedot(hae_numerolla(valinta)))
    pudotusValikko.grid(row=3, column=0)


# Esittää haetun junan tiedot labeleissa
def esita_tiedot(self):
    labelNumero = Label(root, text="Junan numero: " + str(self.numero))
    labelNumero.grid(row=4, column=1)

    labelahto = Label(root, text="Junan lähtöpvm: " + self.lahto)
    labelahto.grid(row=5, column=1)

    labelTyyppi = Label(root, text="Junan tyyppi: " + self.tyyppi)
    labelTyyppi.grid(row=6, column=1)

    labelAjossa = Label(root, text="Ajossa: " + str(self.ajossa))
    labelAjossa.grid(row=7, column=1)

    labelPeruttu = Label(root, text="Peruttu: " + str(self.peruttu))
    labelPeruttu.grid(row=8, column=1)

    labelVauhti = Label(root, text="Nopeus: " + str(self.vauhti) + "km/h")
    labelVauhti.grid(row=9, column=1)

    labelKoordinaatit = Label(root, text="Koordinaatit: " + str(self.koordinaatit[0]) + "," + str(self.koordinaatit[1]))
    labelKoordinaatit.grid(row=10, column=1)


# Hakee  junan nro tekstikentän syötteen
def hae_nro_text():
    syote = nroText.get("1.0", "end-1c")
    nroText.delete('1.0', END)
    return syote


# Hakee junan lähtö pvm tekstikentän syötteen
def hae_pvm_text():
    syote = pvmText.get("1.0", "end-1c")
    pvmText.delete('1.0', END)
    return syote


# Hakee junan tiedot VR:n API:sta ja luo tietoja vastaavan Juna-luokan olion ja lisää sen juna_lista listaan
def hae_junan_tiedot(juna_nro, lahto_pvm):
    if juna_nro == "" or lahto_pvm == "":
        return
    else:
        try:
            url = "https://rata.digitraffic.fi/api/v1/trains/" + lahto_pvm + '/' + juna_nro
            response = requests.get(url).json()

            numero = response[0].get("trainNumber")
            lahto = response[0].get("departureDate")
            tyyppi = response[0].get("trainType")
            ajossa = response[0].get("runningCurrently")
            peruttu = response[0].get("cancelled")

            gpsurl = "https://rata.digitraffic.fi/api/v1/train-locations/latest/" + juna_nro
            responsegps = requests.get(gpsurl).json()
            vauhti = responsegps[0].get("speed")
            koordinaatit = responsegps[0].get("location").get("coordinates")

            juna_lista.append(Juna(numero, lahto, tyyppi, ajossa, peruttu, vauhti, koordinaatit))
            luo_pudotusovalikko()
            esita_tiedot(juna_lista[-1])
        except IndexError:
            tkinter.messagebox.showinfo("Virhe", "Hakemaasi junaa ei löytynyt. Kirjoitithan vain junan numeron esim. 59"
                                                 " Ei IC59")
        except KeyError:
            tkinter.messagebox.showinfo("Virhe", "Hakemaasi junaa ei löytynyt")


# Hakee junien sijainnit ja asettaa Markerit niiden kohdille ja avaa kartan selaimessa.
def avaa_kartta():
    hae_junien_sijainnit()
    webbrowser.open("index.html")


# Silmukka, jossa asetetaan Markerit karttaan junien sijaintien kohdalla,
# ja sijoitetaan Markeriin tekstiksi junan numero
# Koordinaattien leveys- ja pituuspiirit tulevat väärässä järjestyksessä,
# joten käytin nopeaa purkkaratkaisua apumuuttujien kanssa :/
def hae_junien_sijainnit():
    # Alustetaan kartta
    m = folium.Map(location=[63.782486, 27.042476], zoom_start=5.49)
    # VR:n API:n url, josta saadaan kaikkien junien tuoreimmat paikkatiedot
    url = "https://rata.digitraffic.fi/api/v1/train-locations/latest/"
    response = requests.get(url).json()
    for train in response:
        sijainti = train['location']['coordinates']
        junan_nro = train['trainNumber']

        apumuuttuja0 = sijainti[0]
        sijainti[0] = sijainti[1]
        sijainti[1] = apumuuttuja0

        folium.Marker(location=sijainti, popup="Junan numero: " + str(junan_nro),
                      icon=folium.Icon(icon='info-sign')).add_to(m)
    # Tallentaa kartan index.html nimellä samaan kansioon mistä .py ajettu
    m.save("index.html")


# Alustetaan ikkuna
root = Tk()
root.title('Juna sovellus Antti Ahopelto')
root.geometry("480x600")

# Alustetaan tekstiboxit ja niihin liittyvät labelit
nroText = Text(root, width=20, height=1, bg="#dbdbdb")
nroText.grid(row=0, column=1)

pvmText = Text(root, width=20, height=1, bg="#dbdbdb")
pvmText.grid(row=1, column=1)

nroLabel = Label(root, text="Anna junan numero")
nroLabel.grid(row=0, column=0, pady="15")

pvmLabel = Label(root, text="Pvm. muodossa VVVV-KK-PP")
pvmLabel.grid(row=1, column=0)

# Alustetaan nappuloita
haeJunat = Button(root, text="Avaa junakartta", command=avaa_kartta)
haeJunat.grid(row=3, column=2, pady="15")

haeJunanTiedot = Button(root, text="Hae junan tiedot", command=lambda: hae_junan_tiedot(hae_nro_text(), hae_pvm_text()))
haeJunanTiedot.grid(row=3, column=1, pady="15")

root.mainloop()
