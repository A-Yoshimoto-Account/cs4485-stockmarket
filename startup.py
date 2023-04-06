'''
Steps for startup script:
Step 1: auto run (pip install -r requirements.txt)
Step 2: Verify that docker is running 
Step 3: Navigate to milvus_db dir
Step 4: run (docker compose up -d)
Step 5: Navigate back to main dir
Step 6: run gather news.py
Step 7: navigate to milvus_db dir
Step 8: run (python config_db.py)
Step 9: navigate back to main dir
Step 10: run (pip install .)
Step 11: run (flask run)
Step 12: Close'''
import os
import subprocess

def main():
    cur = os.getcwd()
    print(cur)
    path = os.path.join(cur,'milvus_db')
    print(path)
    test = subprocess.run(['python -m pip install -r requirements.txt"'])
    print(test)
    
    # os.system('dir')
    # # test = subprocess.call('dir', shell=True)
    # # print(test)


if __name__ == '__main__': 
    main()