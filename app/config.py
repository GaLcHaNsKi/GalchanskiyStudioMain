"""Application settings. Environment values are read when the app is created."""
import os
from pathlib import Path
from urllib.parse import urlsplit

BASE_DIR = Path(__file__).resolve().parent.parent


def public_url(name, default=''):
    value = os.environ.get(name, default).strip()
    if value:
        parsed = urlsplit(value)
        if parsed.scheme not in {'http', 'https'} or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError(f'{name} must be an absolute HTTP(S) URL without credentials')
    return value


def settings():
    apk = Path(os.environ.get('GUITAR_TUNER_APK_PATH', 'guitar-tuner.apk')).expanduser()
    return {
        'STUDIO_NAME': os.environ.get('STUDIO_NAME', 'Galchanskiy Studio'),
        'LIBRARY_URL': public_url('LIBRARY_URL', 'https://library.galchanskiy-studio.com'),
        'GITHUB_URL': public_url('GITHUB_URL', 'https://github.com/GaLcHaNsKi'),
        'GUITAR_TUNER_APK_PATH': apk if apk.is_absolute() else BASE_DIR / apk,
        'GUITAR_TUNER_VERSION': os.environ.get('GUITAR_TUNER_VERSION', '0.1.0'),
        'GUITAR_TUNER_MIN_ANDROID': os.environ.get('GUITAR_TUNER_MIN_ANDROID', '8.0'),
        'GUITAR_TUNER_RELEASE_DATE': os.environ.get('GUITAR_TUNER_RELEASE_DATE', ''),
        # Paths relative to app/static; add real screenshots here or in an app config override.
        'GUITAR_TUNER_SCREENSHOTS': ('images/tuner-screenshot.jpg',),
        'SEND_FILE_MAX_AGE_DEFAULT': 86400,
    }
