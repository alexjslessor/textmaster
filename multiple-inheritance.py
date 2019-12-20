import re

class RegexMeta:
    # Twitter Mentions and Hashtags
    HTML = r'&(\w+;)'
    MENTIONS = r'@(\w+)'
    HASHTAGS = r'#(\w+)'

class Two:
    # @staticmethod
    def print_two():
        print('Two Func: ')

    # Unbound Method: pg 1002/1594
    def substitute_pattern(pat, replacement, text):
        text = re.sub(pat, replacement, text)
        return str(text)

    def tweet_length(text):
        tweet_length = len(text) - text.count(' ')
        return str(tweet_length)


class Three(RegexMeta, Two):
    
    def __init__(self, data):
        self.data = data

    def __repr__(self):#pg 879/1594
        return '[Three: %s]' % (self.data)

    @classmethod
    def three(cls, data):
        return cls.substitute_pattern(cls.HTML, '', data)


    # @classmethod
    # def print_three(cls, data):
    #     return cls.print_two(data)

if __name__ == "__main__":

    df = ' Stuff Before tag &asdfsdf; <p>Bonch of shit in tag</p> shit after tag'
    b = Three.three(df)
    print(b)
    print(Two.print_two())
    print(Two.tweet_length(df))
    # print(Three.print_three('Stuff'))
    # print(Three.__mro__)
