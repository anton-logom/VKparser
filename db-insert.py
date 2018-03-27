import sqlite3
import json
import time

# Настройки (потом уберем в отдельный файл с настройками)
DBname = 'parser.db'  # Имя файла базы данных
FileName = 'outfile'   # Имя временного файла


# def open_parcelist_from_file():
#     with open(FileName, 'rb') as file:
#         return pickle.load(file)

def load_from_json():
    with open('posts.json', 'r', encoding='utf-8') as file:
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
    print("Начинаем операции с базой данных...")
    start_time = time.time()
    db_clear()
    conn = sqlite3.connect(DBname)
    c = conn.cursor()
    list_put = load_from_json()

    try:
        for i in range(len(list_put)):
            tek = list_put[str(i)]
            c.execute('INSERT INTO vk_news ("news-author", "news-text", "news-links", "news-images") VALUES (?,?,?,?)', (str(tek["author"]), str(tek["text"]), str(tek["links"]), str(tek["images"])))
            conn.commit()
        print('Содержимое добавленно в БД')
    except Exception:
        print('Проблема при записи в БД!')
    conn.close()

    print("Операции с базой данных завершены, время работы составило: %s сек" % (time.time() - start_time))
