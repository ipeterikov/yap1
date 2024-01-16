from bs4 import BeautifulSoup
import requests
import time
import sys
from queue import Queue
from threading import Thread


def riatomsk():
    url = 'https://www.riatomsk.ru/novosti'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    titles = soup.find_all('a', class_='rubNewItem')

    list_news = []
    for title in titles:
        title_t = title.find_next('div', class_='rubNewName')
        #about = title.find_next('div', class_='rubNewAbout')
        date_t = title.find_next('div', class_='rubNewDate')
        divs = title.find_all('div')
        for about in divs:
            if 'class' not in about.attrs:
                an_text = about.text.strip()
        title_text = title_t.text
        date_text=date_t.text.strip()
        list_news.append(
            News(
                title=title_text,
                date=date_text,
                annotation=an_text,
                resource='riatomsk.ru'
            )
        )

    return list_news


def kpru():
    url = 'https://www.kp.ru/online'
    html = requests.get(url).text
    soup = BeautifulSoup(html, features='html.parser')
    news_divs = soup.find_all('div', class_='sc-1tputnk-13 ixDVFm')
    news_list = []
    for div in news_divs:
        title = div.find('a', class_='sc-1tputnk-2 drlShK')
        title_text = title.text.strip()
        date = div.find('span', class_='sc-1tputnk-9 gpa-DyG')
        date_text = date.text
        annotation = div.find('a', class_='sc-1tputnk-3 dcIDGO')
        annotation_text = annotation.text
        news_list.append(
        News(title=title_text, annotation=annotation_text, date=date_text, resource='kp.ru')
            )
    return news_list

def washingtonpost():
    url = 'https://www.washingtonpost.com/politics/'
    html = requests.get(url).text
    soup = BeautifulSoup(html, features='html.parser')
    news_divs = soup.find_all('div', class_='pb-md b bb gray-darkest mt-md')
    news_list = []
    for div in news_divs:
        title = div.find('h3', class_='font-md font-bold font--headline lh-sm gray-darkest hover-blue mb-0 antialiased mb-xxs')
        title_text = title.text.strip()
        date = div.find('span', class_='wpds-c-iKQyrV font-xxxs font-light font--meta-text lh-sm gray-dark dot-xxs-gray-dark')
        date_text = date.text
        news_list.append(
        News(title=title_text, date=date_text, resource='washingtonpost.com')
            )
    return news_list


class News:
    def __init__(self, title="", date="", annotation="", resource=""):
        self.title = title
        self.date = date
        self.annotation = annotation
        self.resource = resource

    def __str__(self):
        return ''.join(self.resource + ' ' +self.date) + '\n' + self.title + '\n' + self.annotation


def get_all_news():
    return [*washingtonpost(),*kpru(), *riatomsk()]


def background_task(q):
    timeout = 5*60
    while True:
        news = get_all_news()
        for i in news:
            q.put(i)
        time.sleep(timeout)


if __name__ == '__main__':
    q = Queue()
    background_thread = Thread(target=background_task, args=[q], daemon=True)
    shown_news = set()
    try:
        background_thread.start()
        while True:
            if not q.empty():
                a = q.get()
                if a.title not in shown_news:
                    shown_news.add(a.title)
                    print(a)
                    print(flush=True)
            else:
                time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        print("Exiting program...")
        sys.exit()