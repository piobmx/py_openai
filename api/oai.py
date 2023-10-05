import openai
from prompts import prompt


class OaiAPI:
    def __init__(self) -> None:
        self.api_base = "https://openkey.cloud/v1"
        self.api_key = "sk-vr0WxtlOTSrf54PoKZXo1TtBDiYUU83hrMqOAUbyM5Eezg2q"
        self.remote = openai
        self.remote.api_base = self.api_base
        self.remote.api_key = self.api_key
        self.answer = ""

    def get_answer(self):
        return self.answer

    def react(self, user_prompt) -> None:
        final_prompt = f"a fragment snippit for '{user_prompt}'"

        print(prompt)
        print(final_prompt)

        self.reply = self.remote.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.0,
            stream=True)

    def react_without_system_prompt(self, user_prompt) -> None:
        final_prompt = f"{user_prompt}"
        self.reply = self.remote.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.0,
            stream=True
        )


    def yield_response(self):
        for resp in self.reply:
            if "content" in resp['choices'][0]['delta']:
                yield resp['choices'][0]['delta']['content']


    def print_reply(self):
        self.answer = ""

        for resp in self.reply:
            if "content" in resp['choices'][0]['delta']:
                word = resp['choices'][0]['delta']['content']
                self.answer += word  
