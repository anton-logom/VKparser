import MySQLdb
import json
import checksum
import time

# НАСТРОЙКИ
import mysql_config
Fname = 'posts.json'    # Имя JSON файла
clear = 0               # очистка БД при запуске программы 0 = не очищать, 1 = очищать


def load_from_json():
    with open(Fname, 'r', encoding='utf-8') as file:
        d = json.load(file)
    return d


def db_clear():
    conn = MySQLdb.connect(host=mysql_config.Host,
                           port=mysql_config.Port,
                           user=mysql_config.username,
                           passwd=mysql_config.password,
                           charset="utf8",
                           db=mysql_config.db)
    c = conn.cursor()
    c.execute('TRUNCATE `parse`')
    conn.commit()
    c.close()
    conn.close()
    print('БД очищена.')


while __name__ == '__main__':
    if clear:
        db_clear()
    print('Ждем обновления json файла...')
    old_sha1 = checksum.get_sha1(Fname)
    new_sha1 = checksum.get_sha1(Fname)
    while old_sha1 == new_sha1:
        new_sha1 = checksum.get_sha1(Fname)
        time.sleep(1)

    list_put = load_from_json()
    print('json-файл обновлён, начинаем запись в БД...')
    start_time = time.time()
    conn = MySQLdb.connect(host=mysql_config.Host,
                           port=mysql_config.Port,
                           user=mysql_config.username,
                           passwd=mysql_config.password,
                           charset="utf8",
                           db=mysql_config.db)
    c = conn.cursor()

    try:
        c.executemany("""
        INSERT IGNORE INTO parse (`news-id`, `news-authors`, `news-text`, `news-links`, `news-images`) VALUES (%(id)s, %(author)s, %(text)s, %(links)s, %(images)s)
        """, list_put)
        conn.commit()
        print("Содержимое добавленно в БД, строк добавлено: " + str(c.rowcount))
    except MySQLdb.DatabaseError:
        print('Проблема при записи в БД!')

    conn.commit()
    c.close()
    conn.close()
    print("Время работы составило: %s сек" % (time.time() - start_time))



