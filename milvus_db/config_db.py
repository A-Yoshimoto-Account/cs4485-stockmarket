# this is a one time script to run in case the Milvus Docker volume has not been configured yet
# before running this script, make sure that the Milvus container is up and running through
# 	by docker compose and the official YAML file: https://github.com/milvus-io/milvus/releases/download/v2.2.3/milvus-standalone-docker-compose.yml
# instructions can be found here: https://milvus.io/docs/install_standalone-docker.md

from pymilvus import connections, Collection, CollectionSchema, FieldSchema
import configparser
import schemas
import pandas as pd

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

		print('Created table')
		print(collection)
		print()

def populate_table(table_name: str, text_df: pd.DataFrame, embed_df: pd.DataFrame):
	col = Collection(table_name)
	context_list = []
	embed_list = []

	for i, row in text_df.iterrows():
		context_list.append(row['context'])
		embed_list.append(embed_df.iloc[i].values)

	data = [context_list, embed_list]
	resp = col.insert(data)
	print('Inserted data')
	print(resp)
	print()

def main():
	connect_to_db()
	create_tables()
	text_df = pd.read_csv('initial_data/test_contexts.csv')
	embed_df = pd.read_csv('initial_data/test_embeds.csv')
	populate_table('context_embeddings', text_df, embed_df)
	disconnect_from_db()


if __name__ == '__main__':
	main()
