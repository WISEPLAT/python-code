from auth import login, password
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time, random


def login_chrome(login, password):
    browser = webdriver.Chrome()
    browser.implicitly_wait(5)
    browser.get('https://www.instagram.com')
    time.sleep(10)
    browser.close()
    browser.quit()


def login_firefox(login, password):
    browser = webdriver.Firefox()
    browser.implicitly_wait(5)
    browser.get('https://www.instagram.com')
    time.sleep(10)
    browser.close()
    browser.quit()


def login_firefox_chrome(_browser, login, password):
    if _browser == "Chrome":
        browser = webdriver.Chrome()
    else:
        browser = webdriver.Firefox()
    browser.implicitly_wait(5)
    browser.get('https://www.instagram.com')
    time.sleep(random.randrange(2,7))

    _login = browser.find_element(By.NAME, "username")
    _login.clear()
    _login.send_keys(login)

    time.sleep(random.randrange(1, 2))

    _password = browser.find_element(By.NAME, "password")
    _password.clear()
    _password.send_keys(password)

    time.sleep(random.randrange(1, 2))

    _password.send_keys(Keys.ENTER)

    # _login_button = browser.find_element_by_css_selector('button[type="submit"]')
    # _login_button.click()

    time.sleep(100)

    browser.close()
    browser.quit()

#login_chrome(login, password)
#login_firefox(login, password)
login_firefox_chrome("Firefox", login, password)
