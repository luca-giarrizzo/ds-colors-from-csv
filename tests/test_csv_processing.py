import sys
import pytest

sys.path.append("/Users/giarrizz/Library/Application Support/Steam/steamapps/common/Substance 3D Designer 2026/Adobe Substance 3D Designer.app/Contents/Resources/python")
import sd
from palette import Palette, PaletteColor
from csv_processing import CSVColorProcessor

# ---

TEST_ASSETS_PATHS: dict[str, str] = {
    "win32": "D:\\Downloads\\testPalette.csv",
    "darwin": "/Users/giarrizz/Downloads/testPalette.csv",
    "linux": "/Users/giarrizz/Downloads/testPalette.csv"
}

TEST_RGB_VALUES: set[tuple[int, int, int]] = {
        (128, 128, 128),
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255)
    }

# ---

def test_csv_processing_save():
    testPalette = Palette("Test palette")
    csvColorProcessor = CSVColorProcessor()
    for rgbValue in TEST_RGB_VALUES:
        testPalette.add(PaletteColor(rgbValue))
    result = csvColorProcessor.savePalette(testPalette, TEST_ASSETS_PATHS[sys.platform])
    assert result


def test_csv_processing_load():
    csvColorProcessor = CSVColorProcessor()
    palette = csvColorProcessor.loadPalette(TEST_ASSETS_PATHS[sys.platform])
    assert palette.rgbValues == TEST_RGB_VALUES


def test_csv_processing_set_get_options():
    csvColorProcessor = CSVColorProcessor()
    csvColorProcessor.labelRow = 3
    assert csvColorProcessor.labelRow == 3


def test_csv_processing_set_option_type_check():
    csvColorProcessor = CSVColorProcessor()
    csvColorProcessor.labelRow = "4"
    assert csvColorProcessor.labelRow != 4


def test_csv_processing_reset_option():
    csvColorProcessor = CSVColorProcessor()
    csvColorProcessor.labelRow = 3
    csvColorProcessor.resetOption("labelRow")
    assert csvColorProcessor.labelRow == CSVColorProcessor.CSV_OPTIONS_DEFAULTS["labelRow"]


def test_csv_processing_reset_all_options():
    csvColorProcessor = CSVColorProcessor()
    csvColorProcessor.labelRow = 3
    csvColorProcessor.colorSeparator = ";"
    csvColorProcessor.resetAllOptions()
    checkOption1 = csvColorProcessor.labelRow == CSVColorProcessor.CSV_OPTIONS_DEFAULTS["labelRow"]
    checkOption2 = csvColorProcessor.colorSeparator == CSVColorProcessor.CSV_OPTIONS_DEFAULTS["colorSeparator"]
    assert checkOption1 and checkOption2

# ---

if "__main__" == __name__:
    pytest.main([__file__, "-v"])
