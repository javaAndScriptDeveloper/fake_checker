from core.enums import PLATFORM_TYPE


class ProduceDataMessagesCommand:

    def __init__(self):
        self.sources_to_listen = []
        self.sources_to_fetch = []
        self.post_extract_func = None
        self.platform_type = None

class DataMessage:

    def __init__(self):
        self.source_external_id = None
        self.platform_type = None
        self.text_content = None