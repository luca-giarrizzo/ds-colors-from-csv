from os import path
from PIL import Image
from sd.api import SDValueColorRGBA, SDValueFloat

from sd.api.sbs.sdsbscompnode import SDSBSCompNode
from sd.api.sbs.sdsbscompgraph import SDSBSCompGraph

from palette import Palette, PaletteColor
from utilities import getLogger

from typing import cast

# ---

def uniformColorNodesToPaletteColors(uniformColorNodes: list[SDSBSCompNode]) -> list[PaletteColor] | None:
    if len(uniformColorNodes) == 0:
        getLogger().warning(f"No Uniform color nodes provided to create palette colors.")
        return None
    paletteColors: list[PaletteColor] = []
    for node in uniformColorNodes:
        colorSDValue = node.getInputPropertyValueFromId("outputcolor")
        if colorSDValue is None:
            getLogger().warning(f"No 'outputcolor' input property found for node {node.getIdentifier()}.")
            return None
        elif isinstance(colorSDValue, SDValueColorRGBA):
            color = PaletteColor.sNewFromSDValueRGBA(colorSDValue)
        elif isinstance(colorSDValue, SDValueFloat):
            color = PaletteColor.sNewFromSDValueFloat(colorSDValue)
        else:
            getLogger().warning(f"Unsupported SDValue: {colorSDValue}")
            return None
        paletteColors.append(color)
    getLogger().info(f"Colors acquired: {', '.join([str(c) for c in paletteColors])}")
    return paletteColors


def paletteColorsToUniformColorNodes(
    paletteColors: list[PaletteColor], graph: SDSBSCompGraph | None) -> list[SDSBSCompNode] | None:
    if len(paletteColors) == 0:
        getLogger().warning(f"No palette colors provided to create Uniform color nodes.")
        return None
    if graph is None:
        getLogger().warning(f"No graph provided to host new Uniform color nodes.")
        return None
    uniformColorNodes: list[SDSBSCompNode] = []
    for paletteColor in paletteColors:
        node = graph.newNode("sbs::compositing::uniform")
        node = cast(SDSBSCompNode, node)
        node.setInputPropertyValueFromId("outputcolor", paletteColor.colorToSDValueRGBA())
        uniformColorNodes.append(node)
    return uniformColorNodes


def paletteToBitmap(palette: Palette, outputDir: str, size: tuple[int, int] = (256, 1)) -> str | None:
    if path.isdir(outputDir):
        outputPath = path.join(outputDir, palette.name + ".png")
    else:
        getLogger().error(f"Output directory does not exist: {outputDir}")
        return None
    if palette.length() == 0:
        getLogger().warning(f"Cannot save image: Palette '{palette.name}' is empty.")
        return None
    paletteImage = Image.new("RGB", size)
    paletteImage.putdata(list(palette.rgbValues))
    try:
        paletteImage.save(outputPath)
        return outputPath
    except Exception as e:
        getLogger().error(f"Failed to save image: {e}")
        return None

# TODO Move this to Palette class as a static method?
def bitmapToPalette(bitmapPath: str) -> Palette | None:
    image = Image.open(bitmapPath)
    if image.mode not in Palette.SUPPORTED_COLOR_MODES:
        getLogger().warning(f"Unsupported color mode: '{image.mode}'. Cannot create palette.")
        return None
    pixelValues = list(image.get_flattened_data())
    palette = Palette(name=path.splitext(path.basename(bitmapPath))[0])
    for value in pixelValues:
        if image.mode == "RGBA":
            value = cast(tuple[int, int, int, int], value)
            palette.add(PaletteColor.sNewFromRGBA(value))
        elif image.mode == "L":
            palette.add(PaletteColor.sNewFromLuminance(value[0]))
    return palette
