import sd
from sd.api.sdpackage import SDPackage
from sd.api.sdproperty import SDProperty, SDPropertyCategory
from sd.api.sbs.sdsbscompgraph import SDSBSCompGraph
from sd.api.sdtypefloat3 import SDTypeFloat3
from sd.api.sdtypefloat4 import SDTypeFloat4
from sd.api.sdvaluestring import SDValueString

from PIL import Image as PIL_Image
from PIL.Image import Image
import logging

# --- Initialise logger ---

__gLogger = None
def getLogger():
    """
    Get the global logger.
    The logger is created the first time the function is called.
    """
    global __gLogger
    if not __gLogger:
            __gLogger = logging.getLogger("PresetsFromCSV")
            # __gLogger.addHandler(sd.getContext().createRuntimeLogHandler())
            __gLogger.propagate = False
            __gLogger.setLevel(logging.DEBUG)
    return __gLogger

# ---

def gatherGraphColorParameters(graph: SDSBSCompGraph) -> dict[str, SDProperty] | None:
    graphColorParameters: dict[str, SDProperty] = {}
    targetTypes = {SDTypeFloat4, SDTypeFloat3}

    for inputProperty in graph.getProperties(SDPropertyCategory.Input):
        inputPropertyEditor: SDValueString | None = graph.getPropertyAnnotationValueFromId(inputProperty, "editor")
        inputPropertyEditorValue: str = inputPropertyEditor.get() if inputPropertyEditor else ""
        if inputProperty.getType().__class__ in targetTypes and inputPropertyEditorValue == "color":
            graphColorParameters[inputProperty.getId()] = inputProperty

    if graphColorParameters:
        getLogger().info(
            "Color inputs:\n" + "\n".join([f"    - {key}: {value}" for key, value in graphColorParameters.items()]))
        return graphColorParameters
    else:
        getLogger().info("No color inputs found.")
        return None


def gatherCSVResourcesPathsInPackage(package: SDPackage) -> dict[str, str]:
    csvResources: dict[str, str] = {}
    for resource in package.getChildrenResources(isRecursive=True):
            resourceFilepath: str = resource.getFilePath()
            if resourceFilepath.endswith(".csv"):
                    csvResources[resource.getIdentifier()] = resourceFilepath
    return csvResources


def getCSVResourceFilePath(package: SDPackage, resourcePkgPath : str) -> str | None:
    resource = package.findResourceFromUrl(resourcePkgPath)
    if not resource:
        getLogger().warning(f"Resource not found: {resourcePkgPath}")
        return None
    resourceFilePath: str = resource.getFilePath()
    if resourceFilePath.endswith(".csv"):
        return resourceFilePath
    else:
        getLogger().warning(f"Resource is not a CSV file: {resourcePkgPath}")
        return None

def generatePaletteImageFromColors(rgbValues: list[tuple[int, int, int]], size: tuple[int, int] = (256, 1)) -> Image:
    paletteImage = PIL_Image.new("RGB", size)
    paletteImage.putdata(rgbValues)
    return paletteImage
