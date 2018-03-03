from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests
import threading


def parce_text(posts):
    print("Начало парсинга текста.")
    post_num = -1
    for post in posts:
        post_num += 1
        if not (post_num > count):
            author_post = post.find('a', {"class": "author"})
            data_text = author_post.text
            try:
                post_text = post.find('div', {"class" : "wall_post_text"})
                text = post_text.text
                data_text += "\n" + text + "\n"
            except Exception:
                data_text += "\n" + "В посте отсутсвует текст или его невозможно загрузить." + "\n"
            insert_to_list("pr_text", data_text, post_num)
    print("Парсинг текста завершен.")


def parce_links(posts):
    print("Начало парсинга ссылок.")
    post_num = -1
    for post in posts:
        post_num += 1
        if not (post_num > count):
            post_links = post.find_all('a', {"target": "_blank"})
            link_num = -1
            data_links = ''
            link_dict = []
            for url_link in post_links:
                link_check = True
                link_path = url_link.attrs["href"]
                for url_added in link_dict:
                    if (link_path == url_added) | (not (link_path.find(url_added) == -1)) | (not (url_added.find(link_path) == -1)):
                        link_check = False
                if link_check:
                    link_dict.append(link_path)
                for url_out in link_dict:
                    link_num += 1
                    data_links += url_out + '\n'
                insert_to_list("pr_links", data_links, post_num)
    print("Парсинг ссылок завершен.")


def parce_images(posts):
    print("Начало парсинга изображений.")
    post_num = -1
    for post in posts:
        post_num += 1
        if not (post_num > count):
            post_images = post.find_all('a', {"class": "image_cover"})
            image_num = -1
            data_images = ''
            for image in post_images:
                image_num += 1
                try:
                    if not image.has_attr('data-video'):
                        image_style = image.attrs["style"]
                        image_path = image_style[image_style.find('url') + 4:len(image_style) - 2]

                        data_images += image_path + '\n'

                        resource = requests.get(image_path)
                        out_image_path = "/Users/r3m1x/Developer/PycharmProjects/OS/img/" + str(post_num) + "_" + str(image_num) + ".jpg"
                        out_image = open(out_image_path, 'wb')
                        out_image.write(resource.content)
                        out_image.close()
                        data_images = data_images + out_image_path + '\n'

                    else:
                        data_images = data_images + "Содержится видео, пропущено." + '\n'
                except Exception:
                    data_images += 'Изображение отсутсвует или возникоа ошибка загрузки.' + '\n'
            insert_to_list("pr_images", data_images, post_num)
    print("Парсинг изображений завершен.")


def insert_to_list(data_type, data, this_i):
     if data_type == "pr_text":
        parse_list[this_i][0] = data
     if data_type == "pr_links":
        parse_list[this_i][1] = data
     if data_type == "pr_images":
        parse_list[this_i][2] = data


def print_posts():
    print("Вывод данных")
    print("=================")
    for i in range(0, count+1):
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


class MyThread(threading.Thread):
    def __init__(self, name, posts):
        threading.Thread.__init__(self)
        self.name = name
        self.posts = posts

    def run(self):
        # Запуск потока
        # try:
        if self.name == "pr_text":
            # print("Запуск потока парсинга текста...")
            parce_text(self.posts)
        if self.name == "pr_links":
            # print("Запуск потока парсинга ссылок...")
            parce_links(self.posts)
        if self.name == "pr_images":
            # print("Запуск потока парсинга изображений...")
            parce_images(self.posts)
        # except Exception:
        #     pass
        #     mf = MyThread(self.name, self.posts)
        #     mf.start()

    # def Scrolling(WebDriver driver):
    #     for j in range (1, 61):
    #         driver.executeScript("scroll(0,1000000)")


if __name__ == '__main__':
    print('Запуск...')
    start_time = time.time()

    parse_list = []
    # count = int(input("Введите кол-во новостей для парсинга: "))
    count = 100

    for i in range(0, count+1):
        parse_list.append(['-', '-', '-'])

    opt = webdriver.ChromeOptions()
    opt.add_argument("--user-data-dir=/Users/r3m1x/Developer/PycharmProjects/OS/cash")
    driver = webdriver.Chrome("/Users/r3m1x/Developer/PycharmProjects/OS/chromedriver", chrome_options=opt)

    print('Ждем загрузки страницы...')
    time.sleep(1)
    driver.get("https://vk.com/feed")

    # while True:

    while len(driver.find_elements_by_class_name("post")) <= count:
        driver.execute_script("scroll(0,1000000)")

    # while driver.find_elements_by_xpath("//div[@class='_post_content']").__len__() <= count:
    #     driver.execute_script("feed.showMore();")

    html_source = driver.page_source
    driver.close()
    print("Chromedriver закрыт.")

    soup = BeautifulSoup(html_source, "html.parser")
    all_posts = soup.find_all('div', {"class": "post"})

    # thread_links = threading.Thread(target=parce_links(all_posts), name="parce_links")
    # thread_images = threading.Thread(target=parce_images(all_posts), name="parce_images")
    # thread_text = threading.Thread(target=parce_text(all_posts), name="parce_text")

    # Создаем группу потоков
    all_threads = []
    for i in ["pr_text", "pr_links", "pr_images"]:
        my_thread = MyThread(i, all_posts)
        my_thread.start()
        all_threads.append(my_thread)

    while len(threading.enumerate()) > 1:
        time.sleep(0.5)
        pass

    print_posts()

    print("Время работы составило: %s сек" % (time.time() - start_time))

















