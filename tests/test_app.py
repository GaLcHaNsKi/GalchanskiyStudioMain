from pathlib import Path
from html.parser import HTMLParser

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING': True, 'GUITAR_TUNER_APK_PATH': tmp_path / 'release.apk',
                       'LIBRARY_URL': 'https://library.example.org',
                       'GITHUB_URL': 'https://github.com/example'})


@pytest.mark.parametrize('url,text', [('/', 'Разработка'), ('/projects/guitar-tuner', 'Простой и точный'), ('/health', 'ok')])
def test_routes(app, url, text):
    response = app.test_client().get(url)
    assert response.status_code == 200
    assert text in response.get_data(as_text=True)
    assert 'Set-Cookie' not in response.headers


def test_links(app):
    html = app.test_client().get('/').get_data(as_text=True)
    for url in ('https://library.example.org', 'https://github.com/example', '/projects/guitar-tuner', '/#projects'):
        assert f'href="{url}"' in html
    assert '/downloads/' not in html


def test_missing_apk(app):
    client = app.test_client()
    html = client.get('/projects/guitar-tuner').get_data(as_text=True)
    assert 'Скоро будет доступно' in html
    assert 'href="/downloads/guitar-tuner.apk"' not in html
    assert client.get('/downloads/guitar-tuner.apk').status_code == 404


def test_download_headers_range_and_bytes(app):
    data = b'PK' + bytes(range(256)) * 8
    Path(app.config['GUITAR_TUNER_APK_PATH']).write_bytes(data)
    client = app.test_client()
    html = client.get('/projects/guitar-tuner').get_data(as_text=True)
    assert 'href="/downloads/guitar-tuner.apk"' in html
    response = client.get('/downloads/guitar-tuner.apk')
    assert response.data == data
    assert response.mimetype == 'application/vnd.android.package-archive'
    assert response.headers['Content-Disposition'] == 'attachment; filename=guitar-tuner.apk'
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert int(response.headers['Content-Length']) == len(data)
    partial = client.get('/downloads/guitar-tuner.apk', headers={'Range': 'bytes=0-9'})
    assert partial.status_code == 206
    assert partial.data == data[:10]
    # Query arguments cannot replace the configured path.
    assert client.get('/downloads/guitar-tuner.apk?path=/etc/passwd').data == data


@pytest.mark.parametrize('url', ['/downloads/../../etc/passwd', '/downloads/other.apk', '/projects/library'])
def test_no_arbitrary_routes(app, url):
    assert app.test_client().get(url).status_code == 404


def test_unset_links_have_no_fake_destinations(app):
    app.config.update(LIBRARY_URL='', GITHUB_URL='')
    html = app.test_client().get('/').get_data(as_text=True)
    assert 'Ссылка скоро появится' in html
    assert 'href=""' not in html
    assert 'href="#"' not in html


@pytest.mark.parametrize('value', ['javascript:alert(1)', '//example.com', 'https://user:pass@example.com'])
def test_unsafe_config_rejected(monkeypatch, value):
    monkeypatch.setenv('LIBRARY_URL', value)
    with pytest.raises(ValueError, match='LIBRARY_URL'):
        create_app()


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script', 'img', 'link'}:
            self.urls.extend(attrs[k] for k in ('href', 'src') if k in attrs)


def test_assets_are_local_and_available(app):
    client = app.test_client()
    for route in ('/', '/projects/guitar-tuner'):
        parser = Assets()
        parser.feed(client.get(route).get_data(as_text=True))
        for url in parser.urls:
            assert url.startswith('/static/')
            response = client.get(url)
            assert response.status_code == 200
            assert 'max-age=86400' in response.headers['Cache-Control']


def test_screenshot_and_release_configuration(app):
    app.config.update(GUITAR_TUNER_SCREENSHOTS=('images/first.png', 'images/second.png'), GUITAR_TUNER_RELEASE_DATE='2026-11-11')
    html = app.test_client().get('/projects/guitar-tuner').get_data(as_text=True)
    assert '/static/images/first.png' in html
    assert '/static/images/second.png' in html
    assert '2026-11-11' in html
