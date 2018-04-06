import subprocess

if __name__ == '__main__':
    subprocess.run('python3 parceWithSoup_linq_multi.py & python3 db_insert.py', shell=True)