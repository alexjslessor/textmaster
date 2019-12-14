# from pandas.io.json import json_normalize
import requests
# import pandas as pd
from contextlib import contextmanager
from datetime import datetime as dt
import re
from sqlite3 import connect, ProgrammingError
from textblob import TextBlob
# pd.set_option('display.width', 700)
# pd.set_option('display.max_columns', 6000)
# pd.set_option('display.max_colwidth', 600)
# pd.set_option('display.max_rows', 600)

# def print_full(x):
#     pd.set_option('display.max_rows', len(x))
#     pd.set_option('display.max_columns', None)
#     pd.set_option('display.width', 2000)
#     pd.set_option('display.float_format', '{:20,.2f}'.format)
#     pd.set_option('display.max_colwidth', -1)
#     print(x)
#     pd.reset_option('display.max_rows')
#     pd.reset_option('display.max_columns')
#     pd.reset_option('display.width')
#     pd.reset_option('display.float_format')
#     pd.reset_option('display.max_colwidth')

r = requests.get('https://a.4cdn.org/pol/catalog.json')
r = r.json()

db_name = '/home/hauwei/Dropbox/alexjslessor-blogposts/api-4chan/chan_gen3.db'

table_name_comments = 'comments_html1'
column_names_comments = '(resto_com, com_com, now_com, time_com, filename_com, url_com, sent_com)'
column_dtype_comments = '(resto_com, com_com text, now_com text, time_com integer, filename_com text, url_com text, sent_com real)'
val_comms = ', ?' * 6
values_comments = f'(?{val_comms})'
# values_comments = '(?, ?, ?, ?, ?, ?)'

table_name_threads = 'threads_html1'
column_names_threads = '(no, now, time, my_time, com, name, trip, ids, capcode, filename, resto, semantic_url, replies, images, url, sent)'
column_dtype_threads = '(no integer primary key, now text, time text, my_time text, com text, name text, trip text, ids text, capcode text, filename text, resto text, semantic_url text, replies text, images text, url text, sent real)'
val_threads = ', ?' * 15
values_threads = f'(?{val_threads})'
# values_threads = '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

'''
- pg 61-62 good idea to mark at least 1x primary key as not null
- pg 69
- 109 one or more primary keys that have unique values
- pg 113 integer primary key adds significant performance boost.
'''
class ChanSqlite:

    def __init__(self, column_dtype, table_name, column_names, values, db_name):
        self.column_dtype = column_dtype
        self.table_name = table_name
        self.column_names = column_names
        self.values = values
        self.db_name = db_name

    @contextmanager
    def _temptable(self, cur, *args):
        cur.execute(f'''create table if not exists {self.table_name} {self.column_dtype}''')
        try:
            yield
        except ProgrammingError as e:
            print(e)
        finally:
            print('Tare down action')

    def sqlite_db(self, *args):
        with connect(self.db_name, check_same_thread=False, isolation_level=None) as conn:
            cur = conn.cursor()
            with self._temptable(cur):
                cur.execute(f'''replace into {self.table_name} {self.column_names} values{self.values}''', (args))
                for row in cur.execute(f'''select * from {self.table_name}'''):
                    print(row)


thread_table = ChanSqlite(column_dtype_threads, table_name_threads, column_names_threads, values_threads, db_name)
comment_table = ChanSqlite(column_dtype_comments, table_name_comments, column_names_comments, values_comments, db_name)

def get_threads(key: str, default='NaN'):
    return threads.get(key, default)

class TextMaster:
    # Twitter Mentions and Hashtags
    MENTIONS = r'@(\w+)'
    HASHTAGS = r'#(\w+)'
    # Phone Number's
    PHONE_NUMBERS = r'(\d{3}.\d{3}.\d{4}|\d{3}.\d{4})'
    # STRIP HTML TAGS
    HTML = r'&(\w+;)'
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

'''
The sentiment property returns a namedtuple of the form Sentiment(polarity, subjectivity). The
polarity score is a float within the range [-1.0, 1.0]. The subjectivity is a float within the range [0.0, 1.0] where 0.0 is
very objective and 1.0 is very subjective
'''
# def gen_chan():
#     for idx, i in enumerate(r):
#         for x in r[idx]['threads']:
#             yield x

# for threads in gen_chan():
#     no = get_threads('no')
#     now = get_threads('now')
#     time = get_threads('time')
#     my_time = dt.today()
#     com = TextMaster.strip_html(get_threads('com'))
#     name = get_threads('name')
#     trip = get_threads('trip')
#     ids = get_threads('id')
#     capcode = get_threads('capcode')
#     filename = get_threads('filename') + get_threads('ext')
#     resto = get_threads('resto')
#     semantic_url = get_threads('semantic_url')
#     replies = get_threads('replies')
#     images = get_threads('images')
#     url = TextMaster.extract_url(get_threads('com'))
#     sent = TextMaster.textblob_sentiment(get_threads('com'))
#     if 'last_replies' in threads:
#         for comment in threads['last_replies']:
#             com_com = TextMaster.strip_html(comment.get('com', 'NaN'))
#             resto_com = comment.get('resto', 'NaN')
#             now_com = comment.get('now', 'NaN')
#             time_com = comment.get('time', 'NaN')
#             filename_com = comment.get('filename', 'NaN') + comment.get('ext', 'NaN')
#             url_com = TextMaster.extract_url(comment.get('com'))
#             sent_com = TextMaster.textblob_sentiment(comment.get('com'))

#             comment_table.sqlite_db(resto_com, com_com, now_com, time_com, filename_com, url_com, sent_com)

#     thread_table.sqlite_db(no, now, time, my_time, com, name, trip, ids, capcode, filename, resto, semantic_url, replies, images, url, sent)
