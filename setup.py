#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup


setup(
    name='xivo_popc_stats',
    version='0.1',

    description='XiVO popc stats',

    author='Sylvain Boily',
    author_email='sboily@avencall.com',

    url='https://github.com/sboily/xivo-popc-stats',

    packages=find_packages(),
    zip_safe = False,
    scripts=['bin/xivo-popc-stats', 'bin/xivo-popc-stats-cli'],
    data_files=[('/etc/xivo-popc-stats', ['etc/xivo-popc-stats/config.yml'])],
    entry_points={
        'xivo_confd.plugins': [
            'popcstats = popc_stats.plugins.popcstats:XiVOPopcStats',
        ],
    }

)

