# 🖐️ MagicHand 👊

**MagicHand** is een  gebruiksvriendelijk systeem waarmee je  VLC - mediaspeler kunt bedienen met alleen je handgebaren en  via je webcam. Hiermee kan je dan gewoon  je hand opsteken en bedienen , zonder ingewikkelde afstandsbedieningen of toetsenborden 

---

## Wat Heb Je Nodig

- Python 3.8  of hoger
- Een werkende webcam
- VLC - mediaspeler
-  Muziek - of videobestanden om af te spelen

---

## Setup

### 1. Download de bestanden
 Zorg dat deze bestanden in 1  map staan :

📁 MagicHand/
- `app.py` - Web  app interface
- `main.py` - Hand  detectie
- `media_controller.py` -  Stuurt commando 's naar  VLC
- `config.json` -  Instelingen
- `requirements.txt` -  Benodigde pakketten
- `run.bat` - Start de app met 1  klik ( Windows)
- `magichand_logo.png` # Je eigen logo

### 2. Python Omgeving instellen

#### Wat is  een virtuele omgeving ?
Een virtuele omgeving  zorgt ervoor dat de  pakketten voor dit project  niet door elkaar lopen met andere projecten op je computer .

#### a. Open Terminal
Open PowerShell ( Windows ) of Terminal ( Mac/Linux) in je projectmap :
cd C:\jouw-map

#### b.  Maak een virtuele  omgeving
python -m venv venv

#### c. Activeer  de omgeving
**Windows:** `venv\Scripts\activate` or `venv\Scripts\Activate.ps1`  
**Mac/Linux:** `source venv/bin/activate`

### 3.  Installeer de benodigde pakketten
pip install -r requirements.txt

### 4. Zet je muziek klaar
Maak een  map music in  je projectmap  en zet  daar je bestanden in :

📁 MagicHand/
  ├── 📁 music/
  │    ├── track1.mp4
  │    ├── track2.mp4
  │    └── ...
  ├── main.py
  ├── app.py
  └── ...

---

##  Hoe Gebruik je MagicHand ?

###  Web App 

1. Dubbelklik op run.bat
2.  Je browser opent automatisch
3. Open VLC  handmatig en laad je muziek/video 's
4. Klik op  " Start Camera "  in de web app
5. Maak gebaren  om VLC te bedienen 
6. Klik op " Stop Camera " of sluit  je browser  om te stoppen

## Gebaren Overzicht

| Gebaar | Wat het doet |
|---------|---------|
| ✋ High-Five | Play / Pauze |
| 👊 Vuist | Stop |
|  ✌️ 2 Vingers | Volgende track |
| 🤟 3  Vingers | Vorige track |
| 🤏 Duim  Wijsvinger Knijpen | Volume omhoog / omlaag |

**Tip:**  Hoe verder je duim en  wijsvinger uit elkaar staan , hoe harder het volume

## Instellingen Aanpassen

**Je kunt MagicHand eenvoudig aanpassen via de web app zelf:**

| Wat kun je aanpassen ? | Waar ? |
|---------|---------|
| 📷 Camera ( ingebouwd/extern ) | Instellingen ==> Camera |
| 🔍 Schermgrootte  | Instellingen  ==> UI Schaalgrootte |
| ⏱️  Reactiesnelheid van gebaren | Instellingen ==> Wachtijd |
| 🤏 Gevoeligheid van  volume knijpen | Instelingen == >  Kneep Instellingen |
|  ✌️ Welk gebaar welke actie doet | Instellingen  ==> Gebaar voor Actie |

**Tip:**  Alle  instellingen  worden automatisch opgeslagen in config.json .

## Problemen Oplossen

| Probleem | Oplossing |
|---------|---------|
| Geen  camera beeld | Controleer of je webcam is aangesloten . Wijzig device_id in config.json van 0 naar 1 |
| VLC reageert niet  | Klik eerst op het VLC - venster zodat het actief is |
|  Gebaren worden niet herkend | Zorg voor goed licht  op je hand. Sta op armlengte afstand . Houd  gebaren even vast |
| App start niet | Instellingen ==>  Controleer of je venv hebt geactiveerd en pip install -r requirements.txt hebt gedaan  |

## Extra Tips voor Gebruikers
- **Licht:**  Zorg voor goed licht op je hand , anders ziet de camera je gebaren niet goed
- **Afstand:** Ga op  ongeveer armlengte afstand  van de camera staan
-  **Geduld:** Houd een gebaar even vast voor 1-2 seconden  voordat het systeem  reageert
- **VLC:** Vergeet  niet om op het VLC - venster te klikken  voordat je gebaren maakt

---

**MagicHand is ontworpen  om media bedienen toegankelijk te maken voor iedereen.  Het ontwerp is speciaal afgestemd op de behoeften van ouderen en mensen met een fysieke of cognitieve beperking .**
