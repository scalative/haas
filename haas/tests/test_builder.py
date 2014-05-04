import os
import shutil
import tempfile
import textwrap

from ..testing import unittest
from . import builder


class TestBuilder(unittest.TestCase):

    def test_buildilng_fixture(self):
        expected_module = textwrap.dedent("""\
        import unittest.case


        class TestSomething(unittest.case.TestCase):
            def test_method(self):
                self.fail()
    """)
        fixture = builder.Directory(
            'top',
            (
                builder.Package(
                    'first',
                    (
                        builder.Module(
                            'test_something.py',
                            (
                                builder.Class(
                                    'TestSomething',
                                    (
                                        builder.Method(
                                            'test_method',
                                            (
                                                'self.fail()',
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

        tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        try:
            fixture.create(tempdir)
            top_path = os.path.join(tempdir, 'top')
            package_path = os.path.join(top_path, 'first')
            init_path = os.path.join(package_path, '__init__.py')
            module_path = os.path.join(package_path, 'test_something.py')

            self.assertTrue(os.path.isdir(top_path))
            self.assertEqual(len(os.listdir(top_path)), 1)
            self.assertTrue(os.path.isdir(package_path))
            self.assertTrue(os.path.isfile(init_path))
            self.assertTrue(os.path.isfile(module_path))

            with open(init_path) as fh:
                self.assertEqual(fh.read(), '')
            with open(module_path) as fh:
                self.assertMultiLineEqual(fh.read(), expected_module)
        finally:
            shutil.rmtree(tempdir)
