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
def test_download_404():
    pook.get(
        'https://ru.hexlet.io/courses',
        reply=404,
    )
    with pytest.raises(Exception) as e:
        download('https://ru.hexlet.io/courses')
    assert '404 Client Error: Not Found for url:' in e.value.args[0]
    assert 'https://ru.hexlet.io/courses' in e.value.args[0]


@pook.on
def test_download_500():
    pook.get(
        'https://google.com',
        reply=500,
    )
    with pytest.raises(Exception) as e:
        download('https://google.com')
    assert '500 Server Error: Internal Server Error for url:' in e.value.args[0]
    assert 'https://google.com' in e.value.args[0]


@pook.on
def test_download_invalid_path():
    pook.get(
        'https://yandex.ru',
        reply=200,
    )
    with pytest.raises(OSError) as e:
        download('https://yandex.ru', '/qwe')
    assert 'No such file or directory' in e.value.args[0]


def test_download_invalid_url():
    with pytest.raises(Exception) as e:
        download('qwe')
    assert "Invalid URL 'qwe':" in e.value.args[0]
    assert 'No schema supplied. Perhaps you meant' in e.value.args[0]
    assert 'http://qwe?' in e.value.args[0]


@pook.on
def test_download_permissions_denied():
    pook.get(
        'https://ya.ru',
        reply=200,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        path = tmpdir + '/qwerty'
        os.mkdir(path, mode=0o111)
        with pytest.raises(OSError) as e:
            download('https://ya.ru', path)
        assert 'Permission denied' in e.value.args[0]
