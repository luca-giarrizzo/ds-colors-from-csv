from sd.api import SDValueColorRGBA, SDValueFloat

from sd.api.sbs.sdsbscompnode import SDSBSCompNode
from sd.api.sbs.sdsbscompgraph import SDSBSCompGraph

from palette import PaletteColor
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
