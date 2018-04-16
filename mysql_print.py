import MySQLdb

# НАСТРОЙКИ
import mysql_config


def print_posts(lst):
    for i in range(0, len(lst)):
        print("Пост №" + str(i + 1))
        print("ID поста:" + lst[i][1], end='\n')
        print("Автор и текст:")
        print(lst[i][2], end='\n')
        print(lst[i][3], end='\n')
        if len(lst[i][5]) > 1:
            print("Изображения:")
            print(lst[i][5], end='\n')
        if len(lst[i][4]) > 1:
            print("Внешние ссылки:")
            print(lst[i][4], end='\n')
        print('---------------')


if __name__ == '__main__':
    print("Вывод из базы данных...")
    conn = MySQLdb.connect(host=mysql_config.Host,
                           port=mysql_config.Port,
                           user=mysql_config.username,
                           passwd=mysql_config.password,
                           charset="utf8",
                           db=mysql_config.db)
    c = conn.cursor()
    c.execute('SELECT * FROM `parse`')
    c_list = c.fetchall()
    conn.close()
    print_posts(c_list)
