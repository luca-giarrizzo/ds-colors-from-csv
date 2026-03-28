import sys
import pytest
from os import path
from palette import Palette, PaletteColor
from csv_processing import CSVColorProcessor

# ---

TEST_RESOURCES_DIR = path.join(path.dirname(__file__), "test_resources")

# ---

class TestPaletteColor:

    TEST_RGB_VALUE: tuple[int, int, int] = (37, 168, 202)
    TEST_HEX: str = "#7ca38f"

    def test_palette_to_string(self):
        palette = PaletteColor(rgbValues=self.TEST_RGB_VALUE)
        palette.name = "My test color"
        assert str(palette) == "Color 'My test color'- (37, 168, 202) - #25A8CA"

    def test_palette_color_from_rgb(self):
        color = PaletteColor(rgbValues=self.TEST_RGB_VALUE)
        assert color.rgbValues == self.TEST_RGB_VALUE

    def test_palette_color_from_hex(self):
        color = PaletteColor(hexCode=self.TEST_HEX)
        assert color.hex == self.TEST_HEX.upper()

    def test_palette_color_name_from_user(self):
        colorName = "My test color"
        color = PaletteColor(name=colorName)
        assert color.name == colorName

    def test_palette_color_name_from_hex(self):
        color = PaletteColor(hexCode=self.TEST_HEX)
        assert color.name == self.TEST_HEX.upper()

    def test_palette_color_channels_from_rgb(self):
        color = PaletteColor(rgbValues=self.TEST_RGB_VALUE)
        assert (color.r, color.g, color.b) == self.TEST_RGB_VALUE

    def test_palette_color_to_float(self):
        color = PaletteColor(rgbValues=self.TEST_RGB_VALUE)
        assert color.toFloat() == (color.r / 255, color.g / 255, color.b / 255)

    def test_palette_color_from_luminance(self):
        color = PaletteColor.sNewFromLuminance(38)
        assert color.rgbValues == (38, 38, 38) and color.hex == "#262626" and color.name == "#262626"

    def test_palette_color_from_rgba(self):
        color = PaletteColor.sNewFromRGBA((87, 231, 12, 90))
        assert color.rgbValues == (87, 231, 12) and color.hex == "#57E70C" and color.name == "#57E70C"

# ---

class TestPalette:

    TEST_PALETTE_COLOR = PaletteColor(rgbValues=(64, 17, 180), name="My test color")
    TEST_PALETTE_COLORS = [
        PaletteColor(rgbValues=(255, 128, 0), name="Orange"),
        PaletteColor(hexCode="#FFFF00", name="Yellow"),
        PaletteColor(hexCode="#FF00FF", name="Magenta"),
        PaletteColor(rgbValues=(128, 0, 255), name="Purple"),
        PaletteColor(rgbValues=(128, 255, 0), name="Green")
    ]

    def test_palette_to_string(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        assert str(palette) == "Palette 'My test palette' - 5 colors."

    def test_palette_get_colors(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        assert palette.colors == {color.name: color for color in self.TEST_PALETTE_COLORS}

    def test_palette_add_color(self):
        palette = Palette("My test palette")
        palette.add(self.TEST_PALETTE_COLOR)
        assert palette.colors == {self.TEST_PALETTE_COLOR.name: self.TEST_PALETTE_COLOR}

    def test_palette_get_color(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        assert palette.getColor("Orange").rgbValues == (255, 128, 0)

    def test_palette_get_names(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        assert palette.names == set([color.name for color in self.TEST_PALETTE_COLORS])

    def test_palette_get_rgb_values(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        assert palette.rgbValues == set([color.rgbValues for color in self.TEST_PALETTE_COLORS])

    def test_palette_get_hexcodes(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        assert palette.hexCodes == set([color.hex for color in self.TEST_PALETTE_COLORS])

    def test_palette_find_color_from_rgb(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        assert palette.findColorFromRGB((128, 0, 255)).name == "Purple"

    def test_palette_find_color_from_hex(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        assert palette.findColorFromHexCode("#ff00ff").name == "Magenta"

    def test_palette_length(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        assert palette.length() == len(self.TEST_PALETTE_COLORS)

    def test_palette_clear(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        palette.clear()
        assert palette.length() == 0

    def test_palette_delete_color(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        palette.delete("Magenta")
        assert not palette.getColor("Magenta") and palette.length() == len(self.TEST_PALETTE_COLORS) - 1

    def test_palette_rename(self):
        newName = "Renamed"
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        palette.rename(newName)
        assert palette.name == newName

    def test_palette_update(self):
        palette = Palette("My test palette", self.TEST_PALETTE_COLORS)
        palette.update("Magenta", self.TEST_PALETTE_COLOR)
        assert palette.getColor("Magenta").rgbValues == self.TEST_PALETTE_COLOR.rgbValues

    def test_palette_from_bitmap(self):
        palette = Palette.sNewFromBitmap(path.join(TEST_RESOURCES_DIR, "ral_classic_palette.png"))
        assert palette.name == "ral_classic_palette" and palette.length() == 216 and palette.findColorFromHexCode("#BF3922")

    def test_palette_from_csv(self):
        csvColorProcessor = CSVColorProcessor()
        palette = Palette.sNewFromCSV(path.join(TEST_RESOURCES_DIR, "ral_classic.csv"), csvColorProcessor)
        assert palette.name == "ral_classic" and palette.length() == 216 and palette.getColor("RAL 2002").hex == "#BF3922"

# ---

if "__main__" == __name__:
    pytest.main([__file__, "-v"])
