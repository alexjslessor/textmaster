from unicodedata import normalize
from datetime import datetime
import string
from textblob import TextBlob
import re
import os
# import spacy
# nlp = spacy.load('en_core_web_sm')
'''
Emojis, theres 2 libraries for this:
https://emojis.readthedocs.io/en/latest/
https://github.com/carpedm20/emoji/
http://www.unicode.org/emoji/charts/full-emoji-list.html
https://www.webfx.com/tools/emoji-cheat-sheet/
Good Articles:
https://towardsdatascience.com/extracting-twitter-data-pre-processing-and-sentiment-analysis-using-python-3-0-7192bd8b47cf
'''

df = '''
310674  2001-09-11 16:12:05     Skytel  [005042977]     A       ALPHA    Phillip.Blakeman@usarec.army.mil|hey| Where are my DONUTS? Mimi
26510   2001-09-11 08:14:59     Skytel  [005206260]     B       ALPHA    IngallsBW@hqmc.usmc.mil|Warning Warning!! DCID EWG MTG This Morning at 0900|I will go unless otherwi    se advised. Bryan (69
28579   2001-09-11 08:24:44     Skytel  [005206261]     B       ALPHA    IngallsBW@hqmc.usmc.mil|FW: Warning Warning!! DCID EWG MTG This Morning at 0900|Ray,be at the CMO Of    fices for the subject meeting. Bry
87201   2001-09-11 10:21:42     Skytel  [004690665]     C       ALPHA    jfraller@usss.treas.gov|(no subject)|Car bomb 15th and F, NW. HIjacked plane enroute DC.
107207  2001-09-11 10:49:59     Skytel  [005201647]     D       ALPHA    jtillman@usss.treas.gov|Bob.....following have been accounted for |BROWN, CASSITY, DADE, GROOVER, KE    NDRICK, KLENNER, LEWIS, WOLFEN, BOWSER, ALLCMCA PERSONNEL --------------554DC0DF3A8507539115AA1F Content-Type: text/x-vcard;
107736  2001-09-11 10:50:44     Skytel  [005055742]     D       ALPHA    wenloe@usss.treas.gov|(no subject)|ALL SFO AGENTS AND SUPERVISORS: CALL INTO THE DUTY DESK IMMEDIATE    LY BY TELEPHONE OR RADIO. 
141555  2001-09-11 11:33:59     Skytel  [005081201]     A       ALPHA    dholland@associates.usss.treas.gov|Urgent!|ALL NEW YORK SECRET SERVICES PERSONNEL -- DO NOT GO INTO     NEW YORK CITY! GO TO THE NEAREST RO! ANY QUESTIONS CALL HEADQUATERS AT406-5988. --------------E9F8E9579C859A005E8589A3 C
1275166  2001-09-11 14:58:57     Skytel  [004690665]     C       ALPHA    jfraller@usss.treas.gov|FYI|USSS K-9 alerted on cars at 10th &and 18th & Penn 
'''

class OtherRegexMeta(object):
    tag2 = r'<.*?>'
    tag3 = r'&nbsp;'
    URL2 = r'(https?://(www\.)?(\w+)(\.\w+))'
    URL3 = r'(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])'
    EMAIL2 = r'(\w+@\w+\.{1}\w+)'

class MetaRegex(object):
    # Twitter Mentions and Hashtags
    HTML = r'&(\w+;)'
    MENTIONS = r'@(\w+)'
    HASHTAGS = r'#(\w+)'

    # Phone Number's
    PHONE_NUMBERS = r'(\d{3}.\d{3}.\d{4}|\d{3}.\d{4})'

    # STRIP HTML TAGS
    HTML_4CHAN_1 = r'&#([0-9]+;)'
    HTML_4CHAN_MAIN = r'&(\w+;|[#0-9]+;)'
    ALL_HTML_TAGS = r'(</?.*?>)'# Every tag enclose in a <>

    #remove special characters, numbers, punctuations
    REMOVE_PAT1 = r"[^a-zA-Z#]"
    REMOVE_PAT2 = r"[^A-Za-z0-9^,!.\/'+-=]"
    REMOVE_PAT2 = r"[^a-zA-Z0-9#@']"

    # White space 2x or more
    STRIP_SPACE = r"\s{2,}"# Whitespace more than 2 chars

    # URL's
    URL1 = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'#url's

    # Datatime
    DATE_TIME = r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})'

    #IP Address
    IP = r'\b(\d{1,4}[.]\d{1,4}[.]\d{1,4}[.]\d{1,4})\b'

    # EMAIL Addresses
    EMAILS = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'

    # Words 1-3 characters
    SHORT_WORDS = r'(\b\w{1,3}\b)'
    NINE_NUMS_4CHAN = r'(\d{9})'

    # Happy Emoticons
    emoticons_happy = set([
        ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
        ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
        '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
        'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
        '<3'
        ])
    # Sad Emoticons
    emoticons_sad = set([
        ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
        ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
        ':c', ':{', '>:\\', ';('
        ])
    emoticons = emoticons_happy.union(emoticons_sad)
    #Emoji patterns
    emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)

class MetaFuncs(object):

    def substitute_pattern(pat, replacement, text):
        text = re.sub(pat, replacement, text)
        return str(text)

    def tweet_length(text):
        tweet_length = len(text) - text.count(' ')
        return str(tweet_length)

    def count_punctuation(text):
        count = sum([1 for char in text if char in string.punctuation])
        return str(round(count/(len(text) - text.count(" ")), 3)*100)

    def findall_pattern(pat, text):
        '''Uses re.findall

        :text: list, pandas DataFrame, ndarray
        '''
        pattern = re.findall(pat, text)
        return str(pattern)

    def count_emojis(text: str):
        '''
        import emojis
        '''
        emoj = emojis.count(text)
        return emoj

    def count_unique_emojis(text: str, unique=True):
        '''
        https://emojis.readthedocs.io/en/latest/api.html#sample-code
        import emojis
        '''
        emoj = emojis.count(text)
        return emoj

    def decode_emojis(text: str):
        '''
        https://emojis.readthedocs.io/en/latest/api.html#sample-code
        import emojis
        '''
        emoj = emojis.decode(text)

    def clean_tweets(tweet):
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(tweet)
        #after tweepy preprocessing the colon symbol left remain after      #removing mentions
        tweet = re.sub(r':', '', tweet)
        tweet = re.sub(r'‚Ä¶', '', tweet)
        #replace consecutive non-ASCII characters with a space
        tweet = re.sub(r'[^\x00-\x7F]+',' ', tweet)
        #remove emojis from tweet
        tweet = emoji_pattern.sub(r'', tweet)
        #filter using NLTK library append it to a string
        filtered_tweet = [w for w in word_tokens if not w in stop_words]
        filtered_tweet = []
        #looping through conditions
        for w in word_tokens:
        #check tokens against stop words , emoticons and punctuations
            if w not in stop_words and w not in emoticons and w not in string.punctuation:
                filtered_tweet.append(w)
        return ' '.join(filtered_tweet)
        #print(word_tokens)
        #print(filtered_sentence)return tweet

# https://towardsdatascience.com/almost-real-time-twitter-sentiment-analysis-with-tweep-vader-f88ed5b93b1c
    def remove_pattern(input_txt, pattern):
        r = re.findall(pattern, input_txt)
        for i in r:
            input_txt = re.sub(i, '', input_txt)        
        return input_txt
# https://towardsdatascience.com/almost-real-time-twitter-sentiment-analysis-with-tweep-vader-f88ed5b93b1c
    def clean_tweets(lst):
        # remove twitter Return handles (RT @xxx:)
        lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")
        # remove twitter handles (@xxx)
        lst = np.vectorize(remove_pattern)(lst, "@[\w]*")
        # remove URL links (httpxxx)
        lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")
        # remove special characters, numbers, punctuations (except for #)
        lst = np.core.defchararray.replace(lst, "[^a-zA-Z#]", " ")
        return lst

    def textblob_sentiment_raw(tweets):
        analysis = TextBlob(tweets)
        sent = analysis.sentiment.polarity
        return str(sent)

    def vader_sentiment_analyzer_scores(text):
        score = analyser.polarity_scores(text)
        lb = score['compound']
        if lb >= 0.05:
            return 1
        elif (lb > -0.05) and (lb < 0.05):
            return 0
        else:
            return -1

    def google_translate_sentiment_analyzer_scores(text, engl=True):
        if engl:
            trans = text
        else:
            trans = translator.translate(text).text
        score = analyser.polarity_scores(trans)
        lb = score['compound']
        if lb >= 0.05:
            return 1
        elif (lb > -0.05) and (lb < 0.05):
            return 0
        else:
            return -1

class ForChanText(MetaRegex, MetaFuncs):

    def __init__(self, data):
        self.data = data

    def __repr__(self):#pg 879/1594
        return '[ForChanText: %s]' % (self.data)

    @classmethod
    def extract_url(cls, data):
        return cls.substitute_pattern(cls.ALL_HTML_TAGS, '', data)
        
    @classmethod
    def strip_html(cls, data):
        data = substitute_pattern(cls.ALL_TAGS, ' ', str(data))
        data = substitute_pattern(cls.HTML_4CHAN_MAIN, ' ', data)
        data = substitute_pattern(cls.NINE_NUMS_4CHAN, ' ', data)
        data = substitute_pattern(cls.STRIP_SPACE, '', data)
        data = data.strip()
        return data

    @classmethod
    def textblob_sentiment_col(cls, data):
        data = substitute_pattern(cls.ALL_TAGS, ' ', str(data))
        data = substitute_pattern(cls.HTML_4CHAN_MAIN, ' ', data)
        data = substitute_pattern(cls.NINE_NUMS_4CHAN, ' ', data)
        data = substitute_pattern(cls.URL1, ' ', data)
        data = substitute_pattern(cls.STRIP_SPACE, '', data)
        data = data.strip()
        data = data.lower()
        data = cls.textblob_sentiment_raw(data)
        return data


# class TwitterText(RegexMeta):

#     def __init__(self, twitter_stream: str):
#         self.twitter_stream = twitter_stream

#     def __repr__(self):
#         return f'TPipe: {self.twitter_stream!r}'

#     @classmethod
#     def process_text(cls, stream):
#         return cls.normalize_text(stream)
#         # cls.strip_html(stream)

#     @staticmethod
#     def normalize_text(text):
#         # text = str(text).encode('utf-8').decode('utf-8')
#         # text = normalize('NFKD', text)
#         text = text.strip()
#         text = text.lower()
#         return text

#     @staticmethod
#     def strip_html(text):
#         HTML = r'&(\w+;)'
#         text = re.sub(HTML, '', text)
#         return str(text)

if __name__ == "__main__":

    df = 'www.textstuff.com ......... <p class="dasfdawsfa"> fadfsdfsgdshsfdghsdf </p>]'
    t1 = ForChanText.extract_url(df)
    # t1 = t1.tweet_length(df)
    print(t1)





















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


# def sub_html(pat, replacement, text):
#     text = re.sub(pat, replacement, text)
#     text = text.strip()
#     text = text.lower()
#     STRIP_SPACE = "\s{2,}"
#     text = re.sub(STRIP_SPACE, '', text)
#     return str(text)


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


