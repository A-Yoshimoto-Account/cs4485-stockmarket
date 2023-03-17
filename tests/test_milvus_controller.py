from pymilvus import Collection, utility
from brains.milvus_access.milvus_controller import TextEmbeddingTableController, connect, disconnect
import pandas as pd
import pytest

@pytest.fixture(autouse=True)
def connect_and_disconnect(tmpdir):
	connect('default', 'localhost', 19530)
	yield
	disconnect('default')

def test_unloaded_collection_exception():
	context_table = TextEmbeddingTableController('context_embeddings', 'context_id', 'context_text', 'context_embeddings')
	with pytest.raises(Exception):
		context_table.drop_collection()

# def test_get_all():
# 	context_table = TextEmbeddingTableController('context_embeddings', 'context_id', 'context_text', 'context_embeddings')
# 	context_table.load_collection()
# 	context_table.release_collection()
# 	context_table.collection.flush()
# 	context_table.load_collection()
# 	entity_count = context_table.collection.num_entities
# 	res = context_table.get_all_primary_keys()
# 	context_table.release_collection()
# 	if not res:
# 		res = []
# 	assert entity_count == len(res)
#
# def test_delete_all():
# 	context_table = TextEmbeddingTableController('context_embeddings', 'context_id', 'context_text', 'context_embeddings')
# 	context_table.load_collection()
# 	context_table.delete_all()
# 	context_table.release_collection()
# 	context_table.collection.flush()
# 	assert context_table.collection.num_entities == 0
#
# def test_insert():
# 	context_table = TextEmbeddingTableController('context_embeddings', 'context_id', 'context_text', 'context_embeddings')
# 	context_table.load_collection()
# 	before = context_table.collection.num_entities
# 	text_df = pd.read_csv('test_files/test_contexts.csv')
# 	embeds_df = pd.read_csv('test_files/test_embeds.csv')
# 	text = text_df.iloc[0].values.tolist()
# 	embeds = [embeds_df.iloc[0].values.tolist()]
# 	context_table.insert(text, embeds)
# 	context_table.release_collection()
# 	context_table.collection.flush()
#
# 	assert context_table.collection.num_entities == before + 1
#
# def test_similarity_search():
# 	context_table = TextEmbeddingTableController('context_embeddings', 'context_id', 'context_text', 'context_embeddings')
# 	context_table.load_collection()
# 	text_df = pd.read_csv('test_files/test_contexts.csv')
# 	embeds_df = pd.read_csv('test_files/test_embeds.csv')
# 	text = text_df.iloc[0].values.tolist()
# 	embeds = [embeds_df.iloc[0].values.tolist()]
# 	context_table.insert(text, embeds)
# 	context_table.insert(text, embeds)
# 	context_table.release_collection()
# 	context_table.collection.flush()
#
# 	context_table.load_collection()
# 	res = context_table.get_similar_contexts(embeds)
# 	context_table.release_collection()
#
# 	assert text == res['context_text']