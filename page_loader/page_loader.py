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
    dir_path = f'{path}_files'
    file_path = f'{path}.html'
    mkdir(dir_path)
    soup = download_images(soup, web_path, dir_path)
    with open(file_path, 'wb') as f:
        f.write(soup.encode(formatter="html5"))
    return file_path


def web_request(path):
    r = requests.get(path)
    return r.content


def download_images(soup, url, directory):
    imgs = soup.find_all('img')
    netloc = urlparse(url).netloc
    for img in imgs:
        full_url = url + img['src']
        file_name = url_str_replace(netloc + img['src'])
        img_name = f'{directory}/{file_name}'
        r = requests.get(full_url)
        if r.status_code == 200:
            with open(img_name, 'wb') as f:
                f.write(r.content)
            img_path = '/'.join(img_name.split('/')[-2:])
            img['src'] = img_path
    return soup


def mkdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)


def url_str_replace(url):
    parse = ''.join(urlparse(url)[1:]).strip()
    parse_after = re.sub(r'\W', '-', parse)
    if parse_after.endswith('-png'):
        parse_after = parse_after[:-4] + '.png'
    return parse_after
