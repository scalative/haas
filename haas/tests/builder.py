# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import abc
import os
import textwrap

from six import add_metaclass

from ..testing import unittest


@add_metaclass(abc.ABCMeta)
class Importable(object):

    def __init__(self, name, contents=()):
        self.name = name
        self.contents = contents

    @abc.abstractmethod
    def create(self, parent_importable):
        """Create the importable object.

        """


class Directory(Importable):

    def create(self, parent_importable):
        assert os.path.isdir(parent_importable)
        package_directory = os.path.join(parent_importable, self.name)
        os.makedirs(package_directory)
        for item in self.contents:
            item.create(package_directory)


class Package(Directory):

    def __init__(self, name, contents=()):
        contents = (Module('__init__.py'),) + tuple(contents)
        super(Package, self).__init__(name, contents)


class Module(Importable):

    def create(self, parent_importable):
        assert os.path.isdir(parent_importable)
        module_path = os.path.join(parent_importable, self.name)
        with open(module_path, 'w') as module:
            for item in self.contents:
                item.create(module)


class Class(Importable):

    def __init__(self, name, contents=(), bases=(unittest.TestCase,)):
        super(Class, self).__init__(name, contents)
        self.bases = bases

    def _format_base_imports(self):
        imports = ['import {0}'.format(base.__module__) for base in self.bases]
        return '\n'.join(imports)

    def _format_bases(self):
        bases = ['{0}.{1}'.format(base.__module__, base.__name__)
                 for base in self.bases]
        return ', '.join(bases)

    def _format_class_header(self):
        template = textwrap.dedent("""\
        {imports}


        class {classname}({bases}):
        """)
        return template.format(
            imports=self._format_base_imports(),
            classname=self.name,
            bases=self._format_bases(),
        )

    def create(self, module_fh):
        module_fh.write(self._format_class_header())
        if len(self.contents) == 0:
            module_fh.write('    pass\n')
        else:
            for item in self.contents:
                item.create(module_fh)
            module_fh.write('\n')


class Method(Importable):

    def create(self, module_fh):
        module_fh.write('    def {0}(self):\n'.format(self.name))
        if len(self.contents) == 0:
            module_fh.write('        pass\n')
        else:
            module_fh.writelines('        {0}'.format(line)
                                 for line in self.contents)


class RawText(Importable):

    def __init__(self, name, contents=''):
        self.name = name
        self.contents = contents

    def create(self, module_fh):
        module_fh.write(self.contents)
        module_fh.write('\n')
