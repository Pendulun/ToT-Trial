from abc import ABC, abstractmethod
from openai import OpenAI


class Evaluator(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def answer(self, text: str) -> str:
        pass


class LocalLLMEvaluator(Evaluator):
    """
    This is the evaluator to be used when running the local-llm project
    from google.
    """

    def __init__(self, url: str):
        super().__init__()
        self.client = OpenAI(
            api_key="foo",
            base_url=url,
        )

    def answer(self, text: str) -> str:
        chat_completion = self.client.chat.completions.create(messages=[
            {
                "role": "user",
                "content": text,
            },
        ],
                                                              model="")
        for choice in chat_completion.choices:
            response = choice.message.content

        return response
