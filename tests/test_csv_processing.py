from palette import Palette, PaletteColor
from csv_processing import CSVColorProcessor

def test_csv_processing_save():
    rgbValues = [
        (128, 128, 128),
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255)
    ]

    testPalette = Palette("Test palette")
    csvColorProcessor = CSVColorProcessor()

    for rgbValue in rgbValues:
        testPalette.add(PaletteColor(rgbValue))

    result = csvColorProcessor.savePalette(testPalette, "D:\\Downloads\\testPalette.csv")

    if result:
        print("PASS")
    else:
        print("FAIL")

if "__main__" == __name__:
    test_csv_processing_save()
