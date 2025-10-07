import torch
from diffusers import DiffusionPipeline, AutoencoderKL, DPMSolverMultistepScheduler
from safetensors.torch import load_file
from sdscripts.networks.lora import create_network_from_weights
import time


if torch.cuda.is_available():
    DEVICE = "cuda"
    DTYPE = torch.float16
else:
    DEVICE = "cpu"
    DTYPE = torch.float32
print("DEVICE:", DEVICE)


def apply_lora(pipe, lora_path, weight=1.0):
    vae = pipe.vae
    text_encoder = pipe.text_encoder
    unet = pipe.unet
    sd = load_file(lora_path)
    lora_network, sd = create_network_from_weights(
        weight, None, vae, text_encoder, unet, sd
    )
    lora_network.apply_to(text_encoder, unet)
    lora_network.load_state_dict(sd)
    lora_network.to(DEVICE, dtype=DTYPE)


vae = AutoencoderKL.from_pretrained(
    "hakurei/waifu-diffusion", subfolder="vae", torch_dtype=DTYPE
)
scheduler = DPMSolverMultistepScheduler.from_pretrained(
    "andite/anything-v4.0", subfolder="scheduler"
)
pipe = DiffusionPipeline.from_pretrained(
    "ckpt/anything-v4.5",
    vae=vae,
    scheduler=scheduler,
    torch_dtype=DTYPE,
)
# https://github.com/huggingface/diffusers/issues/3064
# pipe.unet.load_attn_procs('LucarioLoRA.safetensors', use_safetensors=True)
apply_lora(pipe, "LucarioLoRA.safetensors", 0.7)
pipe.to(DEVICE)

safety_checker = pipe.safety_checker
generator = torch.Generator("cpu")


prompt = "lucario, lucario, masterpiece, best quality, 1girl, white hair, medium hair, cat ears, closed eyes, looking at viewer, :3, cute, scarf, jacket, outdoors, streets"
negative_prompt = "easynegative, bad_prompt, normal quality, bad quality"
seed = 2175400045
steps = 70
cfg_scale = 7.0



while 1:
    print("AAAAAA")
    start_time = time.perf_counter()

    pipe.safety_checker = None
    out = pipe(
        prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=cfg_scale,
        generator=generator.manual_seed(seed),
    )
    # [display(im) for im in out.images]

    end_time = time.perf_counter()

    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time)


    time.sleep(60)