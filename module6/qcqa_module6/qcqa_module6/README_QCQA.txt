QC/QA Module 6 Dataset (Power BI)
----------------------------------
Files:
- DimDate.csv (2024 calendar; DateKey YYYYMMDD; MonthKey YYYYMM)
- DimProject.csv (4 projects with client/category/PM)
- DimLine.csv (4 production lines, 4 plants)
- DimInspector.csv (6 inspectors; Seniority levels)
- DimDefectType.csv (8 defect types; Severity)
- DimShift.csv (A/B/C shifts with hours)
- FactInspection.csv (InspectionDateKey, Project/Line/Inspector/Shift/DefectType, InspectedQty, DefectQty)
- FactRework.csv (ReworkDateKey, Project/Line/DefectType, ReworkQty, ReworkOKQty)
- Targets.csv (DefectRateTarget by ProjectID x MonthKey)

Suggested relationships:
- DimDate[DateKey] -> FactInspection[InspectionDateKey] (active)
- DimDate[DateKey] -> FactRework[ReworkDateKey] (inactive)
- DimProject[ProjectID] -> FactInspection/FactRework (1:*)
- DimLine[LineID] -> FactInspection/FactRework (1:*)
- DimInspector[InspectorID] -> FactInspection (1:*)
- DimDefectType[DefectTypeID] -> FactInspection/FactRework (1:*)
- DimShift[ShiftID] -> FactInspection (1:*)
- DimDate[MonthKey] -> Targets[MonthKey] (1:*)
- DimProject[ProjectID] -> Targets[ProjectID] (1:*)

Mark DimDate as Date table using column [Date].
