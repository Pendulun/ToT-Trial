import time
from abc import ABC, abstractmethod

from openai import OpenAI, OpenAIError
from transformers import pipeline

from utils import timer_dec


class LLM(ABC):
    """
    This is a LLM wrapper. It receives the model name and defines a function for it to answer the query
    """

    def __init__(self, model_name: str = "", **kwargs):
        self.model_name = model_name

    @abstractmethod
    def answer(self, data: list[dict], **kwargs) -> list[dict]:
        pass


class URLLLM(LLM):
    """
    It first connects to the given url using the token and
    then can answer the given text. This is useful when running local-llm
    """

    def __init__(self,
                 model_name: str = "",
                 url: str = "",
                 token: str = 'foo',
                 **kwargs):
        super().__init__(model_name, **kwargs)
        self.client = OpenAI(
            api_key=token,
            base_url=url,
        )

    @timer_dec
    def answer(self, data: list[dict[str, str]], **kwargs) -> list[dict]:
        """
        Data is a list of dict of instances. For this LLM, each dict must have 'question'
        and 'context' keys.
        """
        for attempt in range(5):
            responses = list()
            try:
                for instance in data:
                    content = instance['context'] + "\n" + instance['question']
                    chat_completion = self.client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": content,
                            },
                        ],
                        model=self.model_name,
                        **kwargs)
                    for choice in chat_completion.choices:
                        responses.append({'answer': choice.message.content})
            except OpenAIError as e:
                error_message = str(e)
                if "is currently loading" in error_message:
                    print(
                        f"Attempt {attempt + 1}/5: Model is still loading. Waiting 10 seconds to try again..."
                    )
                    time.sleep(10)
                else:
                    print(f"Unnespected error: {error_message}")
                    raise e
            else:
                return responses
        raise RuntimeError(f"The model didn't load after many tries.")


class HuggingFaceQuestionAnsweringLLM(LLM):
    """
    This uses the question-answering pipeline from hugging face using the provided model.
    If the model_name is empty or None, it uses the default from the pipeline
    """

    def __init__(self, model_name: str, device='cpu', **kwargs):
        if model_name.strip() == "":
            model_name = None
        super().__init__(model_name, **kwargs)
        self.pipeline = pipeline("question-answering",
                                 model=self.model_name,
                                 device=device)

    @timer_dec
    def answer(self, data: list[dict[str, str]], **kwargs) -> list[dict]:
        """
        Data is a list of dict of instances. For this LLM, each dict must have 'question'
        and 'context' keys. This allows for batched processing

        Return a list of dicts of answers. Each dict has a 'answer' and 'score' key.
        """
        questions = [item["question"] for item in data]
        contexts = [item["context"] for item in data]

        results = self.pipeline(question=questions, context=contexts)

        if type(results) == dict:
            results = [results]

        return results
