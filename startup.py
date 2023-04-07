import os
import subprocess

def main():
    cur = os.getcwd()
    path = os.path.join(cur,'milvus_db')
    subprocess.check_call('python -m pip install -r requirements.txt"')
    subprocess.check_call('python -m pip install .')
    subprocess.check_call("docker compose up -d", cwd = path)
    path_two = os.path.join(cur,'brains\data_set_gathering')
    subprocess.check_call(f"python {path_two}\gather_news.py")
    subprocess.check_call("python config_db.py", cwd = path)
    subprocess.Popen("flask run")

if __name__ == '__main__': 
    main()