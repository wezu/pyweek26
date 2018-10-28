import _locale
_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf_8'])

from setuptools import setup

setup(
    name="game",
    options = {
        'build_apps': {
            'include_patterns': [
                '*.png',
                '*.ttf',
                '*.bam',
                '*.glsl',
                '*.txt',
                '*.ico',
                '*.dds',
                '*.prc',
                '*.ogg',
                '*.ini',
            ],
            'gui_apps': {
                'game': 'run_game.py',
            },
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
            'platforms': [
                'manylinux1_x86_64',
                'macosx_10_6_x86_64',
            ],
        }
    }
)
