
# coding: utf-8

# In[4]:

# import modules & set up logging (only works in terminal)
import gensim, logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# In[1]:

import os
import zipfile
import json
import regex
from string import punctuation
import gensim
import pandas as pd
import pickle


# ## Load the zipped line-for-line tweet files

# In[2]:

infile = "/Users/mos/twitterdb/usertweets_160605.zip"
myzip = zipfile.ZipFile(infile)
namelist = myzip.namelist()


# How many files do we have?

# In[3]:

len(namelist)


# Let's look at the first the names in the list

# In[4]:

namelist[:10]


# The first name is the name of the folder, so we remove it.
# For 2015 tweets: the first 6 files are corrupt

# In[5]:

namelist.remove("usertweets/")


# In[6]:

namelist[:10]


# ## Parse out the tweet texts

# In[12]:

line_patt = regex.compile(r"(?P<datetime>\d+-\d+-\d+ \d+:\d+:\d+) (?P<id_str>\d+) (?P<text>.*)")


# In[13]:

a_line = "2012-12-03 09:41:06 275535121732468736 Egentligen älskar du inte mig För jag älskar ingen alls Sånt där är slöseri med tid"


# In[14]:

match = line_patt.search(a_line)
print(match.group("text"))


# Let's work with only three files at first and make it work

# In[7]:

def preprocess_text(text):
    
    no_multispace = " ".join(text.split())
    no_linebreaks = regex.sub(r"[\r\n]","",no_multispace)
    no_hashtags = regex.sub(r"#\w+","",no_linebreaks)
    no_mentions = regex.sub(r"@\w+","",no_hashtags)
    
    url_pattern = url_pattern = "https?\://[\.\/\w\d\?…]+" #very hackish but good enough
    no_urls = regex.sub(url_pattern, " ", no_mentions)
    
    my_punctuation = """!"#$%&'()*+,./:;<=>?@[\]^_`{|}~""" # removed '-' from string.punctuation
    chars = []
    for index, char in enumerate(no_urls):
        if index == 0 and char.isalpha:
            char = char.lower()
            if char in my_punctuation:
                chars.append(" {} ".format(char))
            else:
                chars.append(char)
        else:
            if char in my_punctuation:
                chars.append(" {} ".format(char))
            else:
                chars.append(char)
            
    clean_text = "".join(chars)
    
    #stopwords = set([word.rstrip() for word in open("./top10K_stopwords").readlines()])
    #no_stops = [word for word in clean_text.split() if word not in stopwords]
    
    #return " ".join(no_stops)
    return clean_text


# In[8]:

class awsZipfileUserTweetsIterator(object):
    def __init__(self, namelist):
        self.namelist = namelist
        line_patt = regex.compile(r"(?P<datetime>\d+-\d+-\d+ \d+:\d+:\d+) (?P<id_str>\d+) (?P<text>.*)")
        
    def __iter__(self):    
        for filename in namelist:
            try:
                with myzip.open(filename) as userfile: 
                    fileinfo = myzip.getinfo(filename)
                    if fileinfo.file_size > 1000:
                        file = userfile.read().decode("utf-8")
                        tweets_list = json.loads(file)
                        if len(tweets_list) >= 500:
                            for tweet in tweets_list:
                                screen_name = tweet["screen_name"]
                                if "expanded_url" in tweet.keys():
                                    expanded_url = tweet["expanded_url"]
                                else:
                                    continue
                    
                                if not regex.match(r"RT", tweet["text"]):
                                    text = tweet["text"]
                                    
                                    if len(text.split()) >= 3:
                                        clean_text = preprocess_text(text)
                                        yield clean_text.split()
                                #print(clean_text)
                                    else: # fewer than 3 words in tweet
                                        continue
                                else: # Begins with 'RT'
                                    continue
                            #print("Retweet: {}".format(tweet["text"]))
                        #print("user: {} text: {}".format(screen_name, text))
                        else: # len(tweets_list) too small
                            continue
                    else: # file_size to small
                        continue
            except FileNotFoundError as e:
                print("{}".format(e))


# In[9]:

sentences = awsZipfileUserTweetsIterator(namelist)


# In[10]:

#bigrams = gensim.models.Phrases(sentences)
#pickle.dump(bigrams, open("./bigrams.pickle","wb"))
#print("Finished creating and storing bigrams.")


# In[12]:

#trigrams = gensim.models.Phrases(bigrams[sentences])
#pickle.dump(trigrams, open("./trigrams.pickle","wb"))
#print("Finished creating and storing trigrams.")


# In[ ]:

bigrams = pickle.load(open("./bigrams.pickle","rb"))
trigrams = pickle.load(open("./trigrams.pickle","rb"))


# In[16]:

model = gensim.models.Word2Vec(trigrams[bigrams[sentences]], min_count=30, workers=4, size=150)
model.save('model_ngrams_150_mincount_30')
print("Finished training! Stored the word2vec model as 'model_ngrams_150_mincount_30_no_stops")


# In[ ]:



