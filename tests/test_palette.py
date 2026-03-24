import sys
import pytest

sys.path.append("/Users/giarrizz/Library/Application Support/Steam/steamapps/common/Substance 3D Designer 2026/Adobe Substance 3D Designer.app/Contents/Resources/python")
import sd
from palette import Palette, PaletteColor

# ---

class TestPaletteColor:

    TEST_RGB_VALUE: tuple[int, int, int] = (37, 168, 202)
    TEST_HEX: str = "#7ca38f"

    def test_palette_color_from_rgb(self):
        color = PaletteColor(rgbValues=TestPaletteColor.TEST_RGB_VALUE)
        assert color.rgbValues == TestPaletteColor.TEST_RGB_VALUE


    def test_palette_color_from_hex(self):
        color = PaletteColor(hexCode=TestPaletteColor.TEST_HEX)
        assert color.hex == TestPaletteColor.TEST_HEX.upper()


    def test_palette_color_name_from_user(self):
        colorName = "My test color"
        color = PaletteColor(name=colorName)
        assert color.name == colorName


    def test_palette_color_name_from_hex(self):
        color = PaletteColor(hexCode=TestPaletteColor.TEST_HEX)
        assert color.name == TestPaletteColor.TEST_HEX.upper()


    def test_palette_color_channels_from_rgb(self):
        color = PaletteColor(rgbValues=TestPaletteColor.TEST_RGB_VALUE)
        assert (color.r, color.g, color.b) == TestPaletteColor.TEST_RGB_VALUE


    def test_palette_color_to_float(self):
        color = PaletteColor(rgbValues=TestPaletteColor.TEST_RGB_VALUE)
        assert color.toFloat() == (color.r / 255, color.g / 255, color.b / 255)


class TestPalette:

    TEST_PALETTE_COLOR = PaletteColor(rgbValues=(64, 17, 180), name="My test color")
    TEST_PALETTE_COLORS = [
        PaletteColor(rgbValues=(255, 128, 0), name="Orange"),
        PaletteColor(hexCode="#FFFF00", name="Yellow"),
        PaletteColor(hexCode="#FF00FF", name="Magenta"),
        PaletteColor(rgbValues=(128, 0, 255), name="Purple"),
        PaletteColor(rgbValues=(128, 255, 0), name="Green")
    ]

    def test_palette_get_colors(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        assert palette.getColors() == {color.name: color for color in TestPalette.TEST_PALETTE_COLORS}

    def test_palette_add_color(self):
        palette = Palette("My test palette")
        palette.add(TestPalette.TEST_PALETTE_COLOR)
        assert palette.getColors() == {TestPalette.TEST_PALETTE_COLOR.name: TestPalette.TEST_PALETTE_COLOR}

    def test_palette_get_color(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        assert palette.getColor("Orange").rgbValues == (255, 128, 0)

    def test_palette_get_names(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        assert palette.getNames() == set([color.name for color in TestPalette.TEST_PALETTE_COLORS])

    def test_palette_get_rgb_values(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        assert palette.getRGBValues() == set([color.rgbValues for color in TestPalette.TEST_PALETTE_COLORS])

    def test_palette_get_hexcodes(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        assert palette.getHexCodes() == set([color.hex for color in TestPalette.TEST_PALETTE_COLORS])

    def test_palette_find_color_from_rgb(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        assert palette.findColorFromRGB((128, 0, 255)).name == "Purple"

    def test_palette_find_color_from_hex(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        assert palette.findColorFromHexCode("#ff00ff").name == "Magenta"

    def test_palette_length(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        assert palette.length() == len(TestPalette.TEST_PALETTE_COLORS)

    def test_palette_clear(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        palette.clear()
        assert palette.length() == 0

    def test_palette_delete_color(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        palette.delete("Magenta")
        assert not palette.getColor("Magenta") and palette.length() == len(TestPalette.TEST_PALETTE_COLORS) - 1

    def test_palette_rename(self):
        newName = "Renamed"
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        palette.rename(newName)
        assert palette.name == newName

    def test_palette_update(self):
        palette = Palette("My test palette", TestPalette.TEST_PALETTE_COLORS)
        palette.update("Magenta", TestPalette.TEST_PALETTE_COLOR)
        assert palette.getColor("Magenta").rgbValues == TestPalette.TEST_PALETTE_COLOR.rgbValues

# ---

if "__main__" == __name__:
    pytest.main([__file__, "-v"])
