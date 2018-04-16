import subprocess

if __name__ == '__main__':
    subprocess.run('start "db_control" python mysql_insert.py & start "parcer" python parceWithSoup_linq_multi.py', shell=True)
