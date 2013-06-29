import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'formencode',
    'pastescript',
    'pastedeploy',
    'mako',
    'babel',
    'lingua',
    'beaker',
    'paste',
    'simplejson',
    'dnspython',
    'pyDNS',
    'turbomail',
    'uuid',
    'pyramid_beaker',
    'pyramid_exclog',
    'beautifulsoup',
    'unidecode',
    "dogpile.cache>=0.4.1",
    "redis",
    "httplib2",
    "markdown",
    "smartypants",
    'hnc>=0.0.8dev'
    ]

setup(name='ufostart',
      version='0.0',
      description='ufostart',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="ufostart",
      message_extractors = {
            'ufostart': [
                ('**.py', 'lingua_python', None),
                ('website/templates/**.html', 'mako', {'input_encoding': 'utf-8'}),
                ('website/templates/**.js', 'mako', {'input_encoding': 'utf-8'})
                ]
             },
      entry_points="""\
      [paste.app_factory]
      main = ufostart:main
      """,
      )
