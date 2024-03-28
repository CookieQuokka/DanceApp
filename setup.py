from setuptools import setup

APP = ['Dance_Local_UI.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['ffmpeg', 'audio_offset_finder', 'moviepy'],
    #'excludes': ['IPython', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'numpy', 'matplotlib'],  # add more as needed
    'includes': ['/opt/homebrew/Cellar/libffi/3.4.4/lib/libffi.8.dylib'],
    #'resources': ['/opt/homebrew/opt/libffi/lib/libffi.8.dylib'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    # more examples below
    # name='your_package_name',
    # version='0.1',
    # description='Your package description',
    # python_requires='>=3.6, <4',
)
