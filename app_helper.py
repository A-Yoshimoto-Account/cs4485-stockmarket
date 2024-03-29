import os
import constants
import brains.openai_api.openai_controller as openai_api
import brains.milvus_access.milvus_controller as milvus
from brains.openai_api.query_refiner import QueryRefiner

class ModelController:
	def __init__(self, disable_embeds: bool = False, disable_completions: bool = False):
		self.openai = openai_api.OpenAIController(
			os.getenv(constants.OPENAI_ENV_VAR),
			disable_embeds=disable_embeds,
			disable_completions=disable_completions
		)

		milvus.connect(alias=constants.ALIAS, host=constants.HOST, port=constants.PORT)
		self.milvus_access = milvus.TextEmbeddingTableController(
			name=constants.CONTEXTS_TABLE,
			primary_key=constants.CONTEXTS_PK,
			text_col=constants.CONTEXTS_TEXT_COL,
			embed_col=constants.CONTEXTS_EMBED_COL
		)
		self.milvus_access.load_collection()

		"""_summary_ Ask a question to the model and return the response.
		Args:
			self (ModelController): The instance of the class.
			answering_endpoint (str): The OpenAI endpoint to use for answering.
			answering_model (str): The OpenAI model to use for answering.
			question (str): The question to ask the model.
			ksim (int): The number of similiar articles to refine answer.
			memory (list[dict[str, str]]): The previous questions to use as context.
			refine (str): The type of refinement to use.
		Returns:
			OpenAI response (str): The response from the model.
			or
			QueryRefiner response (str): The response from the model.
		"""
	def ask_question(
			self,
			answering_endpoint: str,
			answering_model: str,
			question: str,
			ksim: int = 1,
			memory: list[dict[str, str]] = [],
			refine: str = None,
	):
		# get embeddings of question with OpenAIController
		q_embed_list = self.openai.access_model(openai_api.EMBEDDING, openai_api.EMBEDDING_MODELS[0], text=question)
		print(f'Got {len(q_embed_list)} embeddings for [{question}]')
		# get most similar contexts with Milvus controller
		most_similar_contexts: list[str] = self.milvus_access.get_similar_contexts(query_embeds=q_embed_list)
		print(f'Got {len(most_similar_contexts)} contexts for [{question}]')
		if len(most_similar_contexts) > ksim:
			most_similar_contexts = most_similar_contexts[:ksim]
		# if no refiner is specified, directly call OpenAI
		if not refine:
			return self.openai.access_model(
				answering_endpoint,
				answering_model,
				question=question,
				ksim=most_similar_contexts[0],
				memory=memory
			)
		# if a refiner is specified, use QueryRefiner
		return QueryRefiner.query(
			self.openai,
			refine,
			answering_endpoint,
			answering_model,
			question,
			most_similar_contexts,
			memory
		)


