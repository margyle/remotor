from glob import glob
import os
import subprocess
import threading

from scrapy.conf import settings


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(THIS_DIR, os.pardir)


def worker(spider):
    subprocess.check_call(['scrapy', 'crawl', spider])


def main():
    os.chdir(PROJECT_ROOT)
    spiders_module = settings.get('NEWSPIDER_MODULE').replace('.', os.sep)
    path = os.path.abspath(os.path.join(PROJECT_ROOT, spiders_module))
    spiders = glob('{path}/*.py'.format(**locals()))
    spiders = [
        os.path.basename(s)[:-3] for s in spiders
            if not s.endswith('__init__.py')]
    threads = []
    for spider in spiders:
        t = threading.Thread(target=worker, args=(spider,))
        threads.append(t)
        t.start()


if __name__ == '__main__':
    main()
