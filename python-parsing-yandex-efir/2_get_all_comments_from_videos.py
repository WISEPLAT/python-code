link_to_efir = 'https://yandex.ru/efir?stream_active=blogger&stream_publisher=voditem_channel_id_42b27492a3cc0bfa9a16271b48753831'

# 1: download geckodriver.exe
# 2: add to path geckodriver.exe
# 3: pip install selenium

import time
from selenium.webdriver import Firefox
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# Эти три строки закомментируйте, а следующую раскомментируйте - тогда будет работать с вызовом интерфейса
opts = Options()
opts.headless = True # без графического интерфейса.
browser = Firefox(options=opts)
# browser = webdriver.Firefox()

all_video_url = []

#Читаем все ссылки на видео из файла
import pickle
with open ('_all_video_links_efir', 'rb') as fp:
    all_video_url = pickle.load(fp)

print('Видео для обработки: ', len(all_video_url))

id = 0
f = open('_rez_video_comments.txt', 'w')
f.write('Видео для обработки: ' + str(len(all_video_url)))


for video in all_video_url:
    browser.get(video)
    delay = 7 # seconds
    try:
        #comment_links = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'IdOfMyElement')))
        comment_links = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'cmnt-item__controls')))
        print("Page is ready!")
    except TimeoutException:
        pass #print("Loading took too much time!")

    id = id + 1
    print(id,'Ссылка на видео: ', video)
    f.write(str(id) + 'Ссылка на видео: ' + video)

    try:
        comment_links_logins = browser.find_elements_by_class_name('cmnt-item__login')
        comment_links_create = browser.find_elements_by_class_name('cmnt-item__create-date')
        comment_links_message = browser.find_elements_by_class_name('cmnt-item__message')
        comment_links_comments = browser.find_elements_by_class_name('cmnt-info-item__text')
        for c in range(0,len(comment_links_message)):
            try:
                comment_login = comment_links_logins[c].text
                comment_create = comment_links_create[c].text
                comment_message = comment_links_message[c].text
                print(comment_create, ' : ', comment_login, ' : ', comment_message)
                f.write(comment_create + ' : ' + comment_login + ' : ' + comment_message)
                for cc in comment_links_comments:
                    print(cc.text)
                    f.write(cc.text)
            except Exception:
                pass
            print('***Найден комментарий***')
            f.write('***Найден комментарий***')
    except Exception:
        pass

f.close()