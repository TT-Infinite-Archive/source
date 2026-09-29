from panda3d.core import ConfigVariableString

# What live.prc carries until a build rewrites it:
PLACEHOLDER = 'BUILD_VERSION'


def protocol():
    return ConfigVariableString('server-version', 'dev').getValue()


def build():
    value = ConfigVariableString('build-version', '').getValue()

    if not value or value == PLACEHOLDER:
        return protocol()

    return value
