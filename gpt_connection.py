import openai
from enum import Enum

API_KEY = "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"


class Model(Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo",
    GPT_4 = "gpt-4",
    TEXT_DAVINCI_003 = "text-davinci-003"

