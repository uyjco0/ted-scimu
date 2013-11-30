# -*- encoding: utf-8 -*-

#
# 'base.py'
# 
# Copyright (C) 2013 Jorge Couchet <jorge.couchet at gmail.com>
#
# This file is part of 'ted-scimu'
# 
# 'ted-scimu' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# 'ted-scimu' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with 'ted-scimu'.  If not, see <http ://www.gnu.org/licenses/>.
#

import traceback
import os

import unicodedata
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize.punkt import PunktWordTokenizer


TED_EXTRA_STOP_WORDS = 'ted_extra_stopwords.txt'


def get_all_filenames(path):
    """
    It gets all the filenames under a given path.
    PARAMETERS:
       1. path: The path to the folder from which to get the filenames
    RETURNS:
       A tuple with the following format:
          (PATH_TO_FOLDER, LIST_WITH_FILENAMES_UNDER_FOLDER)
    """
    res = (None,[])
    try:
        f = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            res = (dirpath, filenames)
    except:
        print "get_all_filenames"
        print ""        
        traceback.print_exc()
    return res


def normalize_word(word):
    """
    It gets a string and replaces the non ASCII characters for their closest ASCII equivalents.
    PARAMETERS:
       1. word: The string to be processed
    RETURNS:
       A new string with the non ASCII characters replaced by their closest ASCII equivalents
    """
    uniword = unicode(word, 'utf8')
    normalized = unicodedata.normalize('NFKD', uniword).encode('ASCII', 'ignore')
    return normalized


def remove_punctuation_stopwords(text, is_ted):
    """
    For a given text, the script generates a list of words which are pre-processed and filtered. The preprocessing includes 
    punctuation elimination, replacing non ASCII characters by their closest ASCII equivalents and lowering. The filtering
    includes elimination of the words that are having only one character, words that are numbers and words that are stopwords.
    PARAMETERS:
       1. text: The string to be pre-processed and filtered
       2. A flag to say if to add to the english standard stopword the custom stopwords prepared for the TED talks corpus
    RETURNS:
       A list of strings where each string is a word from the given text. Each word is the result of the pre-processing and filtering
       carried out by the script
    """
    res = []
    try:
        # Punctuation
        chars = ['.', '/', "'", '"', '?', '!', '#', '$', '%', '^', '&', '*', '(', ')', ' - ', '_', '+' ,'=', '@', ':', '\\', ',', ';', '~', '`', '<', '>', '|', '[', ']', '{', '}', '–', '“', '»', '«', '°', '’']

        # Get the english standard stopwords:
        standard_stopwords = nltk.corpus.stopwords.words('english')
    
        ted_stopwords = []
        if is_ted:
            # Get the custom stopwords for the TED talks corpus
            ted_stopwords = (open(TED_EXTRA_STOP_WORDS).read()).split()

        # Merge the two lists
        stopwords = standard_stopwords + ted_stopwords

        # Remove the punctuation from the text
        for char in chars:
            text = text.replace(char, ' ')
    
        # Broke the text in words. It is assuming that the words are string
        # chunks separated by blank spaces
        text = text.split()

    
        for w in text:
            # Convert non ASCII characters, lower it and remove blank spaces
            tmp = normalize_word(w.lower().strip())
            # Select only the words that have lenght higher than 1, are not digits and ar not stopwords
            if (len(tmp) > 1) and (not tmp.isdigit()) and (tmp not in stopwords):
                res.append(tmp)

    except:
        print "remove_punctuation_stopwords"
        print ""
        traceback.print_exc()
        
    return res



def tokenize_document(doc, is_ted, is_only_nouns):
    """
    For a given string text, the script get the text's tokens. The text is pre-processd and filtered, after that the NLTK tokenizer
    process is carried out, if a flag is enabled, the tokens are tagged and filtered out only the nouns and finally the tokens are
    lemmatized.
    PARAMETERS:
       1. doc: The string text from which extract the tokens
       2. is_ted: A flag to say if to add to the english standard stopword the custom stopwords prepared for the TED talks corpus
       3. is_only_nouns: A flag to say if extract only the tokens tagged as a nouns
    RETURNS:
       A list of strings where each string is a token from the given text
    """
    res = []
    
    try: 
        # First pre-process and filter the given text
        doc2= remove_punctuation_stopwords(doc, is_ted)
        # From the pre-proccesed and filtered text apply the NLTK tokenizer process
        tokens = PunktWordTokenizer().tokenize(' '.join(doc2))
        # If enabled the flag, then only extract the tokens tagged as a nouns
        if is_only_nouns:
            tagged_tokens = nltk.pos_tag(tokens)
            tokens = []
            for token, tag in tagged_tokens:
                if (tag == 'NN') or (tag == 'NNP') or (tag == 'NNS'):
                    tokens.append(token)
        # Lemmatize the tokens using the NLTK lemmatizer
        for i in range(0,len(tokens)):
            lema = WordNetLemmatizer().lemmatize(tokens[i])
            # If the token was not lemmatized, then apply verb lemmatization
            if lema == tokens[i]:
                lema = WordNetLemmatizer().lemmatize(tokens[i], 'v')
            if (len(lema) > 1) and (not lema.isdigit()):
                # Append the lema to the result to be returned
                res.append(lema)
    except:
        print "tokenize_document"
        print ""
        traceback.print_exc()

    return res


def get_docs2corpus(file_name):
    """
    It opens the file with the where is stored the translation between the documents names (the file line) and the documents IDs 
    (the position in the file) for the corpus representation in the Vector Space Model (VSM).
    PARAMETERS:
       1. file_name: The name of the file to be opened
    RETURNS:
       A list where each position in the document ID in the VSM representation and the value is a string with the document name 
    """
    res = []
    try:
        with open(file_name + '.docsid', 'r') as f:
            for line in f.readlines():
               # It has the document name
               # The position in the list is the document id in the corpus
               res.append(line.replace('\n', ''))
    except:
        print "get_docs2corpus"
        print ""
        traceback.print_exc()

    return res

