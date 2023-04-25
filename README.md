# cs4485-stockmarket 📈
**NOTE: Do NOT hardcode any API keys and push them to this repository**

Group repository for UTD SP23 CS 4485 Project: What's Moving the Stock Market Today? (CS-Stock-T1)

---
An installation manual can be found in the `docs/` directory. It will detail the prerequisites, steps to install, and how to use the program.


If running the app without the startup script, you must first setup the Docker container for the Milvus vector database.
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

---
This system uses the OpenAI API, News API, a Selenium web scraper, and Milvus Vector Database to answer questions about the stock market.

Currently, it's scope is limited to questions about Nvidia, AMD, Intel, Qualcomm, Micron Technologies, ARM, and the semiconductor industry.

Please note that this system requires OpenAI and NewsAPI keys tied to the user. Please use at your own discretion.
