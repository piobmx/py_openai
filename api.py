import openai
from prompts import prompt


class OaiAPI:
    def __init__(self) -> None:
        self.api_base = "https://openkey.cloud/v1"
        self.api_key = "sk-jIdDi9srkUoVlqVRIo0KQXu9eT6NMIf6t2FYZMQ2QU6eLGMg"
        self.remote = openai
        self.remote.api_base = self.api_base
        self.remote.api_key = self.api_key
        self.answer = ""

    def get_answer(self):
        return self.answer

    def react(self, user_prompt) -> None:
        # print(prompt)
        final_prompt = f"a fragment snipprt for '{user_prompt}'"


        print(prompt)
        print(final_prompt)

        self.reply = self.remote.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.3,
            stream=True)

    async def print_reply(self):
        # print(self.chat_completion_resp)
        reply = ""
        self.answer = ""
        for resp in self.reply:
            if "content" in resp['choices'][0]['delta']:
                word = resp['choices'][0]['delta']['content']
                self.answer += word  # appends the deltas to record the whole response
                print(word, end="")

            # print(resp.choices[0].delta.content, end="", flush=False)


if __name__ == '__main__':
    o = OaiAPI()
    s = o.react("write a circle and a triangle")
    o.print_reply()
