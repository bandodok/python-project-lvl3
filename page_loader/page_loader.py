import re
import os
import requests
from urllib.parse import urlparse


def download(download_path, output_path=os.getcwd()):
    r = requests.get(download_path)
    file_name = url_str_replace(download_path)
    path = f'{output_path}/{file_name}.html'
    with open(path, 'w') as f:
        f.write(r.text)
    return path


def url_str_replace(url):
    parse = ''.join(urlparse(url)[1:]).strip()
    parse_after = re.sub(r'\W', '-', parse)
    return parse_after
