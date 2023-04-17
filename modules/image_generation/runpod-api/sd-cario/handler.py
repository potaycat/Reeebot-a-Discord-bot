import runpod

## load your model(s) into vram here
import torch
from diffusers import (
    DiffusionPipeline,
    AutoencoderKL,
    EulerAncestralDiscreteScheduler,
    UNet2DConditionModel,
)
from safetensors.torch import load_file
import base64
from io import BytesIO


DEVICE = "cuda"
DTYPE = torch.float16


def apply_lora(pipeline, lora_path, alpha=0.7):
    # https://github.com/huggingface/diffusers/issues/3064
    LORA_PREFIX_UNET = "lora_unet"
    LORA_PREFIX_TEXT_ENCODER = "lora_te"
    state_dict = load_file(lora_path)
    visited = []
    for key in state_dict:
        if ".alpha" in key or key in visited:
            continue
        if "text" in key:
            layer_infos = (
                key.split(".")[0].split(LORA_PREFIX_TEXT_ENCODER + "_")[-1].split("_")
            )
            curr_layer = pipeline.text_encoder
        else:
            layer_infos = key.split(".")[0].split(LORA_PREFIX_UNET + "_")[-1].split("_")
            curr_layer = pipeline.unet
        temp_name = layer_infos.pop(0)
        while len(layer_infos) > -1:
            try:
                curr_layer = curr_layer.__getattr__(temp_name)
                if len(layer_infos) > 0:
                    temp_name = layer_infos.pop(0)
                elif len(layer_infos) == 0:
                    break
            except Exception:
                if len(temp_name) > 0:
                    temp_name += "_" + layer_infos.pop(0)
                else:
                    temp_name = layer_infos.pop(0)
        pair_keys = []
        if "lora_down" in key:
            pair_keys.append(key.replace("lora_down", "lora_up"))
            pair_keys.append(key)
        else:
            pair_keys.append(key)
            pair_keys.append(key.replace("lora_up", "lora_down"))
        if len(state_dict[pair_keys[0]].shape) == 4:
            weight_up = state_dict[pair_keys[0]].squeeze(3).squeeze(2).to(torch.float32)
            weight_down = (
                state_dict[pair_keys[1]].squeeze(3).squeeze(2).to(torch.float32)
            )
            curr_layer.weight.data += alpha * torch.mm(
                weight_up, weight_down
            ).unsqueeze(2).unsqueeze(3)
        else:
            weight_up = state_dict[pair_keys[0]].to(torch.float32)
            weight_down = state_dict[pair_keys[1]].to(torch.float32)
            curr_layer.weight.data += alpha * torch.mm(weight_up, weight_down)
        for item in pair_keys:
            visited.append(item)
    return pipeline


vae = AutoencoderKL.from_pretrained("crosskemono2VAE", torch_dtype=DTYPE)
scheduler = EulerAncestralDiscreteScheduler(
    beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear"
)
unet = UNet2DConditionModel.from_pretrained(
    "andite/anything-v4.0",
    subfolder="unet",
    torch_dtype=DTYPE,
)
pipe = DiffusionPipeline.from_pretrained(
    "ckpt/anything-v4.5",
    vae=vae,
    scheduler=scheduler,
    unet=unet,
    torch_dtype=DTYPE,
)
safety_checker = pipe.safety_checker
generator = torch.Generator(DEVICE)


def handler(event):
    print(event)
    x = event["input"]
    prompt = x.get("prompt", "")
    negative_prompt = x.get("negative_prompt", "")
    seed = int(x.get("seed", 0))
    steps = int(x.get("steps", 28))
    cfg_scale = float(x.get("cfg_scale", 7.0))
    safe = bool(x.get("safety_check", True))
    lora = x.get("lora", "LucarioLoRA.safetensors")
    lora_weight = float(x.get("lora_weight", 0.8))

    if safe:
        pipe.safety_checker = safety_checker
    else:
        pipe.safety_checker = None
    apply_lora(pipe, lora, lora_weight)
    pipe.to(DEVICE)
    out = pipe(
        prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=cfg_scale,
        generator=generator.manual_seed(seed),
    )
    buffered = BytesIO()
    out.images[0].save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return_json = {
        "input": x,
        "output": img_str.decode("utf-8"),
        "nsfw_content_detected": str(out.nsfw_content_detected),
    }
    return return_json


runpod.serverless.start({"handler": handler})
