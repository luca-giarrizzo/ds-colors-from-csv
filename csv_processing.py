from typing import Any

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
