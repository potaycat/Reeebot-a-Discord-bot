from diffusers import *

try:
    UNet2DConditionModel.from_pretrained("xyn-ai/anything-v4.0", subfolder="unet")
except:
    pass
try:
    DiffusionPipeline.from_pretrained("ckpt/anything-v4.5")
except:
    pass

print("CACHED")
