import time

from openai import OpenAI, OpenAIError


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
        for _ in range(5):  # Tentar até 5 vezes
            try:
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
                    return choice.message.content
            except OpenAIError as e:
                if e.http_status == 503 and "model is currently loading" in str(
                        e):
                    print(
                        "Modelo carregando. Tentando novamente em 10 segundos..."
                    )
                    time.sleep(
                        10)  # Aguarde 10 segundos antes de tentar novamente
                else:
                    raise e
        raise RuntimeError("O modelo não carregou após múltiplas tentativas.")
