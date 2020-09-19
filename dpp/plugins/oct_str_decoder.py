from dpp.core.plugin import DecoderPlugin


class Plugin(DecoderPlugin):
    """
    Decodes an octal string sequence to an ascii string.

    Example:

        Input:
            1411421431441451461471501511521531 \
            5415515615716016116216316416516616 \
            7170171172012136260041042247044045 \
            0460570500510750772641400740761740 \
            4005405605507307213704305304705217 \
            6012060061062063064065066067070071

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('OCT (str)', "Thomas Engel", [], context)

    def run(self, text):
        return ''.join([chr(int(chunk, 8)) for chunk in self._chunk_string(text, 3)])

    def _chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]