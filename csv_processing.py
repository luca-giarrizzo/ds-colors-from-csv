import csv
from os import path
from typing import Any

from palette import Palette, PaletteColor
from utilities import getLogger

# ---

class CSVColorProcessor:

    CSV_OPTIONS_DEFAULTS: dict[str, Any] = {
        "csvDialect": "excel",
        "hasLabel": True,
        "labelRow": 0,
        "colorRow": 1,
        "colorSeparator": "-",
        "colorValueFormat": int,
        "hasAlpha": False,
        "hasHeader": True
    }

    def __init__(self):
        self.__options: dict[str, Any] = CSVColorProcessor.CSV_OPTIONS_DEFAULTS

    def getOption(self, identifier: str) -> Any | None:
        if identifier in CSVColorProcessor.CSV_OPTIONS_DEFAULTS:
            return self.__options[identifier]
        else:
            getLogger().error(f"Option not found: {identifier}")
            return None

    def getAllOptions(self) -> dict[str, Any]:
        return self.__options

    def setOption(self, identifier: str, value: Any) -> bool:
        if identifier in CSVColorProcessor.CSV_OPTIONS_DEFAULTS:
            if isinstance(value, CSVColorProcessor.CSV_OPTIONS_DEFAULTS[identifier].__class__):
                self.__options[identifier] = value
                return True
            else:
                getLogger().error(
                    f"Value is of wrong type: {value.__class__} \
                    (Expected: {CSVColorProcessor.CSV_OPTIONS_DEFAULTS[identifier].__class__})")
                return False
        else:
            getLogger().error(f"Option not found: {identifier}")
            return False

    def resetOption(self, identifier: str) -> bool:
        if identifier in CSVColorProcessor.CSV_OPTIONS_DEFAULTS:
            self.__options[identifier] = CSVColorProcessor.CSV_OPTIONS_DEFAULTS[identifier]
            return True
        else:
            getLogger().error(f"Option not found: {identifier}")
            return False

    def resetAllOptions(self) -> None:
        self.__options = {key: value for key, value in CSVColorProcessor.CSV_OPTIONS_DEFAULTS.items()}

    def logCurrentOptions(self):
        optionsPrettyPrint = "\n".join(
            [f"  - {key}: {value}" for key, value in self.__options.items()])
        getLogger().info(f"Current options:\n{optionsPrettyPrint}")

    def loadPalette(self, filepath: str) -> Palette | None:
        try:
            with open(filepath, "r", encoding="utf-8", newline="") as csvFile:
                csvReader = csv.reader(csvFile, delimiter=",", dialect=self.__options["csvDialect"])
                csvValues = [row for row in csvReader]
        except Exception as e:
            getLogger().error("ERROR:" + str(e))
            return None

        paletteColors: list[PaletteColor] = []

        if self.__options["hasHeader"]:
            csvValues = csvValues[1:]  # Skip header row

        for rowIndex, rowCells in enumerate(csvValues):
            colorValueList: list[int] = []
            columnIndex = self.__options["colorRow"]
            if isinstance(columnIndex, str) and "," in columnIndex:
                colorColumns = columnIndex.split(",")
                if len(colorColumns) == 3:
                    for column in colorColumns:
                        if column.isdigit() and column < len(rowCells):
                            cellValue = rowCells[column]
                            if cellValue.isdigit():
                                colorValueList.append(int(cellValue))
                            else:
                                getLogger().error(
                                    f"Invalid color value in cell ({rowIndex}, {column}): {cellValue}")
                        else:
                            getLogger().error(f"Invalid column index: {column}")
                            return None
                else:
                    getLogger().error(f"Invalid amount of columns: {len(colorColumns)}. Specify 3 columns for RGB.")
            elif isinstance(columnIndex, int) and columnIndex < len(rowCells):
                cellValues: list[str] = rowCells[int(self.__options["colorRow"])].split(self.__options["colorSeparator"])
                if len(cellValues) == 3:
                    for cellValue in cellValues:
                        if cellValue.isdigit():
                            colorValueList.append(int(cellValue))
                        else:
                            getLogger().error(
                                f"Invalid color value in cell ({rowIndex}, {columnIndex}): {cellValue}")
                            return None
                else:
                    getLogger().error(f"Invalid amount of values: {len(cellValues)}. Specify 3 values for RGB.")
                    return None
            else:
                getLogger().error(f"Invalid column index: {columnIndex}")
                return None

            rgbValues: tuple[int, int, int] = tuple(colorValueList)

            colorName = None
            if self.__options["hasLabel"]:
                if isinstance(self.__options["labelRow"], int):
                    if self.__options["labelRow"] > len(rowCells):
                        colorName = rowCells[int(self.__options["labelRow"])]
                    else:
                        getLogger().error(f"Label row is out of range: {self.__options["labelRow"]}")
                else:
                    getLogger().error(f"Invalid label row type: {self.__options["labelRow"].__class__}")

            paletteColors.append(PaletteColor(rgbValues=rgbValues, name=colorName))

        return Palette(name=path.splitext(path.basename(filepath))[0], paletteColors=paletteColors)

    def savePalette(self, palette: Palette, filepath: str) -> bool:
        if not path.isdir(path.split(filepath)[0]) and path.splitext(filepath)[1] == ".csv":
            getLogger().error(f"Invalid target filepath: {filepath}")
            return False

        try:
            getLogger().info(f"Writing file at: {filepath}")
            with open(filepath, "w+", encoding="utf-8", newline="") as csvFile:
                csvWriter = csv.writer(csvFile, delimiter=",", dialect=self.__options["csvDialect"])
                if self.__options["hasHeader"]:
                    csvWriter.writerow(["NAME", "RGB", "HEX"])
                    getLogger().info("Header written.")
                for colorName, color in palette.getColors().items():
                    csvWriter.writerow([colorName, self.__options["colorSeparator"].join([str(v) for v in color.rgbValues]), color.hex])
                    getLogger().info(f"Color written: {colorName}")
                getLogger().info("Done.")
            return True
        except Exception as e:
            getLogger().error(f"Could not create CSV file and start CSV writer: {e}")
            return False
