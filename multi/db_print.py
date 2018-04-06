import sqlite3

# НАСТРОЙКИ
DBname = 'parser.db'  # Имя файла базы данных


def print_posts(lst):
    for i in range(0, len(lst)):
        print("Пост №" + str(i+1))
        print("Автор и текст:")
        print(lst[i][0], end='\n')
        print(lst[i][1], end='\n')
        if len(lst[i][2]) > 1:
            print("Изображения:")
            print(lst[i][2], end='\n')
        if len(lst[i][2]) > 1:
            print("Внешние ссылки:")
            print(lst[i][3], end='\n')
        print('---------------')


if __name__ == '__main__':
    print("Вывод из базы данных...")
    conn = sqlite3.connect(DBname)
    c = conn.cursor()
    c.execute('SELECT * FROM vk_news')
    c_list = c.fetchall()
    conn.close()
    print_posts(c_list)
