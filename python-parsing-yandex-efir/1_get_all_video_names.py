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

browser.get(link_to_efir)
search_form = browser.find_element_by_tag_name('html')

for i in range(1,70): #70->на 589 видео хватит :), указать столько, сколько страниц у вас в видео, загружается примерно 10 видео на одно нажатие вниз!
    search_form.send_keys(Keys.PAGE_DOWN)
    print(i, end=' ')
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

#Записываем все ссылки на видео в файл (с перезаписью файла)
import pickle
with open('_all_video_links_efir', 'wb+') as fp:
    pickle.dump(all_video_url, fp)



