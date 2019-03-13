import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
import seaborn as sns
from math import floor
from tqdm import tqdm_notebook as tqdm
import pandas as pd

def get_songs_albums_artists(df):
    n_songs = df.shape[0]
    n_albums = df.release_id.nunique()
    n_artists = df.artist_id.nunique()
    return n_songs, n_albums, n_artists
##########################################################################################################################
# Templates
##########################################################################################################################
def template_vis():
    plt.gca().set_facecolor("#101010")
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().xaxis.set_ticks_position('none') 
    plt.gca().yaxis.set_ticks_position('none') 
    
def plt_captions(title='', xlabel='', ylabel='', titlesize=22, labelsize=18):
    plt.title(title.upper(), fontsize=titlesize, pad=10, color='white', alpha=0.8)
    plt.xlabel(xlabel, fontsize=labelsize, color='white', alpha=0.8)
    plt.ylabel(ylabel, fontsize=labelsize, color='white', alpha=0.8)
##########################################################################################################################
# Vis
##########################################################################################################################
def represent_distribution(sample, xmin=None, xmax=None, nx=None,
                           kind='01', norm_hist=True, figsize=(20,8), title=''):
    mpl.rcParams['figure.figsize'] = figsize
    if kind == '0':
        f, ax_box = plt.subplots(1)
        sns.boxplot(sample, fliersize=0, whis=1.5, ax=ax_box)
        sns.stripplot(sample, color="orange", jitter=0.2, size=3, ax=ax_box)
        ax_box.set(xlabel='')        
        ax_box.set_title(title)
    else:
        if kind == '01':
            f, (ax_box, ax_hist) = plt.subplots(2, sharex=True,
                                                gridspec_kw={"height_ratios": (.25, .75)})
            sns.boxplot(sample, fliersize=0, whis=1.5, ax=ax_box)
            sns.stripplot(sample, color="orange", jitter=0.2, size=3, ax=ax_box)
            ax_box.set(xlabel='')
            ax_box.set_title(title)
        else:
            f, ax_hist = plt.subplots(1)
            ax_hist.set_title(title)
        sns.distplot(sample, ax=ax_hist, bins='sqrt', norm_hist=norm_hist)
        if nx is not None:
            ax_hist.xaxis.set_major_locator(plt.MaxNLocator(nx))
        if xmin is not None:
            ax_hist.set_xlim(left=xmin)
        if xmax is not None:
            ax_hist.set_xlim(right=xmax)

#     print('number of observations: {}'.format(len(sample)))
#     plt.show()
    
def p_quantile(x, p):
    """
    0 <= p <= 1
    """
    x = sorted(x)
    n = len(x)
    
    m = n * p
    if m % 1 == 0:
        m = int(m)
        return (x[m-1] + x[m]) / 2
    else:
        return x[int(floor(m))]

##########################################################################################################################
# Text processing
##########################################################################################################################
import re
import nltk
# nltk.download('punkt')
from nltk import (
    sent_tokenize as splitter, # text => [sentences]
    wordpunct_tokenize as tokenizer # sentence => [words]
)

def tokenize(text):
    return [tokenizer(sentence) for sentence in splitter(text)]

def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]

def tokenize_flatten(text):
    return flatten(tokenize(text))

def replace_hashtags_from_list(tokens_list):
    return [token for token in tokens_list if token != "#"]

def remove_digits(tokens_list):
    return [token for token in tokens_list 
                if not re.match(r"[-+]?\d+(\.[0-9]*)?$", token)]

def remove_containing_non_alphanum(tokens_list):
    return [token for token in tokens_list if token.isalpha()]

def clean_tokens(tokens_list):
    return replace_hashtags_from_list(remove_digits(remove_containing_non_alphanum(tokens_list)))

from nltk.corpus import stopwords
# nltk.download('stopwords')
def remove_stopwords(tokens_list, languages=None):
    return [token for token in tqdm(tokens_list)
                if not token.lower() in stopwords.words(languages)]

##########################################################################################################################
def frequency(df=None, by=None, aux=None, series=None, min_freq_to_show=2, figsize=(20,6)):
    mpl.rcParams['figure.figsize'] = figsize
#     plt.gca().grid(which='major', alpha=0.25, linestyle='--')
#     plt.gca().spines['right'].set_visible(False)
#     plt.gca().spines['left'].set_visible(False)
#     plt.gca().spines['top'].set_visible(False)
    c = np.random.choice(['#554DD2', '#C21D90', '#4ABDC2']) 
    if aux is None:
        if series is None:
            series = df[by]
        frequencies = series.groupby(series).count().sort_values(ascending=False)
    else:
        frequencies = df.groupby(df[by])[aux].nunique().sort_values(ascending=False)
    temp = frequencies[frequencies > min_freq_to_show]
    plt.bar(temp.index, temp.values, color=c, linewidth=0, alpha=0.7)
    
    
##########################################################################################################################
def shorten_tag(tag):
    if pd.isna(tag):
        return tag
    return ''.join(tag.split()[:1])

tags_mapping = [
 'blues',
 'classic',
 'country',
 'folk',
 'progressive',
 'reggae',
 'funk',
 'soundtrack',
 'electronic',
 'jungle',
 'composer',
 'gospel',
 'black',
#  'world',
#  'french',
#  'brazilian',
#  'canadian',
#  'colombian',
#  'german',
#  'greek',
#  'norwegian',
#  'southern',
#  'spanish',
#  'swedish',
#  'barbadian',
#  'birmingham',
#  'irish',
#  'italian',
#  'latin',
#  'latvian',
#  'lebanese',
#  'malian',
#  'northern',
#  'czech',
#  'deutschland',
#  'scottish',
#  'taiwanese',
#  'toronto',
]
tags_mapping = dict(zip(tags_mapping, [[t] for t in tags_mapping]))
tags_mapping.update({
'american': ['detroit','united', 'american', 'us', 'usa',  'los'],
'british': ['british', 'uk', 'english'],
'rock': ['rock', 'post-grunge', 'grunge'],
'heavy': ['heavy', 'thrash', 'hard', 'stoner', 'industrial', 'horror', 'grindcore', 'metal'],
'punk': ['punk', 'post-punk', 'hardcore', 'post-hardcore'],
'alternative': ['alternative', 'madchester'],
'dance': ['dance',  'dancehall'],
'hip-hop': ['hip', 'hip-hop',],
'jazz': ['jazz',],
'smooth': ['soul', 'melodic', 'smooth',],
'contemporary': ['contemporary', 'new'],
'other': ['whistle', 'steal','skate', 'ndw','ska', 'hong', 'production', 'desi', 'easy', 'franASSais','performance', 'operatic', 'suA(c)dois', 'a', 'dA1/4sseldorf', 'seen'],
'indie': ['indie', 'shoegaze'],
'r\'n\'b': ['r\'n\'b','rnb', 'rap'],
'pop': ['pop', 'house'],
'world': ['world', 'french', 'brazilian', 'canadian', 'colombian', 'german', 'greek', 'norwegian', 'southern', 'spanish', 'swedish', 'barbadian', 'birmingham', 'irish', 'italian', 'latin', 'latvian', 'lebanese', 'malian', 'northern', 'czech', 'deutschland', 'scottish', 'taiwanese', 'toronto', 'finnish'],
'trance': ['trip', 'trance'],
})
tags_inverse_mapping = {}
for key in tags_mapping:
    for value in tags_mapping[key]:
        tags_inverse_mapping[value] = key
tags_inverse_mapping
    