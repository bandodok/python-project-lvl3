import re
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import shutil


def download(web_path, output_path=os.getcwd()):
    response = web_request(web_path)
    soup = BeautifulSoup(response, 'html.parser')
    file_name = url_str_replace(web_path)
    path = f'{output_path}/{file_name}'
    dir_path = f'{path[:-5]}_files'
    file_path = f'{path}'
    mkdir(dir_path)
    new_page = PageLoader(soup, web_path, dir_path)
    new_soup = new_page.download()
    with open(file_path, 'wb') as f:
        f.write(new_soup)
    return file_path


def web_request(path):
    r = requests.get(path)
    return r.content


class PageLoader:
    def __init__(self, soup, url, dir):
        self.soup = soup
        self.url = url
        self.dir = dir
        self.netloc = urlparse(self.url).netloc
        self.tags = {
            'images': {'tag': 'img', 'atr': 'src'},
            'links': {'tag': 'link', 'atr': 'href'},
            'scripts': {'tag': 'script', 'atr': 'src'}
        }

    def download(self):
        for v in self.tags.values():
            self.soup = self._download_files(v)
        return self.soup.encode(formatter="html5")

    def _get_full_url(self, file, file_netloc):
        if file_netloc == self.netloc:
            full_url = file[self._atr]
        else:
            full_url = self.url + file[self._atr]
        return full_url

    def _write_file(self, file, url, name):
        r = requests.get(url)
        if r.status_code == 200:
            with open(name, 'wb') as f:
                f.write(r.content)
            file_path = '/'.join(name.split('/')[-2:])
            file[self._atr] = file_path

    def _download_files(self, tags):
        self._tag = tags['tag']
        self._atr = tags['atr']
        files = self.soup.find_all(self._tag)
        for file in files:
            if not file.get(self._atr, None):
                continue
            file_netloc = urlparse(file[self._atr]).netloc
            if file_netloc in (self.netloc, ''):
                full_url = self._get_full_url(file, file_netloc)
                file_name = url_str_replace(self.netloc + file[self._atr])
                file_name = f'{self.dir}/{file_name}'
                self._write_file(file, full_url, file_name)
        return self.soup


def mkdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)


def url_str_replace(url):
    parse = ''.join(urlparse(url)[1:]).strip()
    parse_after = re.sub(r'\W', '-', parse)
    formats = {
        '-png': '.png',
        '-css': '.css',
        '-js': '.js'
    }
    file_format = [x for x in formats if parse_after.endswith(x)]
    if file_format:
        file_format = file_format[0]
        parse_after = parse_after[:-len(file_format)] + formats[file_format]
    else:
        parse_after = parse_after + '.html'
    return parse_after
