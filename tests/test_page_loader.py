from page_loader.page_loader import download
import tempfile


def test_download():
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = download('https://ru.hexlet.io/courses', tmpdir)
        temp_path = f'{tmpdir}/ru-hexlet-io-courses.html'
        assert file_path == temp_path
