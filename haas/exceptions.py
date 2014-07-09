class HaasException(Exception):
    pass


class DotInModuleNameError(HaasException):
    pass


class PluginError(HaasException):
    pass
