from unicodedata import normalize
# from datetime import datetime
import string
from textblob import TextBlob
import re
import os
# import spacy
# nlp = spacy.load('en_core_web_sm')

class RegexMeta:
    # Twitter Mentions and Hashtags
    HTML = r'&(\w+;)'
    MENTIONS = r'@(\w+)'
    HASHTAGS = r'#(\w+)'
    # Phone Number's
    PHONE_NUMBERS = r'(\d{3}.\d{3}.\d{4}|\d{3}.\d{4})'
    # STRIP HTML TAGS
    HTML_4CHAN_1 = r'&#([0-9]+;)'
    HTML_4CHAN_MAIN = r'&(\w+;|[#0-9]+;)'
    ALL_TAGS = r'(</?.*?>)'# Every tag enclose in a <>
    # tag2 = r'<.*?>'
    # tag3 = r'&nbsp;'
    #remove special characters, numbers, punctuations
    REMOVE_PAT1 = r"[^a-zA-Z#]"
    REMOVE_PAT2 = r"[^A-Za-z0-9^,!.\/'+-=]"
    REMOVE_PAT2 = r"[^a-zA-Z0-9#@']"
    # White space 2x or more
    STRIP_SPACE = r"\s{2,}"# Whitespace more than 2 chars
    # URL's
    URL1 = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'#url's
    URL2 = r'(https?://(www\.)?(\w+)(\.\w+))'
    URL3 = r'(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])'
    # Datatime
    DATE_TIME = r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})'
    #IP Address
    IP = r'\b(\d{1,4}[.]\d{1,4}[.]\d{1,4}[.]\d{1,4})\b'
    # EMAIL Addresses
    EMAILS = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
    # Words 1-3 characters
    SHORT_WORDS = r'(\b\w{1,3}\b)'
    NINE_NUMS_4CHAN = r'(\d{9})'

class ForChanText(RegexMeta):

    def __init__(self, data):
        self.data = data

    @classmethod
    def extract_url(cls, data):
        data = re.findall(cls.URL1, str(data))
        return str(data)

    @classmethod
    def strip_html(cls, data):
        data = re.sub(cls.ALL_TAGS, ' ', str(data))
        data = re.sub(cls.HTML_4CHAN_MAIN, ' ', data)
        data = re.sub(cls.NINE_NUMS_4CHAN, ' ', data)
        data = re.sub(cls.STRIP_SPACE, '', data)
        data = data.strip()
        # data = re.sub(r'</?.*?>', ' ', data)
        # data = re.sub(r'&(\w+;|[#0-9]+;)', ' ', data)
        # data = re.sub(r'(\d{9})', ' ', data)
        # data = re.sub(r'\s{2,}', '', data)
        return data

    @classmethod
    def textblob_sentiment(cls, data):
        data = re.sub(cls.ALL_TAGS, ' ', str(data))
        data = re.sub(cls.HTML_4CHAN_MAIN, ' ', data)
        data = re.sub(cls.NINE_NUMS_4CHAN, ' ', data)
        data = re.sub(cls.URL1, ' ', data)
        data = re.sub(cls.STRIP_SPACE, '', data)
        data = data.strip()
        data = data.lower()
        data = cls._textblob_sentiment_raw(data)
        return data

    @staticmethod
    def _textblob_sentiment(data):
        analysis = TextBlob(data)
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1
    
    @staticmethod
    def _textblob_sentiment_raw(data):
        analysis = TextBlob(data)
        sent = analysis.sentiment.polarity
        return str(sent)

######################
# class Spipe:

#     def __init__(self, twitter_stream):
#         self.twitter_stream = twitter_stream

#     def __repr__(self):
#         return f'TPipe: {self.twitter_stream!r}'

#     @classmethod
#     def spacy_stream_pipeline(cls, stream):
#         cls.stage1(stream)


#     @staticmethod
#     def stage1(text):
#         for doc in nlp.pipe(text):
#             print([(ent.text, ent.label_) for ent in doc.ents])


class TwitterText(RegexMeta):

    HTML = r'&(\w+;)'
    MENTIONS = r'@(\w+)'
    HASHTAGS = r'#(\w+)'
    # remove special characters, numbers, punctuations
    REMOVE_PAT1 = r"[^a-zA-Z#]"
    REMOVE_PAT2 = r"[^A-Za-z0-9^,!.\/'+-=]"
    REMOVE_PAT3 = r"[^a-zA-Z0-9#@']"
    # Strip Whitespace more than 2 characters
    STRIP_SPACE = "\s{2,}"

    def __init__(self, twitter_stream: str):
        self.twitter_stream = twitter_stream

    def __repr__(self):
        return f'TPipe: {self.twitter_stream!r}'

    @classmethod
    def process_text(cls, stream):
        return cls.normalize_text(stream)
        # cls.strip_html(stream)

    @staticmethod
    def normalize_text(text):
        # text = str(text).encode('utf-8').decode('utf-8')
        # text = normalize('NFKD', text)
        text = text.strip()
        text = text.lower()
        return text

    @staticmethod
    def strip_html(text):
        HTML = r'&(\w+;)'
        text = re.sub(HTML, '', text)
        return str(text)

def substitute_pattern(pat, replacement, text):
    text = re.sub(pat, replacement, text)
    return str(text)


def textblob_sentiment_raw(tweets):
    analysis = TextBlob(tweets)
    sent = analysis.sentiment.polarity
    return str(sent)


def tweet_length(text):
    tweet_length = len(text) - text.count(' ')
    return str(tweet_length)


def count_punc(text):
    count = sum([1 for char in text if char in string.punctuation])
    return str(round(count/(len(text) - text.count(" ")), 3)*100)


def findall_pattern(pat, text):
    '''Uses re.findall

    :text: list, pandas DataFrame, ndarray
    '''
    pattern = re.findall(pat, text)
    return str(pattern)

# class TwitterPostprocessing(object):

#     # def __init__(self, df):
#     #     df.set_index('idstr', inplace=True)
#     #     df['unix'] = pd.to_datetime(df['unix'])
#     #     df.insert(1, 'date', df['unix'].dt.date)
#     #     df.insert(2, 'time', df['unix'].dt.time)
#     #     df.drop(['unix'], axis=1, inplace=True)
#     #     df['hashtags'] = df['hashtags'].str.replace('[', '').str.replace(']', '')
#     #     df['mentions'] = df['mentions'].str.replace('[', '').str.replace(']', '')
#     #     self.df = df
#     def tag_count(self, series):
#         series = series.str.replace('[', '').str.replace(']', '')
#         all_words = []
#         for line in list(series):
#             words = line.split(', ')
#             for word in words:
#                 all_words.append(word)
#         counter = sorted(Counter(all_words).elements())
#         return pd.Series(counter)

# HTML = r'&(\w+;)'
# MENTIONS = r'@(\w+)'
# HASHTAGS = r'#(\w+)'

# def sub_html(pat, replacement, text):
#     text = re.sub(pat, replacement, text)
#     text = text.strip()
#     text = text.lower()
#     STRIP_SPACE = "\s{2,}"
#     text = re.sub(STRIP_SPACE, '', text)
#     return str(text)

# def findall_pattern(pat, text):
#     '''Uses re.findall
#     :text: list, pandas DataFrame, ndarray
#     '''
#     pattern = re.findall(pat, text)
#     return str(pattern)

# def tweet_length(text):
#     tweet_length = len(text) - text.count(' ')
#     return str(tweet_length)


# def count_punc(text):
#     count = sum([1 for char in text if char in string.punctuation])
#     return str(round(count/(len(text) - text.count(" ")), 3)*100)

# def textblob_sentiment_raw(tweets):
#     REMOVE_PAT2 = r"[%$*;\"_(),!.\/'+-=]"
#     tweets = re.sub(REMOVE_PAT2, '', tweets)
#     STRIP_SPACE = "\s{2,}"
#     tweets = re.sub(STRIP_SPACE, '', tweets)
#     analysis = TextBlob(tweets)
#     sent = analysis.sentiment.polarity
#     return str(sent)

# def preprocessed_tweets(tweets):
#     # tweets = tweets.strip()
#     tweets = tweets.lower()
#     tweets = tweets.replace(r'#(\w+)', ' ')
#     tweets = tweets.replace(r'&(\w+)', ' ')
#     tweets = tweets.replace(r'@(\w+)', ' ')
#     tweets = tweets.replace(r'\s{2,}', ' ')
#     # stopwords = nltk.corpus.stopwords.words('english')
#     text = "".join([word for word in tweets if word not in string.punctuation])
#     # tokens = re.split(r'\W+', text)
#     # text = [word for word in tokens if word not in stopwords]
#     analysis = TextBlob(text)
#     sent = analysis.sentiment.polarity
#     return pd.Series(sent)
