from haas.utils import uncamelcase
from .i_plugin import IPlugin


class BasePlugin(IPlugin):

    name = None
    enabled = False
    enabling_option = None

    def __init__(self, name=None):
        if name is None:
            name = uncamelcase(type(self).__name__, sep='-')
        self.name = name
        self.enabling_option = 'with_{0}'.format(name.replace('-', '_'))

    def add_parser_arguments(self, parser):
        parser.add_argument('--with-{0}'.format(self.name),
                            action='store_true',
                            dest=self.enabling_option)

    def configure(self, args):
        if getattr(args, self.enabling_option, False):
            self.enabled = True
