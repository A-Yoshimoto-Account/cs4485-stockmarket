import openai
from brains.openai_api.prompting import OpenAIPromptCreator

# edit to make it access OpenAI once, instead of multiple times

EMBEDDING_LENGTH = 1536
CHATCOMPLETION = 'chatcompletion'
COMPLETION = 'completion'
EMBEDDING = 'embedding'
ENDPOINTS = [CHATCOMPLETION, COMPLETION, EMBEDDING]

EMBEDDING_MODELS = ['text-embedding-ada-002']
CHATCOMPLETION_MODELS = ['gpt-3.5-turbo']
COMLPETION_MODELS = ['text-davinci-003', 'text-curie-001']


class OpenAIController:
    def __init__(self, api_key: str, disable: bool = False, **kwargs):
        openai.api_key = api_key
        self.disable = disable
        self.prompter = OpenAIPromptCreator(**kwargs)

    def access_model(
            self,
            endpoint: str,
            model: str,
            **kwargs
    ):
        if endpoint not in ENDPOINTS:
            raise Exception(f'{endpoint} endpoint is not supported')

        if endpoint == EMBEDDING:
            if 'text' not in kwargs:
                raise Exception('Embeddings endpoint needs a parameter "text"')
            return self._embedding(model, kwargs['text'])
        elif endpoint == COMPLETION:
            if 'question' not in kwargs or 'context' not in kwargs:
                raise Exception('ChatCompletions endpoint needs parameters "question", "context"')
            return self._completion(model, kwargs['question'], kwargs['context'])
        elif endpoint == CHATCOMPLETION:
            if 'question' not in kwargs or 'context' not in kwargs or 'memory' not in kwargs:
                raise Exception('ChatCompletions endpoint needs parameters "question", "context", "memory"')
            return self._chat_completion(model, kwargs['question'], kwargs['context'], kwargs['memory'])

    def _embedding(
            self,
            model: str,
            text: str
    ) -> list[int]:
        if self.disable:
            return [0] * EMBEDDING_LENGTH
        resp = openai.Embedding.create(
            model=model,
            input=text,
        )
        return [data['embedding'] for data in resp['data']]

    def _completion(
            self,
            model: str,
            question: str,
            context: str,
    ) -> str:
        if self.disable:
            return OpenAIController._placeholder_response(question)

        prompt = self.prompter.create_completion_prompt(question, context)
        resp = openai.Completion.create(
            model=model,
            prompt=prompt,
        )
        return resp['choices'][0]['text']

    def _chat_completion(
            self,
            model: str,
            question: str,
            context: str,
            memory: list[dict[str, str]],
    ) -> str:
        if self.disable:
            return OpenAIController._placeholder_response(question)
        messages = self.prompter.create_chat_messages(question, context, memory)
        resp = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )
        return resp['choices'][0]['message']['content']

    def _placeholder_response(
            question: str
    ) -> str:
        return 'placeholder answer'

    _placeholder_response = staticmethod(_placeholder_response)
