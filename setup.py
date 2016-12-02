#!/usr/bin/env python3
from setuptools import setup, find_packages
import re
 
 
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('blaiog/blaiog.py').read(),
    re.M
    ).group(1)
 
 
# with open("README.md", "rb") as f:
#     long_descr = f.read().decode("utf-8")
 
 
setup(
    name="blaiog",
    version=version,
    packages = ["blaiog","blaiog.web","blaiog.db","blaiog.cli"],
    description="A python async blogging platform",
    # long_description=long_descr,
   
    entry_points = {
        "console_scripts": ['blaiog = blaiog.cli:main']
    },
    install_requires= [
        "pyyaml",
        "passlib",
        "aiohttp",
        "aiohttp-jinja2",
        "aiohttp_session[secure]",
        "aiohttp_security",
        "sqlalchemy",
        "aiomysql",
	"markdown2",
	"pygments"
        
    ],
    #tests_require=["requests_mock"],
    test_suite="tests",
    package_data={ 'blaiog': [
        'web/themes/default/static/*.css',
        'web/themes/default/templates/*.html'
        ]
    }
)
