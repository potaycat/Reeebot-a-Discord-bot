import subprocess

print("launching ComfyUI")
subprocess.Popen(["python", "ComfyUI/main.py"])

import os
import runpod
import requests
import time
import base64
from PIL import Image
from io import BytesIO


def check_api_availability(host):
    i = 0
    while i < 1000:
        try:
            response = requests.get(host)
            return
        except requests.exceptions.RequestException as e:
            print(f"API is not available, retrying in 200ms... ({e})")
        except Exception as e:
            print("something went wrong")
        time.sleep(200 / 1000)
        i += 1


check_api_availability("http://127.0.0.1:8188/prompt")

print("run handler")


def handler(event):
    """
    This is the handler function that will be called by the serverless.
    """
    print("got event")
    print(event)

    try:
        input_ = event["input"]
        image_url = input_.pop("img_url")
        img_data = requests.get(image_url).content
        img_name = image_url.split("/")[-1].split("?")[0]
        with open(f"ComfyUI/input/{img_name}", "wb") as handler:
            handler.write(img_data)

        p = {"prompt": input_}
        res = requests.post("http://127.0.0.1:8188/prompt", json=p)
        try:
            prompt_id = res.json()["prompt_id"]
        except Exception as e:
            print("PROMPT ERROR! details below vvvvv")
            print(res.json())
            return res.json()

        i = 0
        while i < 1000:
            res2 = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}")
            if output_ := res2.json():
                break
            print("generating...", output_)
            time.sleep(200 / 1000)
            i += 1

        im_list = []
        for k, v in input_.items():
            if v["class_type"] == "SaveImage":
                node_ind = k
                break
        for img in output_[prompt_id]["outputs"][node_ind]["images"]:
            with open(
                os.path.join("ComfyUI/output", img["filename"]), "rb"
            ) as image_file:
                data = base64.b64encode(image_file.read())
            im_list.append(str(data))

        json = {"outputs": im_list}
        return json

    except Exception as e:
        return {"error": e}


runpod.serverless.start({"handler": handler})
