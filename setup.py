from setuptools import setup
setup(
	name = 'pytermfx',
	packages = ['pytermfx'],
	version = '0.1.0',
	description = 'Terminal interaction and formatting for Python without curses',
	author = 'Logan Zartman',
	author_email = 'logan.zartman@utexas.edu',
	url = 'https://github.com/loganzartman/pytermfx',
	keywords = ['curses', 'terminal', 'colors', 'ansi', 'escapes'],
	classifiers = [
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3'
	],
	python_requires = ">=3"
)