import os
import threading
import subprocess
from queue import Queue

MAX_THREADS = 25 # 한번에 스캔할 url의 수 
LOG_DIR = 'nuclei-log'

class ScannerThread(threading.Thread):
    def __init__(self, thread_id, url_queue):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.url_queue = url_queue

    def run(self):
        while True:
            url = self.url_queue.get()
            if url is None:
                break
            print(f"[+] Thread-{self.thread_id} : Scanning {url}")
            log_file = os.path.join(LOG_DIR, f"log-{self.thread_id}.txt")
            with open(log_file, 'a') as f:
                f.write(f"\n[+] Scan URL: {url}\n")
                f.write("-"*50)
                subprocess.run(["nuclei", "-u", url], stdout=f, stderr=subprocess.STDOUT)
            self.url_queue.task_done()

def main():
    with open('subdomain_results.txt', 'r') as file: # 사용자가 원하는 target url 파일로 수정.
        urls = file.readlines()
    urls = [url.strip() for url in urls]

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    url_queue = Queue()
    for url in urls:
        url_queue.put(url)

    threads = []
    for thread_id in range(1, MAX_THREADS + 1):
        thread = ScannerThread(thread_id, url_queue)
        thread.start()
        threads.append(thread)

    url_queue.join()

    for _ in range(MAX_THREADS):
        url_queue.put(None)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
