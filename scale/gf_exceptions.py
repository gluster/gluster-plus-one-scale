"""This module provide custome excception to be used."""


class VolumeNotHealthy(Exception):
    """User defind exception.

    This exception could be used when a gluster volume
    command execution fails.
    """

    def __init__(self, message):
        self.message = message


class GfCommandFailed(Exception):
    """User defind exception.

    This exception could be used when a gluster volume
    command execution fails.
    """

    def __init__(self, message):
        self.message = message
