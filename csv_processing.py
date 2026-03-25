import csv
from os import path
from typing import Any

from palette import Palette, PaletteColor
from utilities import getLogger

# ---

class CSVColorProcessor:

    CSV_DIALECTS: set[str] = {"excel", "excel-tab", "unix"}
    COLOR_VALUE_FORMATS: set = {int, float}
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
        self.__options: dict[str, Any] = self.CSV_OPTIONS_DEFAULTS

    @property
    def csvDialect(self) -> str:
        return self.__options["csvDialect"]

    @property
    def hasLabel(self) -> bool:
        return self.__options["hasLabel"]

    @property
    def labelRow(self) -> int:
        return self.__options["labelRow"]

    @property
    def colorRow(self) -> int:
        return self.__options["colorRow"]

    @property
    def colorSeparator(self) -> str:
        return self.__options["colorSeparator"]

    @property
    def colorValueFormat(self) -> type:
        return self.__options["colorValueFormat"]

    @property
    def hasAlpha(self) -> bool:
        return self.__options["hasAlpha"]

    @property
    def hasHeader(self) -> bool:
        return self.__options["hasHeader"]

    @property
    def options(self) -> dict[str, Any]:
        return self.__options

    # ---

    @csvDialect.setter
    def csvDialect(self, csvDialect: str):
        if not isinstance(csvDialect, str):
            getLogger().error(f"Dialect should be a string.")
            return
        if csvDialect in CSVColorProcessor.CSV_DIALECTS:
            self.__options["csvDialect"] = csvDialect
        else:
            getLogger().error(f"Dialect is invalid or unsupported: {csvDialect}")

    @hasLabel.setter
    def hasLabel(self, hasLabel: bool):
        self.__options["hasLabel"] = bool(hasLabel)

    @labelRow.setter
    def labelRow(self, labelRow: int):
        if not isinstance(labelRow, int):
            getLogger().error(f"Label row should be an integer.")
            return
        if labelRow > 0:
            self.__options["labelRow"] = labelRow
        else:
            getLogger().error(f"Label row cannot be negative.")

    @colorRow.setter
    def colorRow(self, colorRow: int):
        if not isinstance(colorRow, int):
            getLogger().error(f"Color row should be an integer.")
            return
        if colorRow > 0:
            self.__options["colorRow"] = colorRow
        else:
            getLogger().error(f"Color row cannot be negative.")

    @colorSeparator.setter
    def colorSeparator(self, colorSeparator: str):
        if not isinstance(colorSeparator, str):
            getLogger().error(f"Color separator should be a string.")
        if colorSeparator.isalnum():
            getLogger().error(f"Color separator cannot be alphanumeric.")
        elif len(colorSeparator) != 1:
            getLogger().error(f"Color separator must be a single character.")
        else:
            self.__options["colorSeparator"] = colorSeparator

    @colorValueFormat.setter
    def colorValueFormat(self, colorValueFormat: type):
        if not isinstance(colorValueFormat, type):
            getLogger().error(f"Color value format should be a type.")
            return
        if colorValueFormat.__class__ in self.COLOR_VALUE_FORMATS:
            self.__options["colorValueFormat"] = colorValueFormat
        else:
            typesList : list[str] = [t.__name__ for t in self.COLOR_VALUE_FORMATS]
            getLogger().error(f"Color value format must be any type of: {', '.join(typesList)}")

    @hasAlpha.setter
    def hasAlpha(self, hasAlpha: bool):
        self.__options["hasAlpha"] = bool(hasAlpha)

    @hasLabel.setter
    def hasLabel(self, hasLabel: bool):
        self.__options["hasLabel"] = bool(hasLabel)

    # ---

    def getOptionValueFromName(self, identifier: str) -> Any | None:
        if identifier in self.CSV_OPTIONS_DEFAULTS:
            return self.__options[identifier]
        else:
            getLogger().error(f"Option not found: {identifier}")
            return None

    def setOptionValueFromName(self, identifier: str, value: Any) -> bool:
        if identifier in CSVColorProcessor.CSV_OPTIONS_DEFAULTS:
            if isinstance(value, self.CSV_OPTIONS_DEFAULTS[identifier].__class__):
                self.__options[identifier] = value
                return True
            else:
                getLogger().error(
                    f"Value is of wrong type: {value.__class__} \
                    (Expected: {self.CSV_OPTIONS_DEFAULTS[identifier].__class__})")
                return False
        else:
            getLogger().error(f"Option not found: {identifier}")
            return False

    def resetOption(self, identifier: str) -> bool:
        if identifier in self.CSV_OPTIONS_DEFAULTS:
            self.__options[identifier] = self.CSV_OPTIONS_DEFAULTS[identifier]
            return True
        else:
            getLogger().error(f"Option not found: {identifier}")
            return False

    def resetAllOptions(self) -> None:
        self.__options = {key: value for key, value in self.CSV_OPTIONS_DEFAULTS.items()}

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
                        if column.isdigit():
                            column = int(column)
                            if column < len(rowCells):
                                cellValue = rowCells[int(column)]
                                if cellValue.isdigit():
                                    colorValueList.append(int(cellValue))
                                else:
                                    getLogger().error(
                                        f"Invalid color value in cell ({rowIndex}, {column}): {cellValue}")
                            else:
                                getLogger().error(f"Color index out of range: {column} in {colorColumns}")
                        else:
                            getLogger().error(f"Column index should be a digit: {column} in {colorColumns}")
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
                for colorName, color in palette.colors.items():
                    csvWriter.writerow([colorName, self.__options["colorSeparator"].join([str(v) for v in color.rgbValues]), color.hex])
                    getLogger().info(f"Color written: {colorName}")
                getLogger().info("Done.")
            return True
        except Exception as e:
            getLogger().error(f"Could not create CSV file and start CSV writer: {e}")
            return False
