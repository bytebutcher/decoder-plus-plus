import re

from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE32', "Thomas Engel", ["base64"])

    def run(self, text):
        import base64
        return base64.b32decode(text.encode('utf-8')).decode('utf-8')

    def can_be_decoded(self, input):
        if len(input) % 4 == 0:
            if re.search(r'^(?:[A-Z2-7]{8})*(?:[A-Z2-7]{2}={6}|[A-Z2-7]{4}={4}|[A-Z2-7]{5}={3}|[A-Z2-7]{7}=)?$', input):
                return True
        return False
