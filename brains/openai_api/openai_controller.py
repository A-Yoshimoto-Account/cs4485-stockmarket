import openai

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
	def __init__(self, api_key, disable=False):
		openai.api_key = api_key
		self.disable = disable
	
	def access_model(self, endpoint, model, text, **kwargs):
		if endpoint not in ENDPOINTS:
			raise Exception(f'{endpoint} endpoint is not supported')

		if endpoint == CHATCOMPLETION or endpoint == COMPLETION:
			ksim = kwargs['ksim']
			memory = kwargs['memory']
			refine = kwargs['refine']
			return self._chat_completion(text, ksim, memory, refine, **kwargs)
		elif endpoint == COMPLETION:
			model_id = kwargs['model_id']
			ksim = kwargs['ksim']
			memory = kwargs['memory']
			refine = kwargs['refine']
			return self._completion(text, model_id, ksim, memory, refine, **kwargs)
		elif endpoint == EMBEDDING:
			return self._embedding(text, **kwargs)

	def _embedding(self, text: str, **kwargs) -> list[int]:
		if not self.disable:
			return [0] * EMBEDDING_LENGTH
		return []
	
	def _chat_completion(self,
		question,
		ksim: int =1,
		memory: list =[],
		refine: str =None,
		**kwargs,
	) -> dict:
		if not self.disable:
			return OpenAIController._placeholder_response(question)
		return {}
	
	def _completion(self,
		question: str,
		ksim: int =0,
		memory: list =[],
		refine: str =None,
		**kwargs,
	) -> dict:
		if not self.disable:
			return OpenAIController._placeholder_response(question)
		return {}

	def _placeholder_response(question: str):
		return {'question': question, 'answer': 'placeholder answer'}

	_placeholder_response = staticmethod(_placeholder_response)
