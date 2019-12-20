class RegexMeta:
    # Twitter Mentions and Hashtags
    HTML = r'&(\w+;)'
    MENTIONS = r'@(\w+)'
    HASHTAGS = r'#(\w+)'


class Two(RegexMeta):
    TWO = 'This is Two'

    # @staticmethod
    def print_two():
        print('Two Func: ', )


class Three(Two):
    
    def __init__(self, data):
        self.data = data

    @classmethod
    def print_three(cls, data):
        return cls.print_two(data)