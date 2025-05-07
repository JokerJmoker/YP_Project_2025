import os
from flask_assets import Bundle

from .functions import recursive_flatten_iterator

def get_bundle(route, tpl, ext, paths, type=False):
    """
    Создает и возвращает объект Bundle (css/js) для регистрации в главном файле приложения.
    Содержит пути до локальных исходников css/js-файлов, сгруппированных по использованию в HTML-шаблонах.

    Параметры:
        route (str): Название роута
        tpl (str): Название HTML-шаблона из папки /templates
        ext (str): Расширение файлов (css/js)
        paths (list): Список путей к исходным файлам
        defer (bool, optional): Флаг для JS-файлов с отложенной загрузкой. 
                              Используется только если это не главный файл "main.js".
                              По умолчанию False.

    Возвращает:
        Bundle: Объект Bundle для регистрации в Flask-Assets
    """
    
    if route and tpl and ext:
        return {
            'instance': Bundle(*paths, output=get_path(route, tpl, ext, type), filters=get_filter(ext)),
            'name': get_filename(route,tpl,ext,type),
            'dir': os.getcwd() 
        }
        
def register_bundle(assets, bundle):
    assets.register(bundle['name'], bundle['instance'])
    return f"Bundle {bundle['name']} registered successfully!"


def register_bundles(assets, bundles):
    for group in recursive_flatten_iterator(bundles):
        for bundle in group:
            register_bundle(assets, bundle)


def get_filename(route, tpl, ext, type):
    suffix = "_defer" if type else ""
    return f"{route}_{tpl}.{ext}{suffix}"


def get_path(route, tpl, ext, type):
    suffix = "/defer" if type else ""
    return f"gen/{route}/{tpl}{suffix}.{ext}"
    
def get_filter(ext):
    return f"{ext}min"

bundles = {
    "post": {
        "all": {
            "css": [get_bundle('post', 'all', 'css', ['css/blocks/table.css'])],
            "js": [get_bundle('post', 'all', 'js', ['js/blocks/js1.js','js/blocks/js2.js','js/blocks/js3.js'])]
        },
        "create": {},
        "update": {},
    },
    "user": {
        "login": {},
        "register": {},
    },
}
