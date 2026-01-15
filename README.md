
readme.MD


# Namn på projektet

Solvely - Algebraiska Lösningar

Elias Bryant, Alfred Cardell, Timothy Andersson, Dayvid Grönqvist, Nathalie Chacana, Mia Radojcic

### Tävlar i kategori: 

Alla

## Projekt & Teknisk- beskrivning

Här skriver ni vad ni har gjort, försök att formulera det så att det blir relevant för kategorin ni tänker att ni tävlar i.
T.ex. om ni har fokuserat på just UI/UX så är det mer relevant än om ni 

Det ska även ingå en tekniskt beskrivning, där ni beskriver en eller flera tekniska lösningar i projektet. Ni skall beskriva funktionen av den tekniska lösningen och hur den används i projektet. Ju tydligare beskrivning desto enklare att bedöma den tekniska lösningen. Beskrivningen skall vara förståelig även för personer som inte kan programmera.

### Externt producerade komponenter

Vi har använt oss av python för våran backend med hjälp av Sympy, LaTex, KaTex, och Fast API, dem hjälper att förstå matten som inputs, och översätter det till ett finare sett att presentera problem i steg och tolka det som görs. Sedan används Uvicorn

### Install

#  HUR MAN KÖR PROJEKTET 
# 1. Skapa och aktivera virtuell miljö:
#    Windows:
#      py -m venv .venv
#      .\.venv\Scripts\activate
#
# 2. Installera beroenden:
#    pip install fastapi uvicorn sympy pydantic
#
# 3. Kör servern:
#    uvicorn main:app --reload
#
# 4. Öppna i webbläsaren:
#    http://127.0.0.1:8000/
