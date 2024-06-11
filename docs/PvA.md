# Individueel Project PvA
**Jader Vulcano 2174242**

## Introductie

Voor het individueel project heb ik besloten om een digitale pedal effect board te ontwikkelen. Deze zal gebruik maken van OpenCL om de audio filters uit te rekenen. De filters zullen eerst worden ontwikkeld in MATLAB en daarna geoptimaliseerd met OpenCL. 

De applicatie zal gebruik maken van DearPyGui om een GUI te maken. De GUI zal de gebruiker in staat stellen om verschillende effecten toe te voegen aan de audio. De effecten zullen worden toegevoegd aan een effect chain. De effect chain zal de audio door de effecten heen sturen en de output van de effect chain zal worden afgespeeld. 

De applicatie zal in de vorm zijn van een node editor. Hierin zal elk effect beschikbaar zijn als een node. Ook zal er een visualisatie node beschikbaar zijn. Deze kan geplaatst worden op elk punt in de effect chain. 

De applicatie zal geschreven worden in python en gebruik maken van de volgende libraries:
- OpenCL
- DearPyGui
- PyAudio
- NumPy

Ook is het mogelijk dat er andere libraries worden gebruikt voor het berekenen van de audio filters. Deze zullen uit het onderzoek rollen.

## Planning

Eerst zal er een onderzoek worden gedaan naar de verschillende audio filters die mogelijk zijn. Hierbij zal er worden gekeken naar de verschillende effecten die mogelijk zijn en hoe deze kunnen worden geïmplementeerd. 

Daarna zal er een prototype worden gemaakt in MATLAB. Hierin zullen de effecten worden geïmplementeerd en getest. Deze zullen dan worden geoptimaliseerd met OpenCL.

* v0.1: los werkend: node editor, audio input, opencl werkend
* v0.2: gain node in node editor

## Logboek

| Datum | Onderwerp                 | Tijd  |
| ----- | ------------------------- | ----- |
| 08/05 | Onderzoek opencl          | 2 uur |
| 15/05 | Onderzoek dpg             | 2 uur |
| 22/05 | Onderzoek numpy en opencl | 2 uur |
| 27/05 | Onderzoek ruis            | 6 uur |

- [ ] fix live input
- [ ] add adding nodes
- [ ] fix noise when using filter

### 15/05

* meerdere problemen met het data formaat, deze zijn opgelost

### 22/05

Ik loop tegen een onverwacht noise probleem aan na het implementeren van een simpele gain filter. Dit is op commit `2a9331f`. De gain heeft een factor 1. Maar ik krijg toch een onverklaarbare ruis in de output file (`output_gain.wav`). Ik zie na het inlezen van de file dat er in het `audio_data` bestand `nan` waardes zitten. Dit is direct na het inlezen van het `.wav` bestand. Ik weet dat alle parameters (sample rate, channels, etc) goed zijn. Ik heb dit gecontroleerd door de `audio_data` weer te schrijven naar een nieuw `.wav` bestand. Dit bestand klinkt precies zoals het origineel.

Uiteindelijk was het probleem dat de wave file values zijn encoded als 16 bit integers. Met dat opgelost kan een basis ui in dpg gerealiseerd worden.

## 11/06



## Eindproduct

In de applicatie zal je:
  - een node editor hebben waar je:
    - nodes kan toevoegen
    - nodes kan verbinden
    - nodes kan verwijderen
  - een node hebben voor input van de audio
    - deze input is een live audio source op het systeem
  - er zullen meerdere effecten beschikbaar zijn:
    - delay
    - lowpass filter
    - highpass filter
    - bandpass filter
    - visualisatie
  - de effecten zullen worden geoptimaliseerd met OpenCL
  - de effecten zullen worden getest in MATLAB
  - de effecten zullen worden getest in de applicatie
   