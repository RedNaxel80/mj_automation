import openai
from enum import Enum
import config

API_KEY = config.GPT_API_KEY


class Model(Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo",
    GPT_4 = "gpt-4",
    TEXT_DAVINCI_003 = "text-davinci-003"

