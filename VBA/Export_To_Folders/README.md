Dette VBA-skriptet er laget for å automatisere eksporten av data fra et Excel-ark til individuelle CSV-filer lagret i spesifikke undermapper. Hver kolonne i Excel-arket vil bli lagret i sin egen CSV-fil i en mappe som er navngitt etter kolonneoverskriften.

Forutsetninger
For å bruke dette skriptet trenger du:

Microsoft Excel installert på din datamaskin.
Data som starter fra kolonne B i Excel-arket (du kan justere dette i henhold til dine faktiske data).
Funksjonalitet
Skriptet utfører følgende operasjoner:

Definer hovedmappe: Brukeren må angi hovedmappen der CSV-filene vil bli lagret.

Definer dataområde: Skriptet setter området for dataene som starter fra kolonne B.

Løkke gjennom overskrifter: Skriptet går gjennom hver celle i den første raden (overskriftene).

Tøm tidligere data: For hver kolonneoverskrift, tømmer skriptet tidligere data i kolonnen.

Løkke gjennom data: Skriptet går gjennom hver celle i det tilsvarende dataområdet, med unntak av overskriftsraden, og legger til celleverdiene i kolonnedataene.

Opprett undermapper: Basert på kolonneoverskriftene, oppretter skriptet undermapper.

Opprett CSV-filer: Skriptet lagrer kolonnedataene i en CSV-fil med et unikt filnavn basert på overskriften.

Melding om fullført prosess: En melding vises når prosessen er fullført.

Bruk
Åpne Excel: Åpne Excel og last inn arbeidsboken som inneholder dataene du vil eksportere.

Åpne VBA-editoren: Trykk Alt + F11 for å åpne VBA-editoren.

Sett inn ny modul: Gå til Insert > Module for å sette inn en ny modul.

Lim inn skriptet: Kopier og lim inn følgende VBA-skript i modulen
