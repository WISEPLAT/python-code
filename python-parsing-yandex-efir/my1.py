link_to_efir = 'https://yandex.ru/efir?stream_active=blogger&stream_publisher=voditem_channel_id_42b27492a3cc0bfa9a16271b48753831'

# 1: download geckodriver.exe
# 2: add to path geckodriver.exe

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
# opts = Options()
# opts.headless = True # без графического интерфейса.
# browser = Firefox(options=opts)
browser = webdriver.Firefox()


browser.get(link_to_efir)
search_form = browser.find_element_by_tag_name('html')

for i in range(1,4): #60->на 509 видео хватит :), указать столько, сколько страниц у вас в видео, загружается примерно 10 видео на одно нажатие вниз!
    search_form.send_keys(Keys.PAGE_DOWN)
    time.sleep(3)

all_video_url = []

links = browser.find_elements_by_tag_name('a')
for i in links:
    try:
        data_link = i.get_attribute('data-id')
        if data_link != 'None':
            new_link_efir = 'https://yandex.ru/efir?stream_id=' + data_link + '&from_block=efir_newtab'
            all_video_url.append(new_link_efir)
            print(new_link_efir)
    except Exception:
        pass

print('Найдено видео: ', len(all_video_url))


comment_test_1 = 'https://yandex.ru/efir?stream_id=47100532fd3d72cea252598951b4ab57'
comment_test_2 = 'https://yandex.ru/efir?stream_id=402e9fe955dcd519b44aaab1b3df950f'

browser.get(comment_test_1)

#time.sleep(10) #For ad

delay = 30 # seconds
try:
    #comment_links = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'IdOfMyElement')))
    comment_links = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'cmnt-item__controls')))
    print("Page is ready!")
except TimeoutException:
    print("Loading took too much time!")

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
        for cc in comment_links_comments:
            print(cc.text)
    except Exception:
        pass

print('***Найден комментарий***')
