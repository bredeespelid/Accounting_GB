Sub ImportFilesToWorksheets()
    Dim FolderPathCSV As String
    Dim FolderPathExcel As String
    Dim CSVFileName As String
    Dim ExcelFileName As String
    Dim wsCSV As Worksheet
    Dim wsExcel As Worksheet
    Dim DataRange As Range
    Dim FileCounter As Integer
    Dim SourceWb As Workbook
    Dim ColumnOffset As Integer
    
    ' Define the folder paths
    FolderPathCSV = ""
    FolderPathExcel = ""
    
    ' Add a new worksheet named "" or use an existing one for CSV
    On Error Resume Next
    Set wsCSV = ThisWorkbook.Sheets("")
    On Error GoTo 0
    
    If wsCSV Is Nothing Then
        Set wsCSV = ThisWorkbook.Sheets.Add
        wsCSV.Name = ""
    End If
    
    ' Clear existing data in the "Input Firmakunder" worksheet
    wsCSV.Cells.Clear
    
    ' Add a new worksheet named "t" or use an existing one for Excel
    On Error Resume Next
    Set wsExcel = ThisWorkbook.Sheets("")
    On Error GoTo 0
    
    If wsExcel Is Nothing Then
        Set wsExcel = ThisWorkbook.Sheets.Add
        wsExcel.Name = ""
    End If
    
    ' Clear existing data in the "Input Visma Fakturaoversikt" worksheet
    wsExcel.Cells.Clear
    
    ' Initialize column offset and file counter for CSV files
    ColumnOffset = 0
    FileCounter = 0
    
    ' Loop through CSV files in the folder
    CSVFileName = Dir(FolderPathCSV & "*.csv")
    
    Do While CSVFileName <> ""
        FileCounter = FileCounter + 1
        
        ' Import the CSV data into the "Input Firmakunder" worksheet
        With wsCSV.QueryTables.Add(Connection:="TEXT;" & FolderPathCSV & CSVFileName, Destination:=wsCSV.Cells(1, 1))
            .TextFileParseType = xlDelimited
            .TextFileConsecutiveDelimiter = False
            .TextFileTabDelimiter = True ' Assumes CSV file uses tabs as delimiter
            .TextFileSemicolonDelimiter = False
            .TextFileCommaDelimiter = False
            .TextFileSpaceDelimiter = False
            .TextFileOtherDelimiter = vbTab ' Change this delimiter if needed
            .TextFileColumnDataTypes = Array(1) ' Data type for all columns (1=xlGeneralFormat)
            .Refresh BackgroundQuery:=False
        End With
        
        ' Determine the data range for the imported CSV data
        If wsCSV.Cells(1, 1).Value <> "" Then
            If DataRange Is Nothing Then
                Set DataRange = wsCSV.Cells(1, 1).CurrentRegion
            Else
                Set DataRange = Union(DataRange, wsCSV.Cells(1, 1).CurrentRegion)
            End If
        End If
        
        ' Move to the next column for the next CSV file's data
        ColumnOffset = ColumnOffset + DataRange.Columns.Count + 1
        
        ' Clear the query table to avoid any conflicts with subsequent imports
        wsCSV.QueryTables(1).Delete
        Set DataRange = Nothing
        
        ' Delete the CSV file
        Kill FolderPathCSV & CSVFileName
        
        ' Move to the next CSV file
        CSVFileName = Dir
    Loop
    
    ' Loop through Excel files in the folder
    ExcelFileName = Dir(FolderPathExcel & "*.xlsx") ' Change to ".xls" for older Excel formats
    
    Do While ExcelFileName <> ""
        ' Open the Excel file for data import
        On Error Resume Next
        Set SourceWb = Workbooks.Open(FolderPathExcel & ExcelFileName)
        On Error GoTo 0
        
        If Not SourceWb Is Nothing Then
            ' Copy data from the source workbook to the target worksheet
            SourceWb.Sheets(1).UsedRange.Copy wsExcel.Cells(1, 1)
            
            ' Close the source workbook without saving changes
            SourceWb.Close SaveChanges:=False
            
            ' Clean up
            Set SourceWb = Nothing
        Else
            MsgBox "Failed to open the Excel file for data import.", vbExclamation
        End If
        
        ' Delete the Excel file
        Kill FolderPathExcel & ExcelFileName
        
        ' Move to the next Excel file
        ExcelFileName = Dir
    Loop
    
    ' Display a message with the results
    Dim Msg As String
    If FileCounter > 0 Then
        Msg = FileCounter & " CSV files have been imported into the '' worksheet in separate columns." & vbCrLf
    Else
        Msg = "No CSV files found in the specified folder." & vbCrLf
    End If
    
    ' Check if Excel file was imported
    If Not wsExcel.Cells(1, 1).Value = "" Then
        Msg = Msg & "The Excel file has been imported into the '' worksheet and deleted from the folder."
    Else
        Msg = Msg & "The Excel file could not be imported."
    End If
    
    MsgBox Msg, vbInformation
    
    ' Clean up
    Set wsCSV = Nothing
    Set wsExcel = Nothing
End Sub