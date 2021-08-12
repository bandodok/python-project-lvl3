import os
from page_loader.page_loader import download
import tempfile
import pook
import pytest


@pytest.fixture
def get_response():
    return open('tests/fixtures/easy_html.html', encoding="utf-8").read()


@pytest.fixture
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
            'https://ru.hexlet.io/assets/professions/nodejs.png',
            reply=200,
            response_body='ok'
        )
        pook.get(
            'https://ru.hexlet.io/assets/application.css',
            reply=200,
            response_body='ok'
        )
        pook.get(
            'https://ru.hexlet.io/courses',
            reply=200,
            response_body='ok'
        )
        pook.get(
            'https://ru.hexlet.io/packs/js/runtime.js',
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


@pook.on
def test_download_404(caplog):
    pook.get(
        'https://ru.hexlet.io/courses',
        reply=404,
    )
    with pytest.raises(SystemExit):
        download('https://ru.hexlet.io/courses')
    assert '404 Client Error: Not Found for url: https://ru.hexlet.io/courses' in caplog.text
    caplog.clear()


@pook.on
def test_download_500(caplog):
    pook.get(
        'https://google.com',
        reply=500,
    )
    with pytest.raises(SystemExit):
        download('https://google.com')
    assert '500 Server Error: Internal Server Error for url: https://google.com' in caplog.text
    caplog.clear()


@pook.on
def test_download_invalid_path(caplog):
    pook.get(
        'https://yandex.ru',
        reply=200,
    )
    with pytest.raises(SystemExit):
        download('https://yandex.ru', 'D:\\qwe')
    assert 'Invalid path: D:\\qwe' in caplog.text
    caplog.clear()


def test_download_invalid_url(caplog):
    with pytest.raises(SystemExit):
        download('qwe')
    assert "Invalid URL 'qwe': No schema supplied. Perhaps you meant http://qwe?" in caplog.text
    caplog.clear()


@pook.on
def test_download_permissions_denied(caplog):
    pook.get(
        'https://ya.ru',
        reply=200,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        path = tmpdir + '/qwerty'
        os.mkdir(path, mode=0o111)
        with pytest.raises(SystemExit):
            download('https://ya.ru', path)
        assert 'PermissionError: Access denied: D:\\project\\qwerty/ya-ru_files\n' in caplog.text
        caplog.clear()
