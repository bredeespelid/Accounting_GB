Dette skriptet automatiserer prosessen med å lage en pivot-tabell og søkefunksjon i et Excel-arbeidsbok. Skriptet omdøper det første regnearket, oppretter en tabell med spesifikke data og legger til formler for enkel avstemming og søking.

Funksjonalitet
Skriptet utfører følgende operasjoner:

Omdøp første regneark: Skriptet endrer navnet på det første regnearket til "Input".

Opprett en ny tabell: Oppretter en ny tabell basert på det brukte området i "Input"-arket og navngir tabellen "avstemming".

Legg til en ny kolonne med formel:

Skriptet legger til en ny kolonne "posenummer" i tabellen.
Setter en formel for å ekstrahere posenummer fra en tekststreng i kolonnen "Fritekst".
Formater datoer: Setter datoformatet for kolonnene D og E til "d/m/yy".

Opprett en pivot-tabell:

Oppretter et nytt regneark kalt "Oversikt".
Lager en pivot-tabell basert på dataene i "avstemming"-tabellen.
Opprett søkefunksjon:

Oppretter et nytt regneark kalt "Søk".
Bruker UNIQUE-funksjonen for å liste unike posenumre fra "avstemming"-tabellen.
Setter opp datavalidering i celle C3 for å lage en rullegardinliste over posenumre.
Bruker VSTACK og FILTER formler for å vise data relatert til valgt posenummer.
