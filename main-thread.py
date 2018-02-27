import os
import time
import requests
import sqlite3
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from http.client import HTTPException

# блок настроек
profile_dir = r"C:\Users\Antoshka\AppData\Local\Google\Chrome\User Data"  # директория кэша Chrome
driver_dir = ".\chromedriver.exe"  # путь до драйвера Chrome
count = 100  # количество записей для парсинга
fullsize_images = 0  # сохранять миниатюры картинок(0) или полные изображения(1). При включении скорость работы падает
download_images = 1  # сохранять(1) или нет (0) картинки на жесткий диск. При включении скорость работы падает
# конец блока настроек


def pr_text(post_all1):
    i = 0
    for post1 in post_all1:
        i += 1

        # обработка заголовка
        id_post = post1.get_attribute("ID")
        author = post1.find_element_by_xpath('//*[@id="' + id_post + '"]/div/div[1]/div/h5/a')

        if (not(len(author.text) == 0)) & (not(i > count)):
            if is_list_complete("pr_text", i):
                data_text = author.text
                # обработка текста записи
                try:
                    if (post1.find_elements_by_class_name(
                            "wall_post_more").__len__() > 0):  # проверяем ссылку "показать полностью"
                        post1.find_element_by_class_name("wall_post_more").click()

                    post_text = post1.find_element_by_class_name("wall_post_text")
                    data_text = data_text + "\n" + post_text.text + "\n"
                except Exception:
                    data_text = data_text = data_text + "\n" + "в посте нет текста или его невозможно загрузить" + "\n"
                insert_to_list("pr_text", data_text, i)
    print("Парсинг текста завершен")


def pr_links(post_all2):
    i = 0
    for post2 in post_all2:
        i += 1
        # обработка ссылок
        if not (i > count):
            if is_list_complete("pr_links", i):
                urls = post2.find_elements_by_css_selector("a[target*='_blank']")
                url_i = 0
                data_link = ''
                url_dict = []
                for url_link in urls:
                    url_check = 1
                    url_path = url_link.get_attribute("href")
                    for url_sr in url_dict:
                        if (url_path == url_sr) | (not (url_path.find(url_sr) == -1)) | (not (url_sr.find(url_path) == -1)):
                            url_check = 0
                    if url_check:
                        url_dict.append(url_path)
                for url_out in url_dict:
                    url_i += 1
                    # print("Внешняя ссылка №" + str(url_i) + ": " + url_out)
                    data_link = data_link + url_out + '\n'
                insert_to_list("pr_links", data_link, i)
    print("Парсинг ссылок завершен")

def pr_images(post_all3):
    # обработка изображений
    i = 0
    for post in post_all3:
        i += 1
        if not (i > count):
            if is_list_complete("pr_images", i):
                images = post.find_elements_by_class_name('image_cover')
                image_i = 0
                data_images = ''
                for image_link in images:
                    image_i += 1
                    try:
                        if (image_link.get_attribute("data-video") == None):
                            if (image_i > 1) & (fullsize_images == 1):

                                driver.execute_script(image_link.get_attribute("onClick"))
                                time.sleep(0.05)
                                image_this = driver.find_element_by_xpath('//*[@id="pv_photo"]/img')
                                image_path = image_this.get_attribute("src")
                                driver.execute_script("Photoview.hide(0);")
                                time.sleep(0.05)

                            else:
                                image_style = image_link.get_attribute('style')  # весь стиль
                                image_path = image_style[image_style.find('url') + 5:len(image_style) - 3]

                            # print("Изображение №" + str(image_i) + ": " + image_path)
                            data_images = data_images + image_path + '\n'

                            if (download_images == 1):
                                # print("Скачиваем изображение...")
                                resource = requests.get(image_path)
                                out_image_path = ".\downloads\img" + str(i) + "_" + str(image_i) + ".jpg"
                                out_image = open(out_image_path, 'wb')
                                out_image.write(resource.content)
                                out_image.close()
                                data_images = data_images + out_image_path + '\n'
                                # time.sleep(0.1)
                        else:
                            data_images = data_images + "Содержится видео, пропущено" + '\n'
                    except NoSuchElementException:
                        data_images = data_images + 'изображения нет или ошибка загрузки' + '\n'
                insert_to_list("pr_images", data_images, i)
    print("Парсинг изображений завершен")


def pr_print():
    print("Начинаем вывод данных")
    print("=================")
    # for i in range(count):
    #     print("Пост №" + str(i))

    for i in range(1, count+1):
        print("Пост №" + str(i))
        print("Автор и текст:")
        print(parse_list[i][0], end='\n')
        if len(parse_list[i][1]) > 1:
            print("Внешние ссылки:")
            print(parse_list[i][1], end='\n')
        if len(parse_list[i][2]) > 1:
            print("Изображения:")
            print(parse_list[i][2], end='\n')
        print('---------------')
    pass


def insert_to_list(tip, data, this_i):
     if tip == "pr_text":
        parse_list[this_i][0] = data
     if tip == "pr_links":
        parse_list[this_i][1] = data
     if tip == "pr_images":
        parse_list[this_i][2] = data


def is_list_complete(tip, this_i):
    if tip == "pr_text":
        j = 0
    if tip == "pr_links":
        j = 1
    if tip == "pr_images":
        j = 2
    try:
        if parse_list[this_i][j] == '-':
            return 1
        else:
            return 0
    except IndexError:
        return 0


class MyThread(threading.Thread):
    def __init__(self, name, posts):
        threading.Thread.__init__(self)
        self.name = name
        self.posts = posts

    def run(self):
        # Запуск потока
        try:
            if self.name == "pr_text":
                print("Запуск потока парсинга текста...")
                pr_text(post_all)
            if self.name == "pr_links":
                print("Запуск потока парсинга ссылок...")
                pr_links(post_all)
            if self.name == "pr_images":
                print("Запуск потока парсинга изображений...")
                pr_images(post_all)
        except Exception:
            print('ресурсы selenium заняты, пробуем подождать...')
            time.sleep(1)
            mf = MyThread(self.name, self.posts)
            mf.start()


if __name__ == '__main__':

    print('Стартуем...')
    start_time = time.time()

    parse_list = []
    for ip in range(1, count+2):
        parse_list.append(['-', '-', '-'])

    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))
    driver = webdriver.Chrome(driver_dir, chrome_options=options)
    print('Ждем загрузки страницы...')
    driver.get('http://vk.com/feed')
    time.sleep(0.1)

    print('Подгружаем все посты на страницу...')
    while driver.find_elements_by_xpath("//div[@class='_post_content']").__len__() <= count:
        driver.execute_script("feed.showMore();")
        time.sleep(0.1)

    print('Начинаем парсинг')
    print("=================")

    post_all = driver.find_elements_by_class_name("post")

#    Создаем группу потоков
    all_threads = []
    for ii in ["pr_text", "pr_links", "pr_images"]:
        my_thread = MyThread(ii, post_all)
        my_thread.start()
        all_threads.append(my_thread)

    for t in all_threads:
        t.join()

    time.sleep(0.5)

    while len(threading.enumerate()) > 1:
        time.sleep(0.5)
        pass
    print('Завершаем работу браузера...')
    driver.close()
    print('Парсинг завершен.')

    pr_print()

    print("время работы составило: %s сек" % (time.time() - start_time))



# elem = driver.find_element_by_id("index_email")
# elem.send_keys("pycon")


# from selenium.webdriver.common.keys import Keys
#
# driver = webdriver.Chrome()
# driver.get("http://www.python.org")
# assert "Python" in driver.title
# elem = driver.find_element_by_name("q")
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source

# if ((i % 10) == 0) & driver.find_elements_by_xpath("//div[@class='_post_content']").__len__() <= count:
#     driver.execute_script("feed.showMore();")
#     time.sleep(0.1)

# try: ПРВЕРИТЬ ПО РЕПОСТАМ
#     repost_text = post.find_element_by_class_name("copy_quote")
    # while (block_images.locked() | block_links.locked()):
        #     pass
        # block_text.acquire()

    # thread_links = threading.Thread(target=pr_links(post_all), name="pr_links")
    # thread_images = threading.Thread(target=pr_images(post_all), name="pr_images")
    # thread_text = threading.Thread(target=pr_text(post_all), name="pr_text")