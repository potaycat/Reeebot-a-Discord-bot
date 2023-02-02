from .pygmalion.model import run_raw_inference
from .pygmalion.prompting import build_prompt_for
from .pygmalion.parsing import parse_messages_from_str
import typing as t


class GPTWrapper:
    initialized = False

    def __init__(self, llm):
        from transformers import AutoTokenizer, AutoModelForCausalLM

        GPTWrapper.tokenizer = AutoTokenizer.from_pretrained(llm)
        GPTWrapper.model = AutoModelForCausalLM.from_pretrained(llm).to("cpu")
        GPTWrapper.generation_settings = {
            "do_sample": True,
            "max_new_tokens": 42,
            "temperature": 0.9,
            "top_p": 0.3,
            "top_k": 0,
            "typical_p": 1.0,
            "repetition_penalty": 1.05,
        }
        GPTWrapper.char_settings = {
            "char_name": "Reon",
            "_user_name": None,
            "char_persona": "A boy cat",
            "char_greeting": "Meow! Good morning!",
            "world_scenario": "You meet the boy cat. He is happy to see you.",
            "example_dialogue": "You: Can you meow for me?\nReon: Yes I can! Meow!\nYou: You're such a good cat\nReon: I am a good cat~\n",
        }

        GPTWrapper.initialized = True

    @staticmethod
    def inference_fn(
        history: t.List[str],
        user_input: str,
        generation_settings: t.Dict[str, t.Any],
        char_settings: t.Dict[str, t.Any],
    ) -> str:
        """
        https://github.com/PygmalionAI/gradio-ui
        """
        char_greeting = char_settings["char_greeting"]
        char_name = char_settings["char_name"]
        if len(history) == 0 and char_greeting is not None:
            return f"{char_name}: {char_greeting}"

        prompt = build_prompt_for(
            history=history,
            user_message=user_input,
            char_name=char_name,
            char_persona=char_settings["char_persona"],
            example_dialogue=char_settings["example_dialogue"],
            world_scenario=char_settings["world_scenario"],
        )

        model_output = run_raw_inference(
            GPTWrapper.model,
            GPTWrapper.tokenizer,
            prompt,
            user_input,
            **generation_settings,
        )

        generated_messages = parse_messages_from_str(model_output, ["You", char_name])
        bot_message = generated_messages[0]

        return bot_message
