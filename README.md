# cs4485-stockmarket
**NOTE: Do NOT hardcode any API keys and push them to this repository**

Group repository for UTD SP23 CS 4485 Project: What's Moving the Stock Market Today?

---
To run the Flask app, have Python and pip downloaded and run the below commands in order:
```
pip install -r requirements.txt
pip install .
flask run
```
The Flask app will be available on http://localhost:5000


The Flask app is a single file module. The packages in this project include code that:
- accesses articles from the web with News API and web scraping
- uses a Docker container of the Milvus vector database to store and access text and text embeddings
- uses the OpenAI Python API to access GPT models
