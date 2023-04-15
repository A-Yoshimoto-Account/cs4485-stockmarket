import os
import subprocess
import time
import dotenv
from app import app

def main():
    dotenv.load_dotenv()
    cur = os.getcwd()
    path = os.path.join(cur,'milvus_db')
    path_two = os.path.join(cur,'brains\data_set_gathering')
    subprocess.check_call('python -m pip install -r requirements.txt"')
    subprocess.check_call('python -m pip install .')
    subprocess.check_call("docker compose up -d", cwd = path)
    print('Waiting 60 secs for Docker to warm up')
    time.sleep(60)
    subprocess.check_call(f"python {path_two}\gather_news.py")
    subprocess.check_call("python config_db.py", cwd = path)
    app.run()

if __name__ == '__main__': 
    main()