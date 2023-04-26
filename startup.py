import os
import subprocess
import time

"""
This script will setup the system and start the system.
It will:
- install the requirements and the system into the local Python environment
- start the Docker container for Milvus vector database
- get the news articles for today
- insert the news articles into the Milvus vector database instance
- start the Flask app 
"""

SLEEP = 15  # the seconds to sleep after starting the Docker containers


def main():
    cur = os.getcwd()
    path = os.path.join(cur,'milvus_db')
    path_two = os.path.join(cur,'brains/data_set_gathering')
    # install the requirements
    subprocess.check_call(['python', '-m', 'pip', 'install', '-r', 'requirements.txt'])
    import dotenv
    # load the API keys as environment variables
    dotenv.load_dotenv()
    # install the system
    subprocess.check_call(['python', '-m', 'pip', 'install', '.'])
    # start the Docker containers and wait
    subprocess.check_call(['docker', 'compose', 'up', '-d'], cwd = path)
    print(f'Waiting {SLEEP} secs for Docker to warm up')
    time.sleep(SLEEP)
    # gather the news for today and populate the database
    subprocess.check_call(['python', f'{path_two}/gather_news.py'])
    subprocess.check_call(['python', 'config_db.py'], cwd = path)
    # start the Flask app
    subprocess.run(['flask', 'run'])


if __name__ == '__main__': 
    main()
