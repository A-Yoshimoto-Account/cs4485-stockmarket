import openai
import time
from typing import Union
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

def openai_error_handler(
    func,
    init_delay=60,
    expo_base=2,
    ratelimiterror=(openai.error.RateLimitError),
    servererror=(openai.error.APIError, openai.error.Timeout, openai.error.ServiceUnavailableError),
    invalidreq=(openai.error.InvalidRequestError, openai.error.AuthenticationError),
    rle_max_retries=5,
    servererr_max_retries=5,
):
    '''
    Decorator function for error handling requests to the OpenAI API
    Done as a measure to prevent errors from disrupting large contiguous access to the API
    '''
    def wrapper(*args, **kwargs):
        rle_retries = 0
        servererr_retries = 0
        delay = init_delay
        while True:
            try:
                return func(*args, **kwargs)
            except ratelimiterror as e:
                rle_retries += 1
                if rle_retries > rle_max_retries:
                    raise Exception(f'Exceeded maximum number of retries ({rle_max_retries})')
                print(f'RateLimitError: Sleeping for {delay} seconds')
                time.sleep(delay)
                delay *= expo_base
                print(f'Next error wait time is {delay} seconds. {rle_max_retries - rle_retries} RateLimitError retries remaining')
            except invalidreq as e:
                raise e
            except servererror as e:
                servererr_retries += 1
                if servererr_retries > servererr_max_retries:
                    print('Returning None for this request')
                    return None
                print('Encountered server error:', e)
                print(f'Sleeping for {delay} seconds')
                time.sleep(delay)
                delay *= expo_base
                print(f'Next error wait time is {delay} seconds. {servererr_max_retries - servererr_retries} server error retries remaining')
            except Exception as e:
                raise e
    return wrapper

class OpenAIController:
    def __init__(self, api_key: str, disable_embeds: bool = False, disable_completions: bool = False, **kwargs):
        openai.api_key = api_key
        self.disable_embeds = disable_embeds
        self.disable_completions = disable_completions
        self.prompter = OpenAIPromptCreator(**kwargs)

        """_summary_ = 'OpenAI API Controller' Accessing the model based on the endpoint and model name
        Args:
        self (OpenAIController): OpenAIController object
        endpoint (str): The endpoint to access
        model (str): The model to use
        kwargs: The parameters to pass to the endpoint
        
        Returns:
        Response from the OpenAI API endpoint
        """
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

    """_summary_ = Accessing the embedding model
    Args:
    self (OpenAIController): OpenAIController object
    model (str): The model to use
    text (str): The text to embed
    """
    @openai_error_handler
    def _embedding(
            self,
            model: str,
            text: Union[str , list],
    ) -> list[int]:
        if self.disable_embeds:
            return [[0] * EMBEDDING_LENGTH]
        resp = openai.Embedding.create(
            model=model,
            input=text,
        )
        return [data['embedding'] for data in resp['data']]

    """_summary_ = Accessing the completion model
    Args:
    self (OpenAIController): OpenAIController object
    model (str): The model to use
    question (str): The question to ask
    context (str): The context to use
    
    Returns:
    response from the OpenAI API endpoint
    """
    @openai_error_handler
    def _completion(
            self,
            model: str,
            question: str,
            context: str,
    ) -> str:
        if self.disable_completions:
            return OpenAIController._placeholder_response(question)

        prompt = self.prompter.create_completion_prompt(question, context)
        resp = openai.Completion.create(
            model=model,
            prompt=prompt,
        )
        return resp['choices'][0]['text']

    """_summary_ = Accessing the chat completion model
    Args:
    self (OpenAIController): OpenAIController object
    model (str): The model to use
    question (str): The question to ask
    context (str): The context to use
    memory (list[dict[str, str]]): The memory to use
    
    Returns:
    response from the OpenAI API endpoint
    """
    @openai_error_handler
    def _chat_completion(
            self,
            model: str,
            question: str,
            context: str,
            memory: list[dict[str, str]],
    ) -> str:
        if self.disable_completions:
            return OpenAIController._placeholder_response(question)
        messages = self.prompter.create_chat_messages(question, context, memory)
        resp = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )
        return resp['choices'][0]['message']['content']

    """_summary_ = Placeholder response for when completions are disabled"""
    def _placeholder_response(
            question: str
    ) -> str:
        return 'placeholder answer'

    _placeholder_response = staticmethod(_placeholder_response)
