import requests


def save_file_from_www(link):
    filename = link.split('/')[-1]
    r = requests.get(link, allow_redirects=True)
    open(filename, 'wb').write(r.content)


link1 = 'https://raw.githubusercontent.com/WISEPLAT/python-code/master/python-xml/yandex_xml_zhilaya.xml'
link2 = 'https://raw.githubusercontent.com/WISEPLAT/python-code/master/python-xml/yandex_xml_commercial.xml'
link3 = 'https://www.culture.ru/storage/images/5cb82d851c1b7c86f5572a72874daa92/59108e2912262e451d2121b407846c44.jpg'

save_file_from_www(link1)
save_file_from_www(link2)
save_file_from_www(link3)
