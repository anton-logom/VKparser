from selenium import webdriver
import time, requests, threading, pickle
from bs4 import BeautifulSoup


#Settings
count = 100
save_images_path = "/Users/r3m1x/Developer/PycharmProjects/OS/img/"
chrome_driver_path = "/Users/r3m1x/Developer/PycharmProjects/OS/chromedriver"
chrome_cash_path = "--user-data-dir=/Users/r3m1x/Developer/PycharmProjects/OS/cash"


def parce_text(posts, final):
    print("Начало парсинга текста.")
    post_num = -1
    for post in posts:
        post_num += 1
        if not (post_num > count-1):
            author_post = post.find('a', {"class": "author"})
            data_text = author_post.text
            try:
                post_text = post.find('div', {"class" : "wall_post_text"})
                text = post_text.text
                data_text += "\n" + text + "\n"
            except Exception:
                data_text += "\n" + "В посте отсутсвует текст или его невозможно загрузить." + "\n"
            insert_to_list("pr_text", data_text, post_num, final)
    print("Парсинг текста завершен.")


def parce_links(posts, final):
    print("Начало парсинга ссылок.")
    post_num = -1
    for post in posts:
        post_num += 1
        if not (post_num > count-1):
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
                    data_links += 'https://vk.com' + url_out + '\n'
                insert_to_list("pr_links", data_links, post_num, final)
    print("Парсинг ссылок завершен.")


def parce_images(posts, final):
    print("Начало парсинга изображений.")
    post_num = -1
    for post in posts:
        post_num += 1
        if not (post_num > count-1):
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
                        out_image_path = save_images_path + str(post_num) + "_" + str(image_num) + ".jpg"
                        out_image = open(out_image_path, 'wb')
                        out_image.write(resource.content)
                        out_image.close()
                        data_images = data_images + out_image_path + '\n'

                    else:
                        data_images = data_images + "Содержится видео, пропущено." + '\n'
                except Exception:
                    data_images += 'Изображение отсутсвует или возникоа ошибка загрузки.' + '\n'
            insert_to_list("pr_images", data_images, post_num, final)
    print("Парсинг изображений завершен.")


def insert_to_list(data_type, data, this_i, final):
     if data_type == "pr_text":
        final[this_i][0] = data
     if data_type == "pr_links":
        final[this_i][1] = data
     if data_type == "pr_images":
        final[this_i][2] = data


def print_posts(list):
    print("Вывод данных")
    print("=================")
    for i in range(0, len(list)):
        print("Пост №" + str(i))
        print("Автор и текст:")
        print(list[i][0], end='\n')
        if len(list[i][1]) > 1:
            print("Внешние ссылки:")
            print(list[i][1], end='\n')
        if len(list[i][2]) > 1:
            print("Изображения:")
            print(list[i][2], end='\n')
        print('---------------')


class MyThread(threading.Thread):
    def __init__(self, name, posts, list):
        threading.Thread.__init__(self)
        self.name = name
        self.posts = posts
        self.list = list

    def run(self):
        if self.name == "pr_text":
            parce_text(self.posts, self.list)
        if self.name == "pr_links":
            parce_links(self.posts, self.list)
        if self.name == "pr_images":
            parce_images(self.posts, self.list)


def parce_main(final):
    # count = int(input("Введите кол-во новостей для парсинга: "))
    options = webdriver.ChromeOptions()
    options.add_argument(chrome_cash_path)
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)

    print('Ждем загрузки страницы...')
    time.sleep(1)
    driver.get("https://vk.com/feed")

    #Пролистывание страницы
    while len(driver.find_elements_by_class_name("post")) < count:
        driver.execute_script("scroll(0,1000000)")

    #Прогрузка страницы
    # while driver.find_elements_by_xpath("//div[@class='_post_content']").__len__() < count:
    #     driver.execute_script("feed.showMore();")

    html_source = driver.page_source
    driver.close()
    print("Chromedriver закрыт.")

    soup = BeautifulSoup(html_source, "html.parser")
    all_posts = soup.find_all('div', {"class": "post"})

    all_threads = []
    for i in ["pr_text", "pr_links", "pr_images"]:
        my_thread = MyThread(i, all_posts, final)
        my_thread.start()
        all_threads.append(my_thread)

    while len(threading.enumerate()) > 1:
        time.sleep(0.5)
        pass

def save_parcelist_to_file(lst):
    with open('outfile', 'wb') as file:
        pickle.dump(lst, file)


def open_parcelist_from_file(lst):
    with open('outfile', 'rb') as file:
        lst = pickle.load(file)

if __name__ == '__main__':
    print('Запуск...')
    start_time = time.time()

    final_list = []
    for i in range(0, count):
        final_list.append(['-', '-', '-'])

    parce_main(final_list)

    save_parcelist_to_file(final_list)
    open_parcelist_from_file(final_list)

    print_posts(final_list)

    print("Время работы составило: %s сек" % (time.time() - start_time))











