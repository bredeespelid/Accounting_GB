Dette skriptet automatisk logger inn på en passordbeskyttet nettside, lar brukeren velge en eller flere "merchants" (selgere), og deretter velge måneder for hvilke rapporter som skal lastes ned. Det oppretter en ny nedlastingsmappe basert på brukerens valg og utfører nedlastingene i denne mappen. Her er hovedtrinnene:

Innlogging:

Skriptet navigerer til innloggingssiden.
Fyller ut brukernavn og passord.
Logger inn og venter på at hovedsiden skal lastes inn.
Hovedsidebehandling:

Parser hovedsiden for å finne alle tilgjengelige "merchants".
Viser en GUI for å la brukeren velge en eller flere "merchants".
Månedsvalg:

Viser en GUI for å la brukeren velge en eller flere måneder for rapporter.
Nedlastingsmappe:

Åpner en filvelger for å la brukeren velge en mappe for nedlasting.
Oppdaterer nettleserens nedlastingsinnstillinger til å bruke den valgte mappen.
Nedlasting av rapporter:

Navigerer til hver valgt "merchant".
Går til "Reports" og deretter "Detailed".
Laster ned rapporter for de valgte månedene.
Venter til nedlastingene er fullført før den går videre til neste rapport eller "merchant".
Lukking:

Skriptet lukker nettleseren etter at alle nedlastingene er fullført.
Dette skriptet kombinerer Selenium for nettleserautomatisering, BeautifulSoup for HTML-parsing, og Tkinter for GUI-interaksjon. Det er spesielt nyttig for automatisering av nedlasting av rapporter fra passordbeskyttede nettsteder.
