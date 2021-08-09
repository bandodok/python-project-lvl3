import re
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import shutil
import logging


logging.basicConfig(
    level=logging.DEBUG,
    filename='app.log',
    filemode='w',
    format="%(asctime)s - "
           "%(levelname)s - "
           "(%(filename)s).%(funcName)s(%(lineno)d) - "
           "%(message)s",
)
logger = logging.getLogger(__name__)


def download(web_path, output_path=os.getcwd()):
    response = web_request(web_path)
    soup = BeautifulSoup(response, 'html.parser')
    file_name = url_str_replace(web_path)
    path = f'{output_path}/{file_name}'
    dir_path = f'{path[:-5]}_files'
    mkdir(dir_path)
    tags = soup.find_all(['img', 'link', 'script'])
    netloc = urlparse(web_path).netloc
    for tag in tags:
        atr = choose_atr(tag)
        if not tag.get(atr, None):
            continue
        source = tag[atr]
        file_netloc = urlparse(source).netloc
        if file_netloc in (netloc, ''):
            full_url = get_full_url(web_path, file_netloc, source)
            file_name = url_str_replace(netloc + tag[atr])
            file_name = f'{dir_path}/{file_name}'
            write_file(tag, atr, full_url, file_name)
    new_soup = soup
    with open(path, 'wb') as f:
        f.write(new_soup.encode(formatter="html5"))
    return path


def write_file(tag, atr, url, name):
    try:
        r = requests.get(url)
    except requests.exceptions.InvalidURL:
        logging.error(f'Invalid url: {url}')
        return
    except requests.exceptions.MissingSchema:
        logging.error(f'Missing schema: {url}')
        return
    if r.status_code == 200:
        with open(name, 'wb') as f:
            f.write(r.content)
        file_path = '/'.join(name.split('/')[-2:])
        tag[atr] = file_path


def get_full_url(web_path, file_netloc, source):
    if file_netloc == '':
        full_url = f'{web_path}{source}'
    else:
        full_url = source
    return full_url


def choose_atr(tag):
    tags = {
        'img': 'src',
        'link': 'href',
        'script': 'src'
    }
    return tags.get(tag.name)


def web_request(path):
    r = requests.get(path)
    return r.content


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
