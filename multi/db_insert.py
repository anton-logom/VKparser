import sqlite3
import json
import checksum
import time

# НАСТРОЙКИ
DBname = 'parser.db'  # Имя файла базы данных
FileName = 'outfile'   # Имя временного файла
Fname = 'posts.json'


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


if __name__ == '__main__':
    db_clear()
    conn = sqlite3.connect(DBname)
    c = conn.cursor()

    old_sha1 = checksum.get_sha1(Fname)
    new_sha1 = checksum.get_sha1(Fname)
    while old_sha1 == new_sha1:
        new_sha1 = checksum.get_sha1(Fname)
        time.sleep(1)

    list_put = load_from_json()
    try:
        for i in range(len(list_put)):
            tek = list_put[str(i)]
            c.execute('INSERT INTO vk_news ("news-authors", "news-text", "news-links", "news-images") VALUES (?,?,?,?)',
                      (str(tek["author"]), str(tek["text"]), str(tek["links"]), str(tek["images"])))
            conn.commit()
        print('Содержимое добавленно в БД')
    except Exception:
        print('Проблема при записи в БД!')
    conn.close()
