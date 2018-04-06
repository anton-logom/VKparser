import subprocess

if __name__ == '__main__':
    subprocess.run('start "parcer" python parceWithSoup_linq_multi.py MAX & start "db_control" python db_insert.py', shell=True)
