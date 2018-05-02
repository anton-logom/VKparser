# coding: utf8

import MySQLdb

# НАСТРОЙКИ
import mysql_config


def print_posts(lst):
    print(lst)
    lastpost = 0
    for i in range(0, len(lst)):
        if not(lastpost == lst[i][0]):
            print('---------------')
            print("Пост №" + str(lst[i][0]))
            print("ID поста:" + lst[i][1], end='\n')
            print("Автор и текст:")
            print(lst[i][2], end='\n')
            print(lst[i][3], end='\n')
        lastpost = lst[i][0]
        if (len(lst[i][5]) > 1) & (not(lst[i][5] == 'Изображения отсутсвуют.')):
            print("Изображение:")
            print(lst[i][5], end='\n')
        if (len(lst[i][7]) > 1) & (not(lst[i][7] == 'Ссылки отсутсвуют.')):
            print("Внешняя ссылка:")
            print(lst[i][7], end='\n')


if __name__ == '__main__':
    print("Вывод из базы данных...")
    conn = MySQLdb.connect(host=mysql_config.Host,
                           port=mysql_config.Port,
                           user=mysql_config.username,
                           passwd=mysql_config.password,
                           charset="utf8",
                           db=mysql_config.db)
    c = conn.cursor()
    c.execute('SELECT * FROM parse_text JOIN parse_images ON (parse_text.id = parse_images.id) JOIN parse_links ON (parse_text.id = parse_links.id)')
    c_list = c.fetchall()
    conn.close()
    print_posts(c_list)
    input()
