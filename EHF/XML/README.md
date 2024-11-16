
Dette Python-programmet parser XML-filer for å ekstrahere og analysere spesifikke datafelt. Programmet bruker tkinter-biblioteket for å gi et grafisk brukergrensesnitt (GUI) hvor brukeren kan velge en eller flere XML-filer. Dataene blir deretter behandlet og en rapport vises i et popup-vindu.

Funksjoner
XML-parsing: Programmet leser og analyserer XML-strukturen for å finne bestemte tagger og deres tilhørende verdier.
Dataekstraksjon: Følgende datafelt hentes ut og analyseres:
CompanyID: Kontrollerer at lengden er nøyaktig 9 tegn.
TaxAmount: Lagrer de tre første funne TaxAmount-verdiene.
TaxInclusiveAmount: Finner den første forekomsten av denne taggen.
Rapportgenerering: Basert på de funne dataene, genereres en rapport som inkluderer summer og statusmeldinger.
Bruk
Installere avhengigheter: Sørg for at du har følgende Python-pakker installert:

xml.etree.ElementTree
pandas
tkinter
Kjøring av programmet:

Start programmet ved å kjøre Python-filen.
Et filvalgsvindu vil dukke opp, hvor du kan velge en eller flere XML-filer.
Etter filvalg, vil programmet behandle filene og vise en rapport i popup-vinduer for hver fil.
Avslutning:

Programmet avsluttes automatisk etter at alle valgte filer er behandlet og rapportene er vist.
Eksempler
Når du velger en XML-fil, vil programmet vise en rapport med oppsummering av data som TaxExclusiveAmount, LineExtensionAmount, og TaxInclusiveAmount. Dette hjelper med raskt å validere innholdet i XML-filene.

Forutsetninger
Programmet forutsetter at XML-filene har en veldefinert struktur med de nødvendige taggene (CompanyID, TaxAmount, TaxInclusiveAmount, etc.).
Brukeren må ha Python installert på systemet sitt.
Feilsøking
Hvis du får en feilmelding angående manglende pakker, installér dem ved hjelp av pip install pandas tkinter.
Hvis XML-filene ikke inneholder de forventede taggene, kan rapportene inneholde feilmeldinger eller tomme felt.
Dette programmet er ideelt for brukere som trenger en rask måte å analysere og validere spesifikke data fra XML-filer.
