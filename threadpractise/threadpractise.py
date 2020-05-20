from threading import Thread, RLock
import queue
from pip._vendor import requests


class spider(Thread):

    def __init__(self, lock, t_queue, w, timeout=10):

        super().__init__()
        self.url = 'http://www.example.com/news.php?page={id}'
        self.headers = {'cookie': 'PHPSESSIONID=xxx'}
        self.timeout = timeout
        self.queue = t_queue
        self.write = w
        self.daemon = True

    def grab(self, pageid):
        url = self.url.format(id=pageid)
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            print(response.content)
            self.write(response.content + '\n')
        except requests.RequestException as e:
            print(url, e)

    def run(self):
        while not self.queue.empty():
            pageid = self.queue.get()
            self.grab(pageid)
            self.queue.task_done()


def main():
    t_queue = queue.Queue()
    lock = RLock()
    for i in range(0, 100):
        t_queue.put(i)

    threads = 5
    t_task = []
    with open('results.txt', 'a+', encoding='utf-8')as w:
        for i in range(threads):
            task = spider(lock, t_queue, w)
            task.start()
            t_task.append(task)

        for item in t_task:
            item.join()

        t_queue.join()


if __name__ == '__main__':
    main()
