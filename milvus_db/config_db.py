# this is a one time script to run in case the Milvus Docker volume has not been configured yet
# before running this script, make sure that the Milvus container is up and running through
# 	by docker compose and the official YAML file: https://github.com/milvus-io/milvus/releases/download/v2.2.3/milvus-standalone-docker-compose.yml
# instructions can be found here: https://milvus.io/docs/install_standalone-docker.md

from pymilvus import connections, Collection, CollectionSchema, FieldSchema
import configparser
import schemas

config_file = 'db-connection.ini'
dbconn_configs = configparser.ConfigParser()
dbconn_configs.read(config_file)

def connect_to_db():
	connections.connect(
		alias=dbconn_configs['MILVUS-CONN']['alias'],
		host=dbconn_configs['MILVUS-CONN']['host'],
		port=int(dbconn_configs['MILVUS-CONN']['port']),
	)

def disconnect_from_db():
	# disconnect from the DB
	connections.disconnect(dbconn_configs['MILVUS-CONN']['alias'])

def create_tables():
	table_names = schemas.TABLE_NAMES
	table_schemas = schemas.TABLE_SCHEMAS

	for table_name in table_names:
		table = table_schemas[table_name]
		columns = table['columns']
		col_fields = table['fields']
		field_schemas = []
		for col in columns:
			field_schema = col_fields[col]
			field_schemas.append(FieldSchema(
				name=col,
				dtype=field_schema['dtype'],
				**field_schema['kwargs'],
			))
		using = table['using']
		shards_num = table['shards_num']
		pk = table['primary_key']
		desc = table['description']
		
		collection_schema = CollectionSchema(
			fields=field_schemas,
			description=desc
		)
		collection = Collection(
			name=table_name,
			schema=collection_schema,
			using=using,
			shards_num=shards_num,
		)
		
		if table['index']:
			index = table['index']
			index_field = index['field_name']
			index_params = index['index_params']
			collection.create_index(
				field_name=index_field,
				index_params=index_params
			)

	# # contexts table schema
	# context_id = FieldSchema(
		# name='context_id',
		# dtype=DataType.INT64,
		# is_primary=True,
		# auto_id=True
	# )
	# context_text = FieldSchema(
		# name='context_text',
		# dtype=DataType.VARCHAR,
		# max_length=6000
	# )
	# context_embeds = FieldSchema(
		# name='context_embeds',
		# dtype=DataType.FLOAT_VECTOR,
		# dim=1536
	# )

	# # create a table in the DB
	# collection_name = 'contexts'
	# schema = CollectionSchema(
		# fields=[context_id, context_text, context_embeds],
		# description='Context embeddings search'
	# )
	# collection = Collection(
		# name=collection_name,
		# schema=schema,
		# using='default',
	# )

	# # create index on embeddings field
	# index_params = {
		# 'metric_type': 'IP',
		# 'index_type': 'IVF_FLAT',
		# 'params': {'nlist': 1024}
	# }
	# collection.create_index(
		# field_name='context_embeds',
		# index_params=index_params
	# )

connect_to_db()
create_tables()
disconnect_from_db()