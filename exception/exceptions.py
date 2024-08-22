from core.enums import PLATFORM_TYPE


class NotSupportedPlatformTypeException(Exception):

    def __init__(self, platform_type: PLATFORM_TYPE):
        super().__init__(f"PLATFORM_TYPE {platform_type} is not supported")
