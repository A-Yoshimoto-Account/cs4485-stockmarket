import os
import subprocess
import time

SLEEP = 15

def main():
    cur = os.getcwd()
    path = os.path.join(cur,'milvus_db')
    path_two = os.path.join(cur,'brains/data_set_gathering')
    subprocess.check_call(['python', '-m', 'pip', 'install', '-r', 'requirements.txt'])
    import dotenv
    dotenv.load_dotenv()
    subprocess.check_call(['python', '-m', 'pip', 'install', '.'])
    subprocess.check_call(['docker', 'compose', 'up', '-d'], cwd = path)
    print(f'Waiting {SLEEP} secs for Docker to warm up')
    time.sleep(SLEEP)
    subprocess.check_call(['python', f'{path_two}/gather_news.py'])
    subprocess.check_call(['python', 'config_db.py'], cwd = path)
    subprocess.run(['flask', 'run'])
if __name__ == '__main__': 
    main()
