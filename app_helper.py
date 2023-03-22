import os
import constants
import brains.openai_api.openai_controller as openai_api
import brains.milvus_access.milvus_controller as milvus
from brains.openai_api.query_refiner import QueryRefiner

class ModelController:
	def __init__(self, disable: bool = False):
		self.openai = openai_api.OpenAIController(os.getenv(constants.OPENAI_ENV_VAR), disable=disable)

		milvus.connect(alias=constants.ALIAS, host=constants.HOST, port=constants.PORT)
		self.milvus_access = milvus.TextEmbeddingTableController(
			name=constants.CONTEXTS_TABLE,
			primary_key=constants.CONTEXTS_PK,
			text_col=constants.CONTEXTS_TEXT_COL,
			embed_col=constants.CONTEXTS_EMBED_COL
		)
		self.milvus_access.load_collection()

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
		q_embeds = self.openai.access_model(openai_api.EMBEDDING, openai_api.EMBEDDING_MODELS[0], text=question)
		# get most similar contexts with Milvus controller
		most_similar_contexts: list[str] = self.milvus_access.get_similar_contexts(query_embeds=[q_embeds])
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


