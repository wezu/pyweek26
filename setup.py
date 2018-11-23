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
            'log_filename': '$USER_APPDATA/flowrock.log',
            'log_append': False,
            'gui_apps': {
                'game': 'run_game.py',
            },
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'p3fmod_audio',
            ],
            'platforms': [
                'win_amd64',
            ],
        }
    }
)
