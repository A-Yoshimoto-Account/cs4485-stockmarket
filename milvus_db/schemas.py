from pymilvus import DataType

TABLE_NAMES = [
	'context_embeddings',
	'question_embeddings',
]

TABLE_SCHEMAS = {
	'context_embeddings': {
		'columns': ['context_id', 'context_text', 'context_embeddings'],
		'using': 'default',
		'shards_num': 2,
		'primary_key': 'context_id',
		'description': 'context texts and embeddings',
		'fields': {
			'context_id': {
				'dtype': DataType.INT64,
				'kwargs': {
					'is_primary': True,
					'auto_id': True,
				},
			},
			'context_text': {
				'dtype': DataType.VARCHAR,
				'kwargs': {
					'max_length': 8192,
				},
			},
			'context_embeddings': {
				'dtype': DataType.FLOAT_VECTOR,
				'kwargs': {
					'dim': 1536,
				},
			},
		},
		'index': {
			'field_name': 'context_embeddings',
			'index_params': {
				'metric_type': 'IP',
				'index_type': 'IVF_FLAT',
				'params': {'nlist': 1024},
			},
		},
	},
	'question_embeddings': {
		'columns': ['question_id', 'question_text', 'question_embeddings'],
		'using': 'default',
		'shards_num': 2,
		'primary_key': 'question_id',
		'description': 'common question text and embeddings',
		'fields': {
			'question_id': {
				'dtype': DataType.INT64,
				'kwargs': {
					'is_primary': True,
					'auto_id': True,
				},
			},
			'question_text': {
				'dtype': DataType.VARCHAR,
				'kwargs': {
					'max_length': 512,
				},
			},
			'question_embeddings': {
				'dtype': DataType.FLOAT_VECTOR,
				'kwargs': {
					'dim': 1536,
				},
			},
		},
		'index': {
			'field_name': 'question_embeddings',
			'index_params': {
				'metric_type': 'IP',
				'index_type': 'IVF_FLAT',
				'params': {'nlist': 1024},
			},
		},
	},
}
