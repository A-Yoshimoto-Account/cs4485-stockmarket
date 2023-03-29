# cs4485-stockmarket 📈
**NOTE: Do NOT hardcode any API keys and push them to this repository**

Group repository for UTD SP23 CS 4485 Project: What's Moving the Stock Market Today?

---
Before running the app, you must first setup the Docker container for the Milvus vector database.
In the `milvus_db` directory, run the below commands:
```
docker compose up -d
python config_db.py
```
The above will initialize the container volumes, and then run the setup required to create the tables.

To run the Flask app, have Python and pip downloaded and run the below commands in order:
```
pip install -r requirements.txt
pip install .
flask run
```
The Flask app will be available on http://localhost:5000

After running `pip install -r requirements.txt`, you can also run the app by running:
```
./run.sh
```
Be sure execution permissions are set.

The Flask app is a single file module. The packages in this project include code that:
- accesses articles from the web with News API and web scraping
- uses a Docker container of the Milvus vector database to store and access text and text embeddings
- uses the OpenAI Python API to access GPT models

Please have environment variables or a .env for OPENAI_API_KEY and NEWS_API_KEY