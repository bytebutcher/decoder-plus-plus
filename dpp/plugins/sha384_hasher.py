from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using SHA384.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            4e6b190af95ffaae6b963ec8cf4138aabe0f33b088164afe \\
            c358f47299ca53885a6e086b74ef7981695e9d55bb809abc
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA384', "Thomas Engel", ["hashlib"], context)

    def run(self, text):
        import hashlib
        return hashlib.sha384(text.encode('utf-8', errors='surrogateescape')).hexdigest()
