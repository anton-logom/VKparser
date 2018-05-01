# coding: utf8
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
    c.execute('TRUNCATE `parse_text`')
    c.execute('TRUNCATE `parse_links`')
    c.execute('TRUNCATE `parse_images`')
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
    conn.autocommit(True)
    c = conn.cursor()

    c.execute('SELECT max(`id`) FROM parse_text')
    lastdb = c.fetchone()[0]
    if not(lastdb):
        lastdb = 0
    list_put = list_put[lastdb+1:]

    list_put_images = []
    list_put_links = []
    for i in range(len(list_put)):
        crimg = list_put[i]['images'].split('\n')
        for cr in crimg:
            list_put_images.append([lastdb+1+i, cr])
        crlnk = list_put[i]['links'].split('\n')
        for cr in crlnk:
            list_put_links.append([lastdb+1+i, cr])


    try:
        c.executemany("""
        INSERT IGNORE INTO parse_text (`postid`, `author`, `text`) VALUES (%(id)s, %(author)s, %(text)s)
        """, list_put)
        kv1 = c.rowcount
        c.executemany("""
        INSERT INTO parse_images (`id`, `image`) VALUES (%s, %s)
        """, list_put_images)
        kv2 = c.rowcount
        c.executemany("""
        INSERT INTO parse_links (`id`, `link`) VALUES (%s, %s)
        """, list_put_links)
        kv3 = c.rowcount
        print("Содержимое добавленно в БД, добавлено: " + str(kv1) + "постов, " + str(kv2) + "изображений, " + str(kv3) + "ссылок.")
    except MySQLdb.DatabaseError:
        print('Проблема при записи в БД!')
    c.close()
    conn.close()
    print("Время работы составило: %s сек" % (time.time() - start_time))



