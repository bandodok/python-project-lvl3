import sys
import re
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import shutil
from page_loader.logger import get_logger
from progress.bar import Bar

logger = get_logger(__name__)


def download(web_path, output_path=os.getcwd()):
    output_path = os.path.abspath(output_path)
    check_output_path(output_path)
    r = web_request(web_path)
    response = r.content
    soup = BeautifulSoup(response, 'html.parser')
    file_name = make_file_name(web_path)
    path = f'{output_path}/{file_name}'
    dir_path = f'{path[:-5]}_files'
    mkdir(dir_path)
    tags = soup.find_all(['img', 'link', 'script'])
    netloc = urlparse(web_path).netloc
    tags = [tag for tag in tags if tag.get(choose_atr(tag), None) is not None]
    for tag in tags:
        atr = choose_atr(tag)
        source = tag[atr]
        file_netloc = urlparse(source).netloc
        file_scheme = urlparse(source).scheme
        if file_netloc in (netloc, '') and file_scheme != 'data':
            full_url = get_full_url(web_path, file_netloc, source)
            file_name = make_file_name(full_url)
            file_name = f'{dir_path}/{file_name}'
            write_file(tag, atr, full_url, file_name)
    with open(path, 'wb') as f:
        f.write(soup.prettify(encoding='utf-8', formatter='html5'))
    return path


def traceback_off(func):
    def wrapper(*args, **kwargs):
        sys.tracebacklimit = 0
        output = func(*args, **kwargs)
        sys.tracebacklimit = 5
        return output
    return wrapper


@traceback_off
def check_output_path(path):
    if not os.path.exists(path):
        raise OSError(os.strerror(2), path)


def write_file(tag, atr, url, name):
    logger.debug(f'get url {url}')
    r = web_request(url)
    total = r.headers.get('content-length')
    with open(name, 'wb') as f:
        if not total:
            f.write(r.content)
        else:
            total = int(total)
            b = Bar('downloading ', suffix='%(percent)d%%')
            print(url)
            chunk_size = max(total // 100, 400)
            for data in b.iter(r.iter_content(chunk_size=chunk_size)):
                f.write(data)
            b.finish()
    logger.debug(f'saved file {name}')
    file_path = '/'.join(name.split('/')[-2:])
    tag[atr] = file_path


def get_full_url(web_path, file_netloc, source):
    if file_netloc == '':
        scheme = urlparse(web_path).scheme
        netloc = urlparse(web_path).netloc
        path = f'{scheme}://{netloc}'
        full_url = f'{path}{source}'
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


@traceback_off
def web_request(path):
    r = requests.get(path, allow_redirects=False, stream=True)
    r.raise_for_status()
    if str(r.status_code).startswith('3'):
        raise requests.exceptions.ConnectionError(path)
    return r


@traceback_off
def mkdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    try:
        os.mkdir(path)
    except OSError:
        raise OSError(os.strerror(13), path)


def url_str_replace(url):
    parse = ''.join(urlparse(url)[1:]).strip()
    parse_after = re.sub(r'\W', '-', parse)
    return parse_after


def get_format(url):
    path = urlparse(url).path
    format = path.split('.').pop()
    format_list = [
        'js', 'css', 'png',
        'jpg', 'ico', 'xml',
        'html', 'rss', 'gif'
    ]
    if format not in format_list:
        format = 'html'
    return format


def make_file_name(url):
    format = get_format(url)
    parsed = url_str_replace(url)
    if parsed.endswith(f'-{format}'):
        format_len = (len(format) + 1)
        file_name = parsed[:-format_len] + f'.{format}'
    else:
        file_name = parsed.replace(f'-{format}', '') + f'.{format}'
    return file_name
