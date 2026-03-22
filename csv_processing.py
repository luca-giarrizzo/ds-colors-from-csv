from typing import Any
from os import path
import csv

from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QToolBar, QDialog, QVBoxLayout, QComboBox, QTextEdit, \
                              QCheckBox, QPushButton, QSpinBox, QFrame
from PySide6.QtCore import Qt, QRect, QPoint

from sd.api import SDResourceBitmap
from sd.api.sdresource import EmbedMethod
from sd.api.sdpackagemgr import SDPackageMgr

from .utilities import *
from .ui_strings import *
from .palette import Palette, PaletteColor

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

    def extractPalette(self, filepath: str) -> Palette | None:
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
            if "," in self.__options["colorRow"]:
                colorColumns = self.__options["colorRow"].split(",")
                if len(colorColumns) == 3:
                    for columnIndex in colorColumns:
                        if columnIndex.isdigit() and columnIndex < len(rowCells):
                            cellValue = rowCells[columnIndex]
                            if cellValue.isdigit():
                                colorValueList.append(int(cellValue))
                            else:
                                getLogger().error(
                                    f"Invalid color value in cell ({rowIndex}, {columnIndex}): {cellValue}")
                        else:
                            getLogger().error(f"Invalid column index: {columnIndex}")
                            return None
                else:
                    getLogger().error(f"Invalid amount of columns: {len(colorColumns)}. Specify 3 columns for RGB.")
            else:
                columnIndex = self.__options["colorRow"]
                if columnIndex.isdigit() and int(columnIndex) < len(rowCells):
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

            rgbValues: tuple[int, int, int] = tuple(*colorValueList)

            if self.__options["hasLabel"] and self.__options["labelRow"].isdigit():
                colorName = rowCells[int(self.__options["labelRow"])]
            else:
                colorName = None

            paletteColors.append(PaletteColor(rgbValues=rgbValues, name=colorName))

        return Palette(name=path.splitext(path.basename(filepath))[0], paletteColors=paletteColors)


# ---

class PresetsFromCSVToolbar(QToolBar):

    def __init__(self, parent, pkgMgr: SDPackageMgr, graph: SDSBSCompGraph):
        super().__init__(parent=parent)
        self.setObjectName("PresetsFromCSVToolbar")
        self.__pkgMgr = pkgMgr
        self.graph = graph
        self.package = self.graph.getPackage()
        self.packageDir, self.packageName = path.split(self.package.getFilePath())
        self.packageResourcesDir = path.join(self.packageDir, path.splitext(self.packageName)[0] + ".resources")

        self.csvProcessor = CSVColorProcessor()

        self.optionsDialog = CSVOptionsDialog(self.csvProcessor)
        self.presetsFromCSVDialog = PresetsFromCSVDialog()
        self.presetsFromCSVDialog.createPresetsButton.clicked.connect(self.createPresetsFromCSV)
        self.presetsFromCSVDialog.createPaletteButton.clicked.connect(self.createPaletteBitmapFromCSV)

        self.optionsAction = QtGui.QAction("Options", self)
        self.optionsAction.triggered.connect(self.displayOptions)
        self.addAction(self.optionsAction)

        self.createPresetsAction = QtGui.QAction("Create presets", self)
        self.createPresetsAction.triggered.connect(self.displayPresetsFromCSVDialog)
        self.addAction(self.createPresetsAction)

    def createPresetsFromCSV(self) -> None:

        def generatePresetsFromColors(
                graph: SDSBSCompGraph, palette: Palette | None, graphInputIdentifier: str) -> None:
            if not palette:
                getLogger().warning("No colors to generate presets from.")
                return None
            for colorName, color in palette.getColors().items():
                getLogger().info("Generating presets for color: " + colorName)
                preset = graph.newPreset(colorName)
                preset.addInput(graphInputIdentifier, color.colorToSDValueRGB())
                getLogger().info(f"Generated preset: {colorName} - {color.rgbValues}")

        # TODO Handle update of existing presets
        csvFilePath: str = self.presetsFromCSVDialog.csvResourceCombobox.currentData()
        colorInputProp: str = self.presetsFromCSVDialog.graphColorCombobox.currentText()
        palette: Palette | None = self.csvProcessor.extractPalette(csvFilePath)

        if palette:
            getLogger().info(f"Found {palette.length()} colors: " + ", ".join(palette.getNames()))
            getLogger().info("Creating presets...")
            generatePresetsFromColors(self.graph, palette, colorInputProp)
        else:
            getLogger().info("No colors found in CSV.")

    def createPaletteBitmapFromCSV(self) -> SDResourceBitmap | None:
        csvFilePath: str = self.presetsFromCSVDialog.csvResourceCombobox.currentData()
        palette: Palette | None = self.csvProcessor.extractPalette(csvFilePath)

        if palette:
            getLogger().info(f"Found {palette.length()} colors: " + ", ".join(palette.getNames()))
            getLogger().info("Creating palette bitmap...")
            paletteImage = generatePaletteImageFromColors(list(palette.getRGBValues()))
            paletteImageFilePath = path.join(
                self.packageResourcesDir, self.presetsFromCSVDialog.csvResourceCombobox.currentText() + "_palette.png")
            paletteImage.save(paletteImageFilePath)
            paletteBitmapResource = SDResourceBitmap.sNewFromFile(self.package, paletteImageFilePath, EmbedMethod.Linked)  # TODO Use 'Resources' folder instead of package root
            return paletteBitmapResource
        else:
            getLogger().info("No colors found in CSV.")
            return None

    def displayOptions(self):
        # zip() function pairs elements by position, sum() adds each pair
        # and map() applies sum() to all pairs for element-wise tuple addition.
        self.position = tuple(map(sum, zip(self.mapToGlobal(QPoint(0, 0)).toTuple(), (0, self.size().height()))))

        self.optionsDialog.setGeometry(QRect(*self.position, *self.optionsDialog.size().toTuple()))
        self.optionsDialog.show()

    def displayPresetsFromCSVDialog(self):
        # TODO Spawn dialog under toolbar action
        self.position = tuple(map(sum, zip(self.mapToGlobal(QPoint(0, 0)).toTuple(), (0, self.size().height()))))

        self.presetsFromCSVDialog.csvResourcesFilepaths = gatherCSVResourcesPathsInPackage(self.package)
        self.presetsFromCSVDialog.graphColorParameters = gatherGraphColorParameters(self.graph)
        self.presetsFromCSVDialog.refreshComboboxesLists()

        self.presetsFromCSVDialog.createPresetsButton.setEnabled(
            len(self.presetsFromCSVDialog.csvResourcesFilepaths) > 0 and len(self.presetsFromCSVDialog.graphColorParameters) > 0)

        self.presetsFromCSVDialog.setGeometry(QRect(*self.position, *self.presetsFromCSVDialog.size().toTuple()))
        self.presetsFromCSVDialog.show()


class CSVOptionsDialog(QDialog):
    def __init__(self, csvProcessor: CSVColorProcessor, parent=None):
        super().__init__(parent)

        self.csvProcessor = csvProcessor

        self.setObjectName("csv-options-dialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setFixedSize(200, 250)

        self.mainLayout = QVBoxLayout()
        self.csvDialectOption: QComboBox = self.addCSVDialectOption()
        self.hasLabelOption: QCheckBox = self.addHasLabelOption()
        self.labelRowOption: QSpinBox = self.addLabelRowOption()
        self.colorRowOption: QSpinBox = self.addColorRowOption()
        self.colorSeparatorOption: QTextEdit = self.addColorSeparatorOption()
        self.colorValueFormatOption: QComboBox = self.addColorValueFormatOption()
        self.hasAlphaOption: QCheckBox = self.addHasAlphaOption()
        self.hasHeaderOption: QCheckBox = self.addHasHeaderOption()
        self.resetButton: QPushButton = self.addResetToDefaultButton()

        self.setLayout(self.mainLayout)

    def addColorRowOption(self) -> QSpinBox:
        colorRowLayout = QtWidgets.QHBoxLayout()
        colorRowLabel = QtWidgets.QLabel(UIStr_colorRowLabel)

        colorRow = RowSpinBox(optionsDialog=self, optionIdentifier="colorRow", parent=self)

        colorRowLayout.addWidget(colorRowLabel)
        colorRowLayout.addWidget(colorRow)
        self.mainLayout.addLayout(colorRowLayout)

        return colorRow

    def addColorSeparatorOption(self) -> QTextEdit:
        colorSeparatorLayout = QtWidgets.QHBoxLayout()
        colorSeparatorLabel = QtWidgets.QLabel(UIStr_colorSeparatorLabel)

        colorSeparator = OptionTextEdit(
            optionsDialog=self, optionIdentifier="colorSeparator", parent=self)

        colorSeparatorLayout.addWidget(colorSeparatorLabel)
        colorSeparatorLayout.addWidget(colorSeparator)
        self.mainLayout.addLayout(colorSeparatorLayout)

        return colorSeparator

    def addColorValueFormatOption(self) -> QComboBox:
        colorValueFormatLayout = QtWidgets.QHBoxLayout()
        colorValueFormatLabel = QtWidgets.QLabel(UIStr_colorFormatLabel)
        colorValueFormat = QtWidgets.QComboBox()

        colorValueFormat.addItem("Float", userData=float)
        colorValueFormat.addItem("Integer", userData=int)

        colorValueFormat.currentIndexChanged.connect(
            lambda: self.csvProcessor.setOption("colorValueFormat", colorValueFormat.itemData(colorValueFormat.currentIndex())))
        colorValueFormat.setCurrentIndex(colorValueFormat.findData(self.csvProcessor.getOption("colorValueFormat")))  # Initialise default value

        colorValueFormatLayout.addWidget(colorValueFormatLabel)
        colorValueFormatLayout.addWidget(colorValueFormat)
        self.mainLayout.addLayout(colorValueFormatLayout)

        return colorValueFormat

    def addHasAlphaOption(self) -> QCheckBox:
        hasAlphaLayout = QtWidgets.QHBoxLayout()
        hasAlphaLabel = QtWidgets.QLabel(UIStr_hasAlphaLabel)

        hasAlpha = QtWidgets.QCheckBox()
        hasAlpha.toggled.connect(lambda: self.csvProcessor.setOption("hasAlpha", hasAlpha.isChecked()))
        hasAlpha.setChecked(self.csvProcessor.getOption("hasAlpha"))  # Initialise default value

        hasAlphaLayout.addWidget(hasAlphaLabel)
        hasAlphaLayout.addWidget(hasAlpha)
        self.mainLayout.addLayout(hasAlphaLayout)

        return hasAlpha

    def addHasLabelOption(self) -> QCheckBox:
        hasLabelLayout = QtWidgets.QHBoxLayout()
        hasLabelLabel = QtWidgets.QLabel(UIStr_hasLabelLabel)

        hasLabel = QtWidgets.QCheckBox()
        hasLabel.toggled.connect(lambda: self.csvProcessor.setOption("hasLabel", hasLabel.isChecked()))
        hasLabel.toggled.connect(lambda: self.labelRowOption.setEnabled(hasLabel.isChecked()))
        hasLabel.setChecked(self.csvProcessor.getOption("hasLabel"))

        hasLabelLayout.addWidget(hasLabelLabel)
        hasLabelLayout.addWidget(hasLabel)
        self.mainLayout.addLayout(hasLabelLayout)

        return hasLabel

    def addHasHeaderOption(self) -> QCheckBox:
        hasHeaderLayout = QtWidgets.QHBoxLayout()
        hasHeaderLabel = QtWidgets.QLabel(UIStr_hasHeaderLabel)

        hasHeader = QtWidgets.QCheckBox()
        hasHeader.toggled.connect(lambda: self.csvProcessor.setOption("hasHeader", hasHeader.isChecked()))
        hasHeader.setChecked(self.csvProcessor.getOption("hasHeader"))  # Initialise default value

        hasHeaderLayout.addWidget(hasHeaderLabel)
        hasHeaderLayout.addWidget(hasHeader)
        self.mainLayout.addLayout(hasHeaderLayout)

        return hasHeader

    def addLabelRowOption(self) -> QSpinBox:
        # TODO Make label row optional and generate label from color values if not provided
        labelRowLayout = QtWidgets.QHBoxLayout()
        labelRowLabel = QtWidgets.QLabel(UIStr_labelRowLabel)

        labelRow = RowSpinBox(optionsDialog=self, optionIdentifier="labelRow", parent=self)

        labelRowLayout.addWidget(labelRowLabel)
        labelRowLayout.addWidget(labelRow)
        self.mainLayout.addLayout(labelRowLayout)

        return labelRow

    def addCSVDialectOption(self) -> QComboBox:
        csvDialectLayout = QtWidgets.QHBoxLayout()
        csvDialectLabel = QtWidgets.QLabel(UIStr_csvDialectLabel)
        csvDialect = QComboBox()

        csvDialect.addItem("Excel", userData="excel")
        csvDialect.addItem("Excel Tab", userData="excel-tab")
        csvDialect.addItem("Unix", userData="unix")

        csvDialect.currentIndexChanged.connect(
            lambda: self.csvProcessor.setOption("csvDialect", csvDialect.itemData(csvDialect.currentIndex())))
        csvDialect.setCurrentIndex(csvDialect.findData(self.csvProcessor.getOption("csvDialect")))  # Initialise default value

        csvDialectLayout.addWidget(csvDialectLabel)
        csvDialectLayout.addWidget(csvDialect)
        self.mainLayout.addLayout(csvDialectLayout)

        return csvDialect

    def addResetToDefaultButton(self) -> QPushButton:
        resetToDefaultLayout = QtWidgets.QHBoxLayout()
        resetToDefaultLayout.setAlignment(Qt.AlignmentFlag.AlignRight)

        resetToDefaultButton = QtWidgets.QPushButton(UIStr_optionsResetButton)
        resetToDefaultButton.setFixedWidth(100)
        resetToDefaultButton.clicked.connect(self.resetOptions)

        resetToDefaultLayout.addStretch()
        resetToDefaultLayout.addWidget(resetToDefaultButton)
        self.mainLayout.addLayout(resetToDefaultLayout)

        return resetToDefaultButton

    def resetOptions(self) -> None:
        self.csvProcessor.resetAllOptions()

        self.csvDialectOption.setCurrentIndex(self.csvDialectOption.findData(
            self.csvProcessor.getOption("csvDialect")))
        self.hasLabelOption.setChecked(
            self.csvProcessor.getOption("hasLabel"))
        self.labelRowOption.setValue(
            self.csvProcessor.getOption("labelRow"))
        self.colorRowOption.setValue(
            self.csvProcessor.getOption("colorRow"))
        self.colorSeparatorOption.setText(
            self.csvProcessor.getOption("colorSeparator"))
        self.colorValueFormatOption.setCurrentIndex(self.colorValueFormatOption.findData(
            self.csvProcessor.getOption("colorValueFormat")))
        self.hasHeaderOption.setChecked(
            self.csvProcessor.getOption("hasHeader"))
        self.hasAlphaOption.setChecked(
            self.csvProcessor.getOption("hasAlpha"))

        getLogger().info("CSV options have been reset.")
        self.csvProcessor.logCurrentOptions()

    def updateOptions(self, key: str, value: Any) -> None:
        self.csvProcessor.setOption(key, value)
        getLogger().info(f"Updated option {key}: {value}")
        self.csvProcessor.logCurrentOptions()


class OptionTextEdit(QtWidgets.QTextEdit):
    def __init__(
            self, optionsDialog: CSVOptionsDialog, optionIdentifier: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.fontMetrics().height())  # Set height to fit a single line of text
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.optionsDialog = optionsDialog
        self.optionIdentifier = optionIdentifier

        self.setText(optionsDialog.csvProcessor.getOption(optionIdentifier))  # Initialise value

    def focusOutEvent(self, e):
        # TODO Add visual feedback for invalid input (e.g. red border) without losing focus
        plainText = self.toPlainText()
        if plainText:
            self.optionsDialog.csvProcessor.setOption(self.optionIdentifier, plainText)
        else:  # Set option value to default if text is empty
            self.optionsDialog.csvProcessor.resetOption(self.optionIdentifier)
        super().focusOutEvent(e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter:
            self.clearFocus()  # Trigger focusOutEvent to save the option value
        elif e.key() == Qt.Key.Key_Backspace:
            self.clear()
        super().keyPressEvent(e)


class RowSpinBox(QtWidgets.QSpinBox):
    def __init__(self, optionsDialog: CSVOptionsDialog, optionIdentifier: str, parent=None):
        super().__init__(parent)
        self.setSingleStep(1)
        self.setMinimum(0)

        self.presetDialog = optionsDialog
        self.optionIdentifier = optionIdentifier

        self.setValue(optionsDialog.csvProcessor.getOption(optionIdentifier))  # Initialise default value

    def focusOutEvent(self, e):
        self.presetDialog.csvProcessor.setOption(self.optionIdentifier, self.value())
        super().focusOutEvent(e)


class PresetsFromCSVDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("presets-from-csv-dialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setFixedSize(200, 200)

        self.csvResourcesFilepaths: dict[str, str] = {}
        self.graphColorParameters: dict[str, SDProperty] = {}

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.csvResourceCombobox: QComboBox = QtWidgets.QComboBox()
        self.addCSVResourceSection()

        self.graphColorCombobox: QComboBox = QtWidgets.QComboBox()
        self.createPresetsButton: QPushButton = QtWidgets.QPushButton(UIStr_createPresetsButton)
        self.addCreatePresetsSection()

        self.createPaletteButton: QPushButton = QtWidgets.QPushButton(UIStr_createPaletteButton)
        self.addCreatePaletteSection()

        self.csvResourceCombobox.currentTextChanged.connect(self.refreshButtonStates)
        self.graphColorCombobox.currentTextChanged.connect(self.refreshButtonStates)

        self.refreshComboboxesLists()
        self.refreshButtonStates()

    def addCSVResourceSection(self) -> None:
        csvResourceLayout = QtWidgets.QHBoxLayout()

        # CSV resource combobox
        csvResourceLabel = QtWidgets.QLabel(UIStr_csvResourceLabel)
        csvResourceLayout.addWidget(csvResourceLabel)
        csvResourceLayout.addWidget(self.csvResourceCombobox)

        self.mainLayout.addLayout(csvResourceLayout)

    def refreshComboboxesLists(self):
        self.graphColorCombobox.clear()
        self.csvResourceCombobox.clear()

        for graphColorParameter in self.graphColorParameters:
            parameterLabel = self.graphColorParameters[graphColorParameter].getLabel()
            if parameterLabel:
                self.graphColorCombobox.addItem(parameterLabel, userData=self.graphColorParameters[graphColorParameter])
            else:
                self.graphColorCombobox.addItem(graphColorParameter, userData=self.graphColorParameters[graphColorParameter])
        self.graphColorCombobox.setCurrentIndex(0)

        for resourceId, resource in self.csvResourcesFilepaths.items():
            self.csvResourceCombobox.addItem(resourceId, userData=resource)
        self.csvResourceCombobox.setCurrentIndex(0)

    def refreshButtonStates(self) -> None:
        if not self.csvResourceCombobox.currentText():
            self.createPresetsButton.setEnabled(False)
            self.createPaletteButton.setEnabled(False)
        else:
            self.createPaletteButton.setEnabled(True)
            if not self.graphColorCombobox.currentText():
                self.createPresetsButton.setEnabled(False)
            else:
                self.createPresetsButton.setEnabled(True)

    def addCreatePresetsSection(self) -> None:
        separator = layoutSeparator()
        self.mainLayout.addWidget(separator)
        createPresetsLayout = QtWidgets.QVBoxLayout()

        # Title
        createPresetsLabel = QtWidgets.QLabel("<b>" + UIStr_createPresetsSection + "</b>")
        createPresetsLayout.addWidget(createPresetsLabel)

        # Graph input combobox
        graphColorLayout = QtWidgets.QHBoxLayout()
        graphColorLabel = QtWidgets.QLabel(UIStr_colorParameterLabel)
        graphColorLayout.addWidget(graphColorLabel)
        graphColorLayout.addWidget(self.graphColorCombobox)
        createPresetsLayout.addLayout(graphColorLayout)

        # Create presets button
        createPresetsLayout.addWidget(self.createPresetsButton)

        self.mainLayout.addLayout(createPresetsLayout)

    def addCreatePaletteSection(self) -> None:
        separator = layoutSeparator()
        self.mainLayout.addWidget(separator)
        createPaletteLayout = QtWidgets.QVBoxLayout()

        # Title
        createPaletteLabel = QtWidgets.QLabel("<b>" + UIStr_createPaletteSection + "</b>")
        createPaletteLayout.addWidget(createPaletteLabel)

        # Create palette button
        createPaletteButton = self.createPaletteButton
        createPaletteLayout.addWidget(createPaletteButton)

        self.mainLayout.addLayout(createPaletteLayout)


def layoutSeparator(lineWidth: int = 5) -> QFrame:
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    separator.setLineWidth(lineWidth)
    return separator
