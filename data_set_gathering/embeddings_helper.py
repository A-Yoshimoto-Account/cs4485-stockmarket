import pandas as pd
import numpy as np

COL_CONTEXT = 'context'
COL_QUESTION = 'questions'
COL_ANSWER = 'answers'

'''
File for searching the embeddings knowledge basestring

Note that currently, we have no dedicated system for looking up embeddings-context pairings
The system in place is using 2 CSVs to store contexts and their embeddings

A future idea is to use a vector database (Milvus?) for dedicated storage
'''

def get_related_contexts(original_index, contexts, embeddings, n, reverse=False):
	original_embeds = embeddings.iloc[original_index]
	sim_scores = embeddings.apply(lambda row: vector_sim(original_embeds, row), axis=1)
	sim_indexes = sim_scores.sort_values(ascending=reverse).head(n + 0 if reverse else 1).iloc[1:].index.values
	return [contexts.iloc[i][COL_CONTEXT] for i in sim_indexes]

def vector_sim(x, y):
	return np.dot(np.array(x), np.array(y))