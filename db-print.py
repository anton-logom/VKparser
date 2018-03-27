import sqlite3
import time

# Настройки (потом уберем в отдельный файл с настройками)
DBname = 'parser.db'  # Имя файла базы данных


def print_posts(list):
    for i in range(0, len(list)):
        print("Пост №" + str(i+1))
        print("Автор и текст:")
        print(list[i][0], end='\n')
        print(list[i][1], end='\n')
        if len(list[i][2]) > 1:
            print("Изображения:")
            print(list[i][2], end='\n')
        if len(list[i][2]) > 1:
            print("Внешние ссылки:")
            print(list[i][3], end='\n')
        print('---------------')

if __name__ == '__main__':
    print("Начинаем вывод из базы данных...")
    start_time = time.time()
    conn = sqlite3.connect(DBname)
    c = conn.cursor()
    c.execute('SELECT * FROM vk_news')
    c_list = c.fetchall()
    conn.close()
    print_posts(c_list)

    print("Вывод из базы данных завершен, время работы составило: %s сек" % (time.time() - start_time))