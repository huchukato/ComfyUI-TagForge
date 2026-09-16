import random

from comfy.comfy_types import IO, InputTypeDict

from .wildcards import WildcardLoader


class WildcardProcessorNode:
    _session_usage: dict[str, dict[str, int]] = {}
    MODEL_PRESETS = {
        "None": {
            "positive": "",
            "negative": "",
        },
        "Pony": {
            "positive": "score_9, score_8_up, score_7_up, depth of field, dynamic pose, dynamic angle",
            "negative": "score_6, score_5, score_4, worst quality, low quality, ugly, malformed, bad anatomy, grayscale, watermark",
        },
        "Illustrious": {
            "positive": "masterwork, masterpiece, best quality, detailed, depth of field, high detail, very aesthetic, dynamic pose, dynamic angle, adult",
            "negative": "lowres, worst quality, low quality, bad anatomy, bad hands, jpeg artifacts, signature, watermark, text, logo, extra digits, censored, loli, blurry, deformed, extra limbs, missing limbs, poorly drawn face, poorly drawn hands",
        },
    }

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        return {
            "required": {
                "text": (IO.STRING, {"default": "", "multiline": True, "dynamicPrompts": False,
                                     "tooltip": "Enter a prompt using wildcard syntax. The selected model prefix is added automatically."}),
            },
            "optional": {
                "seed": (IO.INT, {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                                  "tooltip": "Seed for randomization (0 = random)."}),
                "populated_text": (IO.STRING, {"default": "", "multiline": True, "dynamicPrompts": False,
                                               "tooltip": "In populate mode: displays the expanded result (read-only). In fixed mode: editable, used as-is."}),
                "mode": (["populate", "fixed", "reproduce"], {"default": "populate",
                           "tooltip": "Populate: expands wildcards from text on each queue. Fixed: uses populated_text as-is (editable). Reproduce: re-uses populated_text once, then switches back to populate."}),
                "deduplicate": (IO.BOOLEAN, {"default": True,
                                             "tooltip": "Reduce the probability of options already used this session."}),
                "downvote_factor": (IO.FLOAT, {"default": 0.5, "min": 0.01, "max": 1.0, "step": 0.05,
                                              "tooltip": "Probability multiplier applied for each previous use."}),
                "base_model": (list(cls.MODEL_PRESETS), {"default": "Pony",
                                                          "tooltip": "Selects the positive prefix and negative prompt preset."}),
            },
        }

    RETURN_TYPES = (IO.STRING, IO.STRING)
    RETURN_NAMES = ("processed_text", "negative")
    FUNCTION = "process_wildcards"
    CATEGORY = "TagForge"

    @classmethod
    def apply_model_preset(cls, text, base_model="Pony"):
        preset = cls.MODEL_PRESETS.get(base_model, cls.MODEL_PRESETS["Pony"])
        content = (text or "").strip().lstrip(", ")
        for candidate in cls.MODEL_PRESETS.values():
            prefix = candidate["positive"]
            if not prefix:
                continue
            if content == prefix:
                content = ""
                break
            if content.startswith(f"{prefix},"):
                content = content[len(prefix) + 1:].lstrip()
                break
        positive = ", ".join(part for part in (preset["positive"], content) if part)
        return positive, preset["negative"]

    def process_wildcards(self, text, seed=0, populated_text="", mode="populate",
                          deduplicate=True, downvote_factor=0.5, base_model="Pony", **kwargs):
        WildcardLoader.load()
        if mode == "fixed":
            result = populated_text
        else:
            source = populated_text if mode == "reproduce" else text
            actual_seed = seed or random.SystemRandom().randint(1, 0xffffffffffffffff)
            usage = self._session_usage if deduplicate and downvote_factor < 1.0 else None
            result = WildcardLoader.process(source, actual_seed, usage, downvote_factor)
        positive, negative = self.apply_model_preset(result, base_model)
        return {"ui": {"text": [positive]}, "result": (positive, negative)}

    @classmethod
    def reset_session_cache(cls):
        cls._session_usage.clear()
