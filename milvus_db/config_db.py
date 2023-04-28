from pymilvus import connections, Collection, CollectionSchema, FieldSchema, utility
import configparser
import schemas
import pandas as pd
from datetime import datetime
import os

"""
This is a script that will create the collections in the
    Milvus vector database instance and populate the database.
"""

config_file = 'db-connection.ini'  # file with connection configurations
url_file = 'insertedurls.csv'  # CSV recording inserted article URLs
# reads config_file contents
dbconn_configs = configparser.ConfigParser()
dbconn_configs.read(config_file)


def connect_to_db():
    """
    Connects to the database according to the configuration file
    """
    connections.connect(
        alias=dbconn_configs['MILVUS-CONN']['alias'],
        host=dbconn_configs['MILVUS-CONN']['host'],
        port=int(dbconn_configs['MILVUS-CONN']['port']),
    )


def disconnect_from_db():
    """
    Disconnects from the database
    """
    connections.disconnect(dbconn_configs['MILVUS-CONN']['alias'])


def create_tables():
    """
    Creates the tables according to the schemas.py file
    This will skip tables already created in the database.
    Terminal output will be printed notifying of any skipped creations and
        created tables.
    """
    table_names = schemas.TABLE_NAMES
    table_schemas = schemas.TABLE_SCHEMAS
    # iterate through the tables
    for table_name in table_names:
        print(f'Creating collection {table_name}')
        # skips existing tables
        if utility.has_collection(table_name):
            print(f'Found existing collection {table_name}, skipping it\'s creation.')
            continue
        # if table creation is being done, the last updated date is reset
        else:
            dbconn_configs['MILVUS-CONN']['updated'] = ''
        # obtain table columns
        table = table_schemas[table_name]
        columns = table['columns']
        col_fields = table['fields']
        field_schemas = []
        # create the column schemas
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
        # creates the table schema
        collection_schema = CollectionSchema(
            fields=field_schemas,
            description=desc
        )
        # creates the table
        collection = Collection(
            name=table_name,
            schema=collection_schema,
            using=using,
            shards_num=shards_num,
        )
        # Releasing the collection (if it exists) before creating a new one
        # this would resolve an error attempting to load an updated database to Milvus
        collection.release()
        if table['index']:
            index = table['index']
            index_field = index['field_name']
            index_params = index['index_params']
            collection.create_index(
                field_name=index_field,
                index_params=index_params
            )
        # report the created table
        print('Created table')
        print(collection)
        print()


def populate_table(table_name: str, text_df: pd.DataFrame, embed_df: pd.DataFrame):
    """
    Populates teh given table with the given text and embeddings.
    This will be skipped if the database has already been updated for the day.
    @param table_name: the table to populate
    @param text_df: a DataFrame containing the text to insert
    @param embed_df: a DataFrame containing the embedding vectors to insert
    """
    # skip operation if database already updated for today
    if ('updated' in dbconn_configs['MILVUS-CONN']) and \
            (dbconn_configs['MILVUS-CONN']['updated'] == datetime.today().strftime('%m-%d-%Y')):
        print('Database already has been updated for today')
        return
    # get to table to insert into
    col = Collection(table_name)
    context_list = []
    embed_list = []
    # url_df will track which URLs are already inserted into the database
    url_df = pd.DataFrame(columns=['URL'])
    if os.path.isfile(url_file):
        url_df = pd.read_csv(url_file)
    inserted = 0
    skipped = 0
    # iterate through each text, embedding pair and insert them into the lists
    for i, row in text_df.iterrows():
        if row['URL'] in url_df['URL'].values:
            skipped += 1
            continue
        context_list.append(row['context'])
        embed_list.append(embed_df.iloc[i].values)
        inserted += 1
        url_df = pd.concat([url_df, pd.DataFrame([[row['URL']]], columns=['URL'])], ignore_index=True)
    # insert into the database
    if context_list:
        data = [context_list, embed_list]
        resp = col.insert(data)
        url_df.to_csv(url_file, index=False)
        print('Inserted data')
        print(resp)
        print()

    print(f'Inserted {inserted} new articles, skipped {skipped} duplicate articles')

    # record the date to track when the database has been last updated
    dbconn_configs['MILVUS-CONN']['updated'] = datetime.today().strftime('%m-%d-%Y')
    with open('db-connection.ini', 'w') as file:
        dbconn_configs.write(file)


def create_file_path(
        file_type: str
):
    """
    @param file_type: the type of file to create the file path for
    @return: the file path to today's created files
    """
    today = datetime.today().strftime('%m-%d-%Y')
    directory = 'initial_data/'
    file_name = f'{file_type}_{today}.csv'
    return os.path.join(directory, file_name)


def main():
    """
    This script will:
    - create the database tables if not already created
    - populate the database tables if not already done for today
    """
    connect_to_db()
    create_tables()
    text_df = pd.read_csv(create_file_path('context'))
    embed_df = pd.read_csv(create_file_path('embeds'))
    populate_table('context_embeddings', text_df, embed_df)
    disconnect_from_db()


if __name__ == '__main__':
    main()
