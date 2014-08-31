# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
import os
import sys
import subprocess

from setuptools import setup


MAJOR = 0
MINOR = 5
MICRO = 0

IS_RELEASED = False

VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env,
        ).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"

    return git_revision


def write_version_py(filename='haas/_version.py'):
    template = """\
# THIS FILE IS GENERATED FROM SETUP.PY
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

if not is_released:
    version = full_version
"""
    fullversion = VERSION
    if os.path.exists('.git'):
        git_rev = git_version()
    elif os.path.exists('haas/_version.py'):
        # must be a source distribution, use existing version file
        try:
            from haas._version import git_revision as git_rev
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "haas/_version.py and the build "
                              "directory before building.")
    else:
        git_rev = "Unknown"

    if not IS_RELEASED:
        fullversion += '.dev1-' + git_rev[:7]

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))


if __name__ == "__main__":
    install_requires = ['six']
    if sys.version_info < (2, 7):
        install_requires += ['unittest2', 'argparse']

    write_version_py()
    from haas import __version__

    with open('README.rst') as fh:
        long_description = fh.read()

    setup(
        name='haas',
        version=__version__,
        url='https://github.com/sjagoe/haas',
        author='Simon Jagoe',
        author_email='simon@simonjagoe.com',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: OS Independent',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Programming Language :: Python',
            'Topic :: Software Development',
            'Topic :: Software Development :: Testing',
        ],
        description='Extensible Python Test Runner',
        long_description=long_description,
        license='BSD',
        packages=['haas'],
        install_requires=install_requires,
        entry_points={
            'console_scripts': [
                'haas=haas.main:main',
            ],
        },
    )
