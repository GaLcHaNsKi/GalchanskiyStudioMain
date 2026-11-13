from pathlib import Path

from flask import Blueprint, abort, current_app, render_template, send_file

bp = Blueprint('main', __name__)
PROJECTS = (
    {'name': 'Library', 'description': 'Управление книгами и библиотечным каталогом.', 'icon': 'book', 'theme': 'library'},
    {'name': 'Guitar Tuner', 'description': 'Точный офлайн-тюнер для гитары и баса.', 'icon': 'guitar', 'theme': 'tuner'},
)
FEATURES = (
    'Поддержка шестиструнной гитары', 'Поддержка четырёхструнной бас-гитары',
    'Автоматическое определение струны', 'Стрелочный индикатор отклонения',
    'Работа без интернета', 'Отсутствие рекламы',
)


def apk_path():
    return Path(current_app.config['GUITAR_TUNER_APK_PATH'])


@bp.get('/')
def index():
    return render_template('index.html', projects=PROJECTS)


@bp.get('/projects/guitar-tuner')
def guitar_tuner():
    path = apk_path()
    try:
        size = path.stat().st_size if path.is_file() else None
    except OSError:
        size = None
    return render_template('guitar_tuner.html', features=FEATURES, apk_size=size)


@bp.get('/downloads/guitar-tuner.apk')
def download_apk():
    # Only this configured server path is used; the request supplies no file path.
    try:
        return send_file(apk_path(), mimetype='application/vnd.android.package-archive',
                         as_attachment=True, download_name='guitar-tuner.apk',
                         conditional=True, max_age=0)
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        abort(404)


@bp.get('/health')
def health():
    return {'status': 'ok'}


@bp.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
