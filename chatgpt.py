import openai
from enum import Enum

API_KEY = "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"


class Model(Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo",
    GPT_4 = "gpt-4",
    TEXT_DAVINCI_003 = "text-davinci-003"


class ChatGPT:
    def __init__(self, api_key=API_KEY, model="gpt-3.5-turbo", limit=200):
        if model not in [Model.GPT_4, Model.GPT_3_5_TURBO, Model.TEXT_DAVINCI_003]:
            raise ValueError("Invalid model name. Choose from 'gpt-3.5-turbo', 'gpt-4', 'text-davinci-003'.")

        self.api_key = api_key
        openai.api_key = self.api_key
        self.model = model
        self.limit = limit

    def query(self, messages):
        completion = openai.ChatCompletion.create(model=self.model, messages=messages)
        print(completion)
        return completion.choices[0].message.content


def main():
    chat_gpt = ChatGPT()
    response = chat_gpt.query([{"role": "user", "content": "What's the best baseball team in the world?"}])
    print(response)


# import requests
# import json
#
# API_KEY = "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"
# PROMPT_DEFAULT = f"""I want you to act as a prompt engineer. You will help me write prompts for an ai art generator called Midjourney.
# I will provide you with short content ideas and your job is to elaborate these into full, explicit, coherent prompts.
# Prompts involve describing the content and style of mages in concise accurate language. It is useful to be explicit and use references to popular culture, artists and mediums. Your focus needs to be on nouns and adjectives. I will give you some example prompts for your reference. Please define the exact camera that should be used
# Here is a formula for you to use: (content: insert nouns here) (medium: insert artistic medium here) (style: insert references to genres, artists and popular culture here) (lighting, reference the lighting here) (colours reference color styles and palettes here)(composition: reference camera, specific lenses, shot types and positional elements here)
# Examples of medium: block print, folk art, cyanotype, graffiti, paint-by-numbers, risograph, ukiyo-e, pencil sketch, watercolor, pixel art, blacklight painting, cross stick, pixel art, photography, 3d, etc.
# Examples of styles for pencis sketch: life drawing, continuous line, loose gestural, blind contour, value study, charcoal sketch, etc. Any style can have such specific details.
#
# If the prompt describes characters, you can use emotions they express, for example: determined, happy, sleepy, angry, shy, embarassed - this works for both real characters, like people, pets, animals, but also for imagined characters like cartoons or antropomorphized ones as well.
# For color palletes you can be very specific, for example: millenial pink, acid green, sesaturated, canary yellow, peach, two toned, pastel, mauve, ebony, neutral, day glo, green tinted, etc.
# You can also specify locations, for example: tundra, salt flat, jungle, desert, mountain, cloud forest, etc.
# From the formula remove the brackets and keywords: content, medium, style, lighting, composition, but you can use them in the prompt if needed. Don't insert instructions, just description (e.g. "Soft morning light" instead of "The lighting should be a soft morning light"). You need to specify the preferred main style - photography, drawing, cartoon, 3D, manga etc.
#
# Example prompt:
# Portrait of a Celtic Jedi Centinel with wet Shamrock Armor, green lightsaber, by Aleksi Briclot, shiny wet dramatic lighting
#
# I want you to suggest {input('Number of prompts: ')} prompts for: {input("Topic: ")}
# Give them in a single message, without any additional comments, notes, additions, bullets or numbered lists. Just the prompts, one after another, each on a new line. You can use the formula above to help you.
# """
#
#
# class ChatGPT:
#     def __init__(self, api_key, max_tokens=200):
#         self.api_key = api_key
#         self.max_tokens = max_tokens
#         self.model = "gpt-3.5-turbo"
#         self.prompt = None
#         self.response = None
#
#     def query(self, prompt=PROMPT_DEFAULT):
#         url = f"https://api.openai.com/v1/engines/{self.model}/chat/completions"
#
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": "Bearer " + self.api_key
#         }
#
#         data = {
#             "prompt": prompt,
#             "max_tokens": self.max_tokens,
#         }
#
#         self.response = None
#         response = requests.post(url, headers=headers, data=json.dumps(data))
#         response_json = response.json()
#         try:
#             self.response = response_json['choices'][0]['text'].strip()
#         except KeyError:
#             print(f"Error: {response_json}")
#
#
# def main():
#     gpt = ChatGPT(API_KEY)
#
#     messages = [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": input("Enter your message: ")}
#     ]
#
#     gpt.query(messages)
#     print(f"AI response: \n{gpt.response}")
#
#
# if __name__ == "__main__":
#     main()
