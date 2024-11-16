Sub ExportToFolders()
    Dim mainFolderPath As String
    Dim headerCell As Range
    Dim DataRange As Range
    Dim headerText As String
    Dim cell As Range
    Dim subFolderPath As String
    Dim filePath As String
    Dim columnData As String
    
    ' Angi hovedmappen der csv-filene vil bli lagret.
    mainFolderPath = ""
    
    'Sett området for dataen som starter fra kolonne B (juster området i henhold til dine faktiske data).
    Set DataRange = Range("B1").CurrentRegion
    
    ' Løkke gjennom hver celle i den første raden (overskriftene).
    For Each headerCell In Range("B1").Resize(1, DataRange.Columns.Count)
        headerText = headerCell.Value
        
        'Sjekk om overskriften ikke er tom.
        If headerText <> "" Then
            ' Tøm tidligere data i kolonnen.
            columnData = ""
            
            ' Løkke gjennom hver celle i det tilsvarende datarområdet, med unntak av overskriftsraden.
            For Each cell In Intersect(DataRange.Offset(1), DataRange.Columns(headerCell.Column - DataRange.Column + 1))
                'Legg til celleverdien i kolonnedataene.
                columnData = columnData & cell.Value & vbCrLf
            Next cell
            
            ' Opprett undermappen basert på overskriftens navn.
            subFolderPath = mainFolderPath & headerText & "\"
            
            ' Opprett undermappen hvis den ikke allerede eksisterer.
            If Dir(subFolderPath, vbDirectory) = "" Then
                MkDir subFolderPath
            End If
            
            'Opprett et unikt filnavn basert på overskriften.
            filePath = subFolderPath & "" & headerText & ".csv"
            
            ' Lagre kolonnedataene i notatfilen.
            SaveToNotepad filePath, columnData
        End If
    Next headerCell
    
    MsgBox "(er)-overført!"
End Sub

Sub SaveToNotepad(ByVal filePath As String, ByVal text As String)
    Dim fileNumber As Integer
    fileNumber = FreeFile
    
    ' Åpne filen i utdatamodus og skriv teksten.
    Open filePath For Output As fileNumber
    Print #fileNumber, text
    Close fileNumber
End Sub