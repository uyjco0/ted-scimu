# -*- encoding: utf-8 -*-

#
# 'text_augmentation.py'
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
import time
import base
import csv
import gensim
from gensim import corpora, similarities, models
import dbpedia
import math
import urllib2

# Constant used to measure the closeness between two weights
PERCENTAGE_MAX_WEIGHT = 0.05

def get_dbpedia_annotations(text, tokens):
    """
    It returns for the given 'text' only one annotation from Dbpedia. The criteria in order to choose the annotation to return is
    the token with the highest weight in the TF-IDF space from the tokens that are composing the annotation 's 'surface form'.
    PARAMETERS:
       1. text: The text used to query Dbpedia Spotlight for annotations
       2. tokens: A dict where each key is a token from the corpus and, where each value is the token 's weight in the
          TF-IDF space for the corpus 
    RETURNS:
       A tuple with the following format:
          (ANNOTATION_URI, ANNOTATION_SURFACE_FORM, ANNOTATION_ONTOLOGY_TYPES, SUPPORT_SCORE, SIMILARITY_SCORE) 
    """
    res = None
    # Request the annotations to the Dbpedia Spotlight 's Web Service
    annotations = dbpedia.get_annotations(text)
    # Extract the information from the returned annotations
    anns = dbpedia.get_results(annotations)
    if len(anns) > 0:
        if len(anns) == 1:
            res = anns[0]
        else:
            max_weight = 0
            max_element = None
            # Loop over the returned annotations and select only one in order to avoid to add to much information
            # The idea is to use the annotation from the tokens more relevant for the document, for this reason
            # the script is using the results from the TF-IDF model stored in 'tokens'
            for i in range(0, len(anns)):
                # The current annotation
                ann = anns[i]
                # The 'surface form' returned by Dbpedia
                base_tokens = ann[1]
                # The 'surface form' from Dbpedia could be a combination of tokens
                all_tokens = base_tokens.split()
                # Iterate over the tokens from the 'surface form'
                for token in all_tokens:
                    # If the token is a key in the dict 'tokens', then process the token
                    if token in tokens:
                        # It is a lucky token, it is the first
                        if max_weight == 0:
                            max_weight = tokens[token]
                            max_element = ann
                        # If the new token 's weight is clearly higher than the current weight, the the new one wins
                        elif tokens[token] > max_weight*(1 + PERCENTAGE_MAX_WEIGHT):
                            max_weight = tokens[token]
                            max_element = ann
                        # If the new weight has less than PERCENTAGE_MAX_WEIGHT difference with the current weight, 
                        # then check the 'support' or 'similarity score'
                        elif ((math.fabs(tokens[token] - max_weight))/max_weight) <= PERCENTAGE_MAX_WEIGHT:
                            # It checks the support, if it is bigger, then the new one wins
                            if ann[3] > max_element[3]:
                                max_weight = tokens[token]
                                max_element = ann
                            # If there is a tie with the support, then check the similarity score
                            elif ann[3] == max_element[3]:
                                # It checks the similarity score, if it is bigger, then the new one wins
                                if ann[4] > max_element[4]:
                                    max_weight = tokens[token]
                                    max_element = ann
            res = max_element

    return res


def augment_corpus_information(dictionary_name, mm_name, docs2corpus_name, tfidf_name, docs_augmented_name):
    """
    It returns the texts that will be used to augment the corpus 's document information in order to try to have a better match in a similarity
    query. It is used when the documents from a corpus are containing little information.
    PARAMETERS:
       1. dictionary_name: The name of the file with the generated dictionary for the corpus. The dictionary has the tokens used for the
       corpus representation in the VSM
       2. mm_name: The name of the file with the Market Matrix representation for the corpus in the VSM
       3. docs2corpus_name: The name of the file with the translations between the documents names (a file line) and the documents IDs for the 
          corpus representation in the VSM (the position in the file)
       4. tfidf_name: The name of the file with the TF-IDF representation (transformation) of the corpus
       5. docs_augmented_name: The name of the CSV file where to store the information about the augmentated documents 
    RETURNS:
       A dict where each key and value has the following format:
          {DOCUMENT_FILE_NAME:ANNOTATION_ABSTRACT}
       It also generate the CSV file 'docs_augmented_name' with the information about the augmentated documents. It has the following format:
           DOCUMENT_NAME, DBPEDIA_URI
    """
    res = {}
    total_augmentation = 0;
    try:
        # Load the needed vector transformations for the Science Museum corpus
        docs2corpus = base.get_docs2corpus(docs2corpus_name)
        dictionary = corpora.Dictionary().load(dictionary_name + '.dict')
        mm = corpora.MmCorpus(mm_name + '.mm')
        tfidf = gensim.models.tfidfmodel.TfidfModel().load(tfidf_name + '.tfidf')
        docs_augmented = open(docs_augmented_name + '.csv', "w")

        # Loop over all the documents from the stored Science Museum corpus representation 
        # in the VSM
        for i in range(0, len(mm)):
            # Get documents by offset, in this way the offset matches with the 
            # document ID within the corpus representation in the VSM
            doc = mm[i]
            # Get the Science Museum 's document name. The offset in the 'docs2corpus' file also
            # matches with the document 's offset within the corpus representation in the VSM
            doc_file_name = docs2corpus[i]
            # Get the document 's representation in the TF-IDF space
            vtf = tfidf[doc]
            # Sort the vector coordinates from high to low according their TF-IDF weight
            vtf = sorted(vtf, key=lambda info: info[1], reverse=True)

            print "Going to add Dbpedia annotations for: %s"%(doc_file_name)
            text = ''
            tokens = {}
            # Get the tokens from the document, add the token's weight to the
            # 'tokens' dict and build 'text' as the concatenation of all the
            # tokens. This 'text' is used later to ask for annotations to Dbpedia
            for tid, weight in vtf:
                if weight > 0:
                    # Get the token 's string from the token 's ID in the corpus
                    token = dictionary[tid]
                    tokens[token] = weight
                    if text == '':
                        text = token
                    else:
                        text = text + ' ' + token
            # If any, it get only one annotation from Dbpedia
            annotation = get_dbpedia_annotations(text, tokens)
            if annotation:
                # Ask for the 'abstract' referenced by the Dbpedia annotation
                # This 'abstract' is the one used to augment the document information
                # in order to try to have a better match with the TED talks
                abstract = dbpedia.get_abstract(annotation[0])
                if abstract is not None:
                    try:
                        abstract = abstract.encode('utf-8').strip()
                        res[doc_file_name] = abstract
                        total_augmentation = total_augmentation + 1
                    except:
                        pass
                docs_augmented.write((', '.join([doc_file_name, annotation[0]])).encode('utf-8').strip() + '\n')

        docs_augmented.close()

        print "The total amount of augmentations is %s  over a total of %s documents"%(total_augmentation,len(mm))

    except:
        try:
            docs_augmented.close()
        except:
            pass
        print "add_dbpedia_annotations"
        print ""
        traceback.print_exc()

    return res
