from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time, requests, threading, pickle, os
from bs4 import BeautifulSoup
import subprocess
from py_linq import Enumerable
import json

# НАСТРОЙКИ
count = 10
options = webdriver.ChromeOptions()
login = ""  # логин аккаунта вк (требуется только если авторизация в браузере не выполнена)
password = ""  # пароль аккаунта вк (требуется только если авторизация в браузере не выполнена)

# Windows
# save_images_path = ".\downloads\img"  # директория для сохранения картинок и префикс имени файлов картинок
# chrome_driver_path = ".\chromedriver.exe"  # путь до драйвера Chrome
# profile_dir = r"C:\Users\Antoshka\AppData\Local\Google\Chrome\User Data"  # Директория кэша Chrome
# options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))

# MacOS
save_images_path = "/Users/r3m1x/OSimg/"
chrome_driver_path = "/Users/r3m1x/ChromeDriver/chromedriver"
chrome_cache_path = "--user-data-dir=/Users/r3m1x/ChromeDriver/caсhe/"
options.add_argument(chrome_cache_path)


def avtorization(login, password, driver):
    check = 0
    try:
        driver.find_element_by_class_name("post")
        check = 1
    except NoSuchElementException:
        print("Авторизация отсутствует. Подставляем логин и пароль из настроек...")
        driver.get('https://vk.com/id1')
        time.sleep(0.5)
        elem = driver.find_element_by_name('email')
        elem.send_keys(login)
        elem = driver.find_element_by_name('pass')
        elem.send_keys(password)
        elem.send_keys(Keys.RETURN)
        time.sleep(0.5)
        driver.get('https://vk.com/feed')
        try:
            driver.find_element_by_class_name("post")
            check = 1
        except NoSuchElementException:
            pass
    if check:
        print("Авторизовались успешно")
        return 1
    else:
        print("Авторизация не удалась")
        return 0


def parce_authors(posts, final):
    print("Начало парсинга авторов.")
    start_time = time.time()
    my_collection = Enumerable(posts)
    authors = my_collection.select_many(lambda x: x.find("a", {"class": "author"}))
    authors = authors.to_list()
    insert_to_list("authors", authors, final)
    print("Парсинг авторов завершен.")
    print("Время парсинга авторов составило: %s сек" % (time.time() - start_time))


def search_text(post):
    try:
        post_text = post.find("div", {"class" : "wall_post_text"})
        text = post_text.text
    except Exception:
        text = "Текст отсутсвует."
    return text


def parce_text(posts, final):
    print("Начало парсинга текста.")
    start_time = time.time()
    my_collection = Enumerable(posts)
    wall_text = my_collection.select(lambda x: search_text(x))
    wall_text=wall_text.to_list()
    insert_to_list("text", wall_text, final)
    print("Парсинг текста завершен.")
    print("Время парсинга текста составило: %s сек" % (time.time() - start_time))


def search_links(post):
    post_links = post.find_all('a', {"target": "_blank"})
    if len(post_links) > 0:
        post_links_collection = Enumerable(post_links)
        links = post_links_collection.select(lambda x: 'https://vk.com'+x.attrs["href"])
        links = links.to_list()
        return links
    else:
        return ["Ссылки отсутсвуют."]


def parce_links(posts, final):
    print("Начало парсинга ссылок.")
    start_time = time.time()
    my_collection = Enumerable(posts)
    links = my_collection.select(lambda x: search_links(x))
    links = links.to_list()
    insert_to_list("links", links, final)
    print("Парсинг ссылок завершен.")
    print("Время парсинга ссылок составило: %s сек" % (time.time() - start_time))


def save_image(style):
    if not(style == None) and not(style == False):  # Пиздец говнокод конечно
        image_path = style[style.find('url') + 4:len(style) - 2]
        resource = requests.get(image_path)
        out_image_path = save_images_path + image_path[image_path.rfind('/') + 1:len(image_path)]
        out_image = open(out_image_path, 'wb')
        out_image.write(resource.content)
        out_image.close()
        time.sleep(0.05)
        return [image_path, out_image_path]
    else:
        return ["Содержится видео, пропущено"]


def search_images(post):
    post_images = post.find_all('a', {"class": "image_cover"})
    if len(post_images) > 0:
        post_images_collection = Enumerable(post_images)
        images = post_images_collection.select(lambda x: not x.has_attr('data-video') and x.attrs["style"])
        images = images.to_list()
        if len(images) > 0:
            images = Enumerable(images)
            try:
                images = images.select(lambda x: save_image(x))
                images = images.to_list()
                return images
            except Exception:
                print("ошибка при обработке изображений")
    else:
        return ["Изображения отсутсвуют."]


def parce_images(posts, final):
    print("Начало парсинга изображений.")
    start_time = time.time()
    my_collection = Enumerable(posts)
    images = my_collection.select(lambda x: search_images(x))
    images = images.to_list()
    insert_to_list("images", images, final)
    print("Парсинг изображений завершен.")
    print("Время парсинга изображений составило: %s сек" % (time.time() - start_time))


def insert_to_list(data_type, data, final):
    if data_type == "authors":
        final[0] = data
    if data_type == "text":
        final[1] = data
    if data_type == "links":
        final[2] = data
    if data_type == "images":
        final[3] = data


def print_posts(list):
    print("Вывод данных")
    print("=================")
    for i in range(len(list[0])):
        print("Пост №" + str(i))
        print("Автор:")
        print(list[0][i], end='\n')
        print("Текст:")
        print(list[1][i], end='\n')
        print("Внешние ссылки:")
        for lnk in list[2][i]:
                print(lnk, end='\n')
        print("Изображения:")
        for img in list[3][i]:
                print(img, end='\n')
        print('---------------')


class MyThread(threading.Thread):
    def __init__(self, name, posts, list):
        threading.Thread.__init__(self)
        self.name = name
        self.posts = posts
        self.list = list

    def run(self):
        if self.name == "authors":
            parce_authors(self.posts, self.list)
        if self.name == "text":
            parce_text(self.posts, self.list)
        if self.name == "links":
            parce_links(self.posts, self.list)
        if self.name == "images":
            parce_images(self.posts, self.list)


def parce_main(final):
    # count = int(input("Введите кол-во новостей для парсинга: "))

    driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    print('Ждем загрузки страницы...')
    driver.get("https://vk.com/feed")
    time.sleep(0.2)
    if avtorization(login, password, driver):
        print('Начинаем копирование из браузера, будет обработано ' + str(count) + ' постов...')
        # Пролистывание страницы
        while len(driver.find_elements_by_class_name("post")) < count:
            driver.execute_script("scroll(0,1000000)")

        # Прогрузка страницы
        # while driver.find_elements_by_xpath("//div[@class='_post_content']").__len__() < count:
        #     driver.execute_script("feed.showMore();")

        html_source = driver.page_source
        print("Копирование завершено.")
        driver.close()
        print("Драйвер брузера закрыт.")

        soup = BeautifulSoup(html_source, "html.parser")
        all_posts = soup.find_all('div', {"class": "post"})

        all_threads = []
        for i in ["authors", "text", "links", "images"]:
            my_thread = MyThread(i, all_posts, final)
            my_thread.start()
            all_threads.append(my_thread)

        while len(threading.enumerate()) > 1:
            time.sleep(0.1)
            pass


def save_parcelist_to_file(lst):
    with open('outfile', 'wb') as file:
        pickle.dump(lst, file)


def open_parcelist_from_file():
    with open('outfile', 'rb') as file:
        return pickle.load(file)


def save_to_json(posts):
    for i in range(len(posts)):
        with open('posts.json',
                  'w') as file:
            json.dump(posts, file, indent=2, ensure_ascii=False)


def load_from_json():
    with open('posts.json','r') as file:
        d = json.load(file)
    return d


if __name__ == '__main__':
    print('Запуск...')
    start_time = time.time()

    final_list = ['-', '-', '-', '-']

    parce_main(final_list)

    # save_parcelist_to_file(final_list)
    # final_list = open_parcelist_from_file()

    print_posts(final_list)
    for j in range(len(final_list)):
        final_list[j] = {i: final_list[j][i] for i in range(len(final_list[j]))}
    dict = {i: final_list[i] for i in range(len(final_list))}
    save_to_json(dict)
    load_dict = load_from_json()
    print(load_dict)

    print("Парсинг завершен, время работы составило: %s сек" % (time.time() - start_time))

    #print(subprocess.call('python .\db-insert.py', shell=True))











