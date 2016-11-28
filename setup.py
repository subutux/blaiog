#!/usr/bin/env python3
from setuptools import setup
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
    packages = ["blaiog"],
    description="A python async blogging platform",
    # long_description=long_descr,
   
    entry_points = {
        "console_scripts": ['blaiog = blaiog.cli:main']
    },
    install_requires= [
    
        "aiohttp",
        "sqlalchemy",
        "aiomysql"
        
    ],
    #tests_require=["requests_mock"],
    test_suite="tests"
    
)
