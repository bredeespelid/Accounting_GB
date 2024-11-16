
function main(workbook: ExcelScript.Workbook) {
	let one = workbook.getWorksheets()[0];

	one.setName("Input");

	let newTable = workbook.addTable(one.getUsedRange(), true);

	newTable.setName("avstemming");
	
	let posenummer = newTable.addColumn(-1, null, "Posenummer");


	posenummer.getRangeBetweenHeaderAndTotal().setFormula("=INDEX(MID([@Fritekst],ROW(INDIRECT(\"1:\"&LEN([@Fritekst]))),12),MATCH(TRUE,ISNUMBER(--MID([@Fritekst],ROW(INDIRECT(\"1:\"&LEN([@Fritekst]))),12)),0))");

		one.getRange("D:E").setNumberFormat("d/m/yy");

	let oversikt = workbook.addWorksheet("Oversikt")

	let pt = oversikt.addPivotTable("PIVOT", newTable, oversikt.getRange("A1"));

	/* Add "Product line" as a row hierarchy in the pivot table */

	pt.addRowHierarchy(pt.getHierarchy("Posenummer"));

	pt.addDataHierarchy(pt.getHierarchy("Posenummer"))

	pt.addColumnHierarchy(pt.getHierarchy("Posenummer"));


	let sok = workbook.addWorksheet("Søk")


	sok.getRange("A1").setFormulaLocal("=UNIQUE(avstemming[])");

	sok.getRange("A:A").setColumnHidden(true);

	let dataValidation: ExcelScript.DataValidation;
	// Data validation changed on range C3 on selectedSheet
	dataValidation = sok.getRange("C3").getDataValidation();
	dataValidation.clear();
	dataValidation.setIgnoreBlanks(true);
	dataValidation.setPrompt({ showPrompt: true, title: "", message: "" });
	dataValidation.setErrorAlert({ showAlert: true, title: "", message: "", style: ExcelScript.DataValidationAlertStyle.stop });
	dataValidation.setRule({ list: { inCellDropDown: true, source: "=$A:$A" } });
	// Set range C2 on selectedSheet
	sok.getRange("C2").setValue("Velg posenr");
	// Set range C4 on selectedSheet
	sok.getRange("C4").setFormula("=VSTACK(avstemming[#Headers],FILTER(avstemming,avstemming[Posenummer]=C3))");
	sok.getCell(2, 2).setValue("Trykk her!")

	sok.getRange("F:G").setNumberFormat("d/m/yy");
}
