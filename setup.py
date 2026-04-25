import sys
import codecs
import setuptools

from version import __version__ as version


install_requires = [
    'beautifulsoup4>=4.14.3',
    'decorator>=5.2.1',
    'kitchen>=1.2.6',
    'requests>=2.32.5',
    'six>=1.17.0',
    'mailcap-fix>=1.0.1',
]

tests_require = [
    'coveralls',
    'pytest>=9.0.2',
    'coverage',
    'mock',
    'pylint>=4.0.5',
    'vcrpy>=8.1.1',
]

extras_require = {
    'test': tests_require
}

# https://hynek.me/articles/conditional-python-dependencies/
if int(setuptools.__version__.split(".", 1)[0]) < 18:
    assert "bdist_wheel" not in sys.argv
else:
    # Building the bdist_wheel with conditional environment dependencies
    # requires setuptools version > 18. For older setuptools versions this
    # will raise an error.
    pass


def long_description():
    with codecs.open('README.md', encoding='utf8') as f:
        return f.read()


setuptools.setup(
    name='rtv',
    version=version,
    description='A simple terminal viewer for Reddit (Reddit Terminal Viewer)',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/michael-lazar/rtv',
    author='Michael Lazar',
    author_email='lazar.michael22@gmail.com',
    license='MIT',
    keywords='reddit terminal praw curses',
    packages=[
        'rtv',
        'rtv.packages',
        'rtv.packages.praw'
    ],
    package_data={
        'rtv': ['templates/*', 'themes/*'],
        'rtv.packages.praw': ['praw.ini']
    },
    data_files=[("share/man/man1", ["rtv.1"])],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    entry_points={'console_scripts': ['rtv=rtv.__main__:main']},
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console :: Curses',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Terminals',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        ],
)
