import sqlite3
import json
import checksum
import time
import subprocess

# НАСТРОЙКИ
DBname = 'parser.db'    # Имя файла базы данных
Fname = 'posts.json'    # Имя временного файла


def load_from_json():
    with open(Fname, 'r', encoding='utf-8') as file:
        d = json.load(file)
    return d


def db_clear():
    conn = sqlite3.connect(DBname)
    c = conn.cursor()
    c.execute('DELETE FROM vk_news')
    conn.commit()
    conn.close()
    print('БД очищена.')


while __name__ == '__main__':
    print('ждем обновления json файла...')
    old_sha1 = checksum.get_sha1(Fname)
    new_sha1 = checksum.get_sha1(Fname)
    while old_sha1 == new_sha1:
        new_sha1 = checksum.get_sha1(Fname)
        time.sleep(1)

    list_put = load_from_json()
    print('json-файл обновлён, начинаем запись в БД...')
    db_clear()
    conn = sqlite3.connect(DBname)
    c = conn.cursor()
    try:
        start_time = time.time()
        c.executemany('INSERT INTO vk_news ("news-authors", "news-text", "news-links", "news-images") VALUES (:author, :text, :links, :images)', list_put)
        conn.commit()
        print("Содержимое добавленно в БД, строк добавлено: " + str(conn.total_changes))
        print("Время работы составило: %s сек" % (time.time() - start_time))
    except Exception:
        print('Проблема при записи в БД!')
    conn.close()


