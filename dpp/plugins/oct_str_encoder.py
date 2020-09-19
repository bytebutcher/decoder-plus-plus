from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes an ascii string to an octal string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            1411421431441451461471501511521531 \
            5415515615716016116216316416516616 \
            7170171172012136260041042247044045 \
            0460570500510750772641400740761740 \
            4005405605507307213704305304705217 \
            6012060061062063064065066067070071

    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('OCT (str)', "Thomas Engel", [], context)

    def run(self, text):
        return ''.join(['{:03o}'.format(ord(char)) for char in text])
