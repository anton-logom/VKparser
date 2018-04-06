from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time, requests, threading, pickle, os, multiprocessing, json
from bs4 import BeautifulSoup
from py_linq import Enumerable


options = webdriver.ChromeOptions()

# НАСТРОЙКИ
count = 100
login = ""  # логин аккаунта вк (требуется только если авторизация в браузере не выполнена)
password = ""  # пароль аккаунта вк (требуется только если авторизация в браузере не выполнена)

# Windows
save_images_path = ".\downloads\img"  # директория для сохранения картинок и префикс имени файлов картинок
chrome_driver_path = ".\chromedriver.exe"  # путь до драйвера Chrome
profile_dir = r"C:\Users\Antoshka\AppData\Local\Google\Chrome\User Data"  # Директория кэша Chrome
options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))

# # MacOS
# save_images_path = "/Users/r3m1x/OSimg/"
# chrome_driver_path = "/Users/r3m1x/ChromeDriver/chromedriver"
# chrome_cache_path = "--user-data-dir=/Users/r3m1x/ChromeDriver/caсhe/"
# options.add_argument(chrome_cache_path)


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
    my_collection = Enumerable(posts)
    authors = my_collection.select_many(lambda x: x.find("a", {"class": "author"}))
    authors = authors.to_list()
    insert_to_list("authors", authors, final)


def search_text(post):
    try:
        post_text = post.find("div", {"class" : "wall_post_text"})
        text = post_text.text
    except Exception:
        text = "Текст отсутсвует."
    return text


def parce_text(posts, final):
    my_collection = Enumerable(posts)
    wall_text = my_collection.select(lambda x: search_text(x))
    wall_text=wall_text.to_list()
    insert_to_list("text", wall_text, final)


def search_links(post):
    post_links = post.find_all('a', {"target": "_blank"})
    if len(post_links) > 0:
        post_links_collection = Enumerable(post_links)
        links = post_links_collection.select(lambda x: 'https://vk.com'+x.attrs["href"])
        links = links.to_list()
        links = sorted(set(links))
        return links
    else:
        return ["Ссылки отсутсвуют."]


def parce_links(posts, final):
    my_collection = Enumerable(posts)
    links = my_collection.select(lambda x: search_links(x))
    links = links.to_list()
    insert_to_list("links", links, final)


def save_image(style):
    if not(style == None) and not(style == False):  # Пиздец говнокод конечно
        image_path = style[style.find('url') + 4:len(style) - 2]
        resource = requests.get(image_path)
        out_image_path = save_images_path + image_path[image_path.rfind('/') + 1:len(image_path)]
        out_image = open(out_image_path, 'wb')
        out_image.write(resource.content)
        out_image.close()
        time.sleep(0.05)
        #return [image_path, out_image_path]
        return out_image_path
    else:
        return "Содержится видео, пропущено"


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
                return ["Ошибка"]
    else:
        return ["Изображения отсутсвуют."]


def parce_images(posts, final):
    my_collection = Enumerable(posts)
    images = my_collection.select(lambda x: search_images(x))
    images = images.to_list()
    insert_to_list("images", images, final)


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


def save_to_json(final_list):
    posts = {}
    for j in range(len(final_list[0])):
        posts[j] = {
            'author': final_list[0][j],
            'text': final_list[1][j],
            'links': str(final_list[2][j]),
            'images': str(final_list[3][j])
        }

    for i in range(len(posts)):
        with open('posts.json', 'w', encoding='utf-8') as file:
            json.dump(posts, file, indent=2, ensure_ascii=False)


def load_from_json():
    with open('posts.json', 'r', encoding='utf-8') as file:
        d = json.load(file)
    return d


if __name__ == '__main__':
    print('Запуск парсинга...')
    start_time = time.time()
    final_list = ['-', '-', '-', '-']
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    print('Ждем загрузки страницы...')
    driver.get("https://vk.com/feed")
    time.sleep(0.2)
    if avtorization(login, password, driver):
        print('Начинаем копирование из браузера, будет обработано около ' + str(count) + ' постов...')

        # Пролистывание страницы
        while len(driver.find_elements_by_class_name("post")) < count:
            driver.execute_script("scroll(0,1000000)")

        html_source = driver.page_source
        print("Копирование завершено.")
        driver.close()
        print("Драйвер брузера закрыт.")

        soup = BeautifulSoup(html_source, "html.parser")
        all_posts = soup.find_all('div', {"class": "post"})

        threading.Thread(target=parce_authors(all_posts, final_list), name="authors")
        threading.Thread(target=parce_text(all_posts, final_list), name="text")
        threading.Thread(target=parce_links(all_posts, final_list), name="links")
        threading.Thread(target=parce_images(all_posts, final_list), name="images")

    print("Парсинг завершен, время работы составило: %s сек" % (time.time() - start_time))
    threading.Thread(target=save_to_json(final_list), name="save_to_json")
    threading.Thread(target=print_posts(final_list), name="print")









