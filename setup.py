# -*- coding: utf-8 -*-

"""
	Adapted from https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
"""

from setuptools import setup


setup(
	name='django_minimal_log',
	description='Simple logging functionality for Django',
	long_description='',
	url='https://github.com/mverleg/django_minimal_log',
	author='Mark V',
	maintainer='(the author)',
	author_email='mdilligaf@gmail.com',
	license='LICENSE.txt',
	keywords=['django', 'logging',],
	version='0.6.0',
	packages=[
		'minimal_log_host',
		'minimal_logger',
		'minimal_log_host.migrations',
	],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		'django',
		'requests',
		'django_ipware',
	],
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Topic :: System :: Logging',
		'Topic :: System :: Monitoring',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: Implementation :: PyPy',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
)


