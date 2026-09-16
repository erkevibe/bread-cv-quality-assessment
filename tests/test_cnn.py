import numpy as np
from PIL import Image
from torchvision.models import MobileNet_V3_Small_Weights

from breadcv.cnn import build_preprocess


def test_mobilenet_preprocess_supports_current_weight_preset() -> None:
    image = Image.fromarray(np.full((120, 240, 3), 127, dtype=np.uint8))
    tensor = build_preprocess(MobileNet_V3_Small_Weights.DEFAULT, 224)(image)
    assert tuple(tensor.shape) == (3, 224, 224)
    assert tensor.dtype.is_floating_point
