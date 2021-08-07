import os
from page_loader.page_loader import download
import tempfile
import pook
from pytest import fixture


@fixture
def get_response():
    return open('tests/fixtures/easy_html.html', encoding="utf-8").read()


@fixture
def get_html():
    return open('tests/fixtures/easy_html_images.html', encoding="utf-8").read()


@pook.on
def test_download(get_response, get_html):
    with tempfile.TemporaryDirectory() as tmpdir:
        pook.get(
            'https://ru.hexlet.io/courses',
            reply=200,
            response_body=get_response
        )
        pook.get(
            'https://ru.hexlet.io/courses/assets/professions/nodejs.png',
            reply=200,
            response_body='ok'
        )
        file_path = download('https://ru.hexlet.io/courses', tmpdir)
        page_path = f'{tmpdir}/ru-hexlet-io-courses.html'
        files_dir = f'{tmpdir}/ru-hexlet-io-courses_files'
        img_path = f'{files_dir}/ru-hexlet-io-assets-professions-nodejs.png'
        assert os.path.exists(page_path), "page file not found"
        assert os.path.exists(files_dir), "files dir not found"
        assert os.path.exists(img_path), "img file not found"
        file = open(file_path, encoding="utf-8").read()
        assert file == get_html
