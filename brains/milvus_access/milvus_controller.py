from typing import List, Any

from pymilvus import connections, Collection, utility

def connect(alias, host, port):
	connections.connect(
		alias=alias,
		host=host,
		port=port
	)

def disconnect(alias):
	connections.disconnect(alias)

# note that Milvus does not update the physical disk immediately, and as a result,
#	when delete or insert operation are made, the num_entities attribute of Collection
#	may not immediately reflect the correct value.
# Milvus does, however, ensure that future accesses to deleted or inserted items are not erroneous
class _TableController:
	def __init__(self, name, primary_key):
		self.name: str = name
		self.primary_key = primary_key
		self.collection: Collection = None

	def _check_collection_loaded(func):
		def wrapper(self, *args, **kwargs):
			self.check_collection_loaded()
			func(self, *args, **kwargs)
		return wrapper

	def check_collection_loaded(self):
		if not self.collection:
			raise Exception('Please load the collection first before using it')

	def load_collection(self):
		self.collection = Collection(self.name)
		self.collection.load()

	@_check_collection_loaded
	def release_collection(self):
		self.collection.release()

	@_check_collection_loaded
	def drop_collection(self):
		self.release_collection()
		utility.drop_collection(self.name)

	@_check_collection_loaded
	def delete_all(self):
		pks = self.get_all_primary_keys()
		if pks:
			self.collection.delete(f'{self.primary_key} in {pks}')

	@_check_collection_loaded
	def get_all_primary_keys(self):
		results = self.collection.query(f'{self.primary_key} >= 0')
		return [res[self.primary_key] for res in results]

	_check_collection_loaded = staticmethod(_check_collection_loaded)

class TextEmbeddingTableController(_TableController):
	def __init__(self, name: str, primary_key: str, text_col: str, embed_col: str):
		super().__init__(name, primary_key)
		self.text_col = text_col
		self.embed_col = embed_col

	@_TableController._check_collection_loaded
	def insert(
			self,
			text_list: list,
			embedding_list: list
	):
		data = [text_list, embedding_list]
		resp = self.collection.insert(data)
		return resp

	@_TableController._check_collection_loaded
	def get_similar_contexts(
			self,
			query_embeds: list,
			nprobe: int = 16,
			limit: int = 15
	) -> list:
		search_params = {"metric_type": "IP", "params": {"nprobe": nprobe}, "offset": 0}
		res_ids = self.collection.search(
			data=query_embeds, 
			anns_field=self.embed_col,
			param=search_params,
			limit=limit,
			expr=None,
			consistency_level="Strong",
		)
		results = self.collection.query(
			expr=f"{self.primary_key} in {res_ids[0].ids}",
			offset=0,
			limit=limit,
			output_fields=[self.text_col],
			consistency_level="Strong"
		)
		resp: list[str] = [res[self.text_col] for res in results]
		print(resp)
		return resp

