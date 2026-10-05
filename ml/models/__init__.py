from ml.models.unet import UNet
from ml.models.deeplabv3 import DeepLabV3PlusLite
from ml.models.segformer import SegFormerTiny
def create_model(name,in_channels=3,num_classes=6):
    key=name.lower()
    if key=="unet": return UNet(in_channels,num_classes)
    if key in {"deeplabv3plus","deeplabv3+","deeplab"}: return DeepLabV3PlusLite(in_channels,num_classes)
    if key=="segformer": return SegFormerTiny(in_channels,num_classes)
    raise ValueError(f"Unknown model architecture: {name}")
