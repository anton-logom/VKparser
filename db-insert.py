import sqlite3
import pickle
import time

# Настройки (потом уберем в отдельный файл с настройками)
DBname = 'parser.db'  # Имя файла базы данных
FileName = 'outfile'   # Имя временного файла


def open_parcelist_from_file():
    with open(FileName, 'rb') as file:
        return pickle.load(file)


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
    list_put = open_parcelist_from_file()
    # print(len(list_put))
    try:
        c.executemany('INSERT INTO vk_news ("news-text","news-links", "news-images") VALUES (?,?,?)', list_put)
        conn.commit()
        print('Содержимое добавленно в БД')
    except Exception:
            print('Проблема при записи в БД!')
    conn.close()

    print("Операции с базой данных завершены, время работы составило: %s сек" % (time.time() - start_time))




# c.execute('INSERT INTO vk_news ("id","news-text","news-images","news-links") VALUES ("' + str(i+1) + '", ""' + str(list_put[i][0]) + '"", ""' + str(list_put[i][1]) + '"", ""' + str(list_put[i][2]) + '"")')
