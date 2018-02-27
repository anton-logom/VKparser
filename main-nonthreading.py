import os
import time
import requests
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# блок настроек
profile_dir = r"C:\Users\Antoshka\AppData\Local\Google\Chrome\User Data"  # директория кэша Chrome
driver_dir = ".\chromedriver.exe"  # путь до драйвера Chrome
count = 100  # количество записей для парсинга
fullsize_images = 0  # сохранять миниатюры картинок(0) или полные изображения(1). При включении скорость работы падает
download_images = 1  # сохранять(1) или нет (0) картинки на жесткий диск. При включении скорость работы падает еще больше
# конец блока настроек


if __name__ == '__main__':
    print('Стартуем...')
    start_time = time.time()
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))
    driver = webdriver.Chrome(driver_dir, chrome_options=options)
    print('Ждем загрузки страницы...')
    driver.get('http://vk.com/feed')
    time.sleep(0.1)

    print('Подгружаем все записи...')
    while driver.find_elements_by_xpath("//div[@class='_post_content']").__len__() <= count:
        driver.execute_script("feed.showMore();")
        time.sleep(0.1)

    print('Начинаем парсинг')
    print("=================")

    post_all = driver.find_elements_by_class_name("post")

    i = 0
    for post in post_all:
        i += 1

        # обработка заголовка
        id_post = post.get_attribute("ID")
        author = driver.find_element_by_xpath('//*[@id="' + id_post + '"]/div/div[1]/div/h5/a')
        if len(author.text) == 0:
            break
        if i > count:
            break

        print("Пост №" + str(i))
        print(author.text)

        # обработка текста записи
        try:
            if (post.find_elements_by_class_name("wall_post_more").__len__() > 0):  # проверяем ссылку "показать полностью"
                post.find_element_by_class_name("wall_post_more").click()

            post_text = post.find_element_by_class_name("wall_post_text")
            print(post_text.text)
        except Exception:
            print("нет текста")

        # try: ПРВЕРИТЬ ПО РЕПОСТАМ
        #     repost_text = post.find_element_by_class_name("copy_quote")

        # обработка ссылок
        urls = post.find_elements_by_tag_name("a")
        url_i = 0
        url_dict = []
        for url_link in urls:
            if (url_link.get_attribute("target") == "_blank"):
                url_check = 1
                url_path = url_link.get_attribute("href")
                for url_sr in url_dict:
                    if (url_path == url_sr) | (not(url_path.find(url_sr) == -1)) | (not(url_sr.find(url_path) == -1)):
                        url_check = 0
                if url_check:
                    url_dict.append(url_path)
        for url_out in url_dict:
            url_i += 1
            print("Внешняя ссылка №" + str(url_i) + ": "+ url_out)

        # обработка изображений
        images = post.find_elements_by_class_name('image_cover')
        image_i = 0
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

                    print("Изображение №" + str(image_i) + ": " + image_path)

                    if (download_images == 1):
                        print("Скачиваем изображение...")
                        resource = requests.get(image_path)
                        out_image_path = ".\downloads\img" + str(i) + "_" + str(image_i) + ".jpg"
                        out_image = open(out_image_path, 'wb')
                        out_image.write(resource.content)
                        out_image.close()
                        print("Готово. " + out_image_path)
                        time.sleep(0.1)
                else:
                    print("Содержится видео, пропущено")
            except NoSuchElementException:
                print("изображения нет или ошибка загрузки")


        print("=================")


    print('Завершаем работу...')
    driver.close()

    print("--- %s секунд ---" % (time.time() - start_time))

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