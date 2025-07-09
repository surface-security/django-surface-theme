from setuptools import setup


def get_install_requires():
    install_requires = [
        "Django>=3,<6",
        "django-jsoneditor>0.1,<=0.2",
    ]

    try:
        import importlib
    except ImportError:
        install_requires.append("importlib")

    try:
        from collections import OrderedDict
    except ImportError:
        install_requires.append("ordereddict")

    return install_requires


setup(install_requires=get_install_requires())
