# Namn på projektet

Solvely - Algebraiska Lösningar

Elias Bryant, Alfred Cardell, Timothy Andersson, Dayvid Grönqvist, Nathalie Chacana, Mia Radojcic

### Tävlar i kategori: 

Alla

## Projekt & Teknisk- beskrivning 
Vi har skapat en interaktiv matte webbsida som inte bara är till för att räkna ut svar, utan även för att hjälpa användaren att förstå hur matematiska problem löses. Vårt fokus har legat på användarvänlighet och lärande, där webbsidan ska fungera som ett pedagogiskt stöd snarare än en vanlig miniräknare.
Användaren kan skriva in valfri matteuppgift och välja mellan två olika lägen. I svar-läget ges ett snabbt slutresultat, medan förenkla-läget visar en tydlig steg-för-steg-lösning med förklaringar till varje moment. Detta gör att användaren kan följa tankegången bakom lösningen och på så sätt lära sig hur uppgiften ska lösas, inte bara vilket svar den ger.
För att stödja inlärningen ytterligare finns en digital notebook där användaren kan spara bra förklaringar och lösningar. Notebooken kan sedan användas som referens vid framtida uppgifter. Webbsidan har även stöd för flera språk samt både ljust och mörkt läge, vilket gör den tillgänglig för fler användare och anpassningsbar efter personliga preferenser

Webbsidan är uppbyggd med HTML, CSS, JavaScript och Python som tillsammans gör att både utseende och funktion fungerar som helhet. HTML används för att skapa strukturen på sidan, såsom knappar, texter och inmatningsfält som användaren interagerar med. CSS används för att utforma designen och bestämma färger, layout och utseende, inklusive stöd för både ljust och mörkt läge. JavaScript används för att ge sidan funktionalitet genom att hantera knapptryckningar, språkval och automatiska uppdateringar av innehållet när användaren skriver in en matteuppgift eller byter inställningar. Själva matematiken hanteras i en Python-fil (main.py), där användarens inmatning tas emot, bearbetas och omvandlas till antingen ett färdigt svar eller en steg-för-steg-lösning som sedan skickas tillbaka till webbsidan för visning.
### Externt producerade komponenter

JS
I Javascript har vi använt oss att ge funktioner för knapparna, texterna(som är nummer) och labels. Till exempel ha mörkt läge eller multi språk som ändrats i alla texter på språket du valt. Javascript hjälper också att uppdatera sidan automatiskt när vi trycker på knapparna eller skickar in numret för resultatet.

Python
Vi har använt oss av python för våran backend med hjälp av Sympy, LaTex, KaTex, Fast API, och Uvicorn dem hjälper att förstå matten som inputs, och översätter det till ett finare sett att presentera problem i steg och tolka det som görs. Vad som görs är att vi använder Python som backend med FastAPI för att ta emot användarens matteproblem och skicka tillbaka en steg-för-steg-lösning. SymPy tolkar inputen symboliskt, förenklar och löser (linjära och andragradsekvationer), och allt formateras som LaTeX för tydlig presentation. Frontend renderar LaTeX med KaTeX, så varje steg visas snyggt i webbläsaren. Servern körs lokalt med Uvicorn. 

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
