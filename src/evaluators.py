from openai import OpenAI


class LLM():
    """
    This is a LLM wrapper. It first connects to the given url using the token and
    then can answer the given text
    """

    def __init__(self, url: str, token: str = 'foo', model_name: str = ""):
        super().__init__()
        self.client = OpenAI(
            api_key=token,
            base_url=url,
        )
        self.model_name = model_name

    def answer(self, text: str, **kwargs) -> str:
        """
        Return the LLM answer to the given text.
        """
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text,
                },
            ],
            model=self.model_name,
            **kwargs)
        for choice in chat_completion.choices:
            response = choice.message.content

        return response
