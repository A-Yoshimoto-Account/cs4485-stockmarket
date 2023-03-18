import os
import constants
import brains.openai_api.openai_controller as openai_api
import brains.milvus_access.milvus_controller as milvus
from brains.openai_api.query_refiner import QueryRefiner

class ModelController:
	def __init__(self, disable: bool):
		self.openai = openai_api.OpenAIController(os.getenv(constants.OPENAI_ENV_VAR), disable=disable)
		self.milvus_access = milvus.TextEmbeddingTableController(
			name=constants.CONTEXTS_TABLE,
			primary_key=constants.CONTEXTS_PK,
			text_col=constants.CONTEXTS_TEXT_COL,
			embed_col=constants.CONTEXTS_EMBED_COL
		)
	
	def ask_question(self,
		answering_endpoint,
		answering_model,
		question,
		ksim=1,
		memory=[],
		refine=None,
	):
		# need to change:
		# 1. get embeds of question with OpenAIController
		# 2. get most sim contexts to questions with milvus_controller
		# 3, use OpenAIController to get answer with endpoint and model
		q_embeds = self.openai.access_model(openai_api.EMBEDDING, openai_api.EMBEDDING_MODELS[0], text=question)
		most_similar_contexts = self.milvus_access.get_similar_contexts(query_embeds=[q_embeds])
		if len(most_similar_contexts) > ksim:
			most_similar_contexts = most_similar_contexts[:ksim]
		if not refine:
			return self.openai.access_model(answering_endpoint, answering_model, question=question, ksim=most_similar_contexts[0], memory=memory)
		return QueryRefiner.query(self.openai, refine, answering_endpoint, answering_model, question, most_similar_contexts, memory)
