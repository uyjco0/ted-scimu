# -*- encoding: utf-8 -*-

#
# 'smilarity_query_scimu.py'
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
import urllib2
import csv
import gensim
from gensim import corpora, similarities, models

def download_image_from_scimu(base_url, path, media_id, extension):
        """
        It downloads to local storage an image from the Web Service offering the Science Museum images
        PARAMETERS:
           1. base_url: The base URL to the Science Museum 's Web Service
           2. path: The local path to the folder where to store the image. If it is 'None' the image is stored in the folder where the script is
           3. media_id: The image identifier for the Web Service
           4. extension: The image extension
        RETURNS:
           Nothing. The downloaded image is placed in local storage
        """
        if path is None:
           path = ''
        else:
            path = path + '/'

        file_name = path + media_id + extension
        url = base_url + media_id
        imgData = urllib2.urlopen(url).read()
        with open(file_name, 'wb') as f:
            f.write(imgData)
            f.close()


def get_scimu_processed(processed_scimu_name):
    """
    It loads the file with the summary of all the processed Science Museum objects that belongs to the Science Museum corpus
    PARAMETERS:
       1. processed_scimu_name: A complete file name (if there is not path, then the document is relative to the script)
    RETURNS:
        A dict indexed by the document name in the corpus and where each value is a list with the following format:
           [SCIMU_DOCUMENT_COMPLETE_PATH, SCIMU_OBJECT_ID, SCIMU_OBJECT_NAME, SCIMU_OBJECT_TITLE, SCIMU_OBJECT_DESC, SCIMU_MEDIA_ID]
    """
    scimu_processed_data = {}
    try:
        with open(processed_scimu_name + '.csv', 'rb') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                tmp = []
                for i in range(0, len(row)):
                    if i <> 1:
                        tmp.append(row[i])
                # The dict is indexed by the doc 's filename
                scimu_processed_data[row[1]]=tmp
            f.close()
    except:
        print 'get_scimu_processed'
        traceback.print_exc()        
    return scimu_processed_data

def get_scimu_augmentated(docs_augmentated_name):
    """
    It loads the file with the summary of the documents from the Science Museum corpus augmentated with the abstract from the
    Dbpedia Spotlight annotations.
    PARAMETERS:
       1. docs_augmentated_name: A complete file name (if there is not path, then the document is relative to the script)
    RETURNS:
        A list with the following format:
           [SCIMU_DOCUMENT_NAME]
    """
    docs_augmentated_data = []
    try:
        # 'scimu_processed_objects.csv'
        with open(docs_augmentated_name + '.csv', 'rb') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                docs_augmentated_data.append(row[0])
            f.close()
    except:
        print 'get_scimu_augmentated'
        traceback.print_exc()
    return docs_augmentated_data


def get_vsm_id_from_object_id(object_id, docs2corpus_scimu, processed_scimu):
    """
    It returns the ID of the Science Museum corpus 's document whithin its VSM representation from the Science Museum object ID.
    It works only for the Science Museum corpus.
    PARAMETERS:
       1. object_id: The Science Museum object ID
       2. docs2corpus_scimu: The list with the translations between the Science Museum documents with the generated text from the 
          objects (a file line) and the IDs for these documents representation in the VSM (the position in the file) 
       3. processed_scimu: A dict with the summary of all the processed Science Museum objects that belongs to the Science Museum corpus
    RETURNS:
       The document 's ID in its VSM representation or -1 if it was not found
    """
    res = -1
    try:
        for i in range(0, len(docs2corpus_scimu)):
            doc_name = docs2corpus_scimu[i]
            if processed_scimu[doc_name][1] == object_id:
                res = i
                break
    except:
        print 'get_vsm_id_from_object_id'
        traceback.print_exc()
    return res


def get_vsm_id_from_document_name(doc_name, docs2corpus):
    """
    It returns the ID of the corpus 's document whithin its VSM representation from the document name in the corpus.
    It works for the TED talks and Science Museum corpus
    PARAMETERS:
       1. doc_name: The document name in the Science Museum corpus
       2. docs2corpus: The list with the translations between the corpus documents (a file line) and the IDs for these documents 
       representation in the VSM (the position in the file) 
    RETURNS:
       The document 's ID in its VSM representation or -1 if it was not found
    """
    res = -1
    try:
        for i in range(0, len(docs2corpus)):
            if docs2corpus[i] == doc_name:
                res = i
                break
    except:
        print 'get_vsm_id_from_document_name'
        traceback.print_exc()
    return res


def get_object_id_from_vsm_id(vsm_id, docs2corpus_scimu, processed_scimu):
    """
    It returns the Science Museum object ID from the ID of the Science Museum corpus 's document whithin its VSM representation.
    It works only for the Science Museum corpus.
    PARAMETERS:
       1. vsm_id: The document 's ID in its VSM representation
       2. docs2corpus_scimu: The list with the translations between the Science Museum documents with the generated text from the 
          objects (a file line) and the IDs for these documents representation in the VSM (the position in the file) 
       3. processed_scimu: A dict with the summary of all the processed Science Museum objects that belongs to the Science Museum corpus
    RETURNS:
       The Science Museum object ID or None if it was not found
    """
    try:
        doc_name = docs2corpus_scimu[vsm_id]
        object_id = processed_scimu[doc_name][1]
        res = object_id
    except:
        print 'get_object_id_from_vsm_id'
        traceback.print_exc()
    return res


def get_most_contributing_topic(tid, sid, mm_ted, mm_scimu, lda_ted):
    """
    For a given TED talk ID in the VSM and a Science Museum object ID in the VSM, the script is returning the most contributing
    topic for each one in the the TED talks LDA model.
    PARAMETERS:
       1. tid: The TED talk ID in the VSM
       2. sid: The Science Museum object ID in the VSM
       3. mm_ted: The TED talks corpus representation in the VSM
       4. mm_scimu: The Science Museum corpus representation in the TED talks VSM
       5. lda_ted: The LDA model for the TED Talks corpus
    RETURNS:
       A tuple with the following format:
          (STRING_WITH_TOKENS_FOR_THE_MOST_CONTRIBUTING_TOPIC_IN_TED_TALK, STRING_WITH_TOKENS_FOR_THE_MOST_CONTRIBUTING_TOPIC_IN_SCIMU_DOC) 
    """
    ted_topic = ''
    scimu_topic = ''
    res = ('','')
    try:
        # Get the TED talk vector representation
        tv = mm_ted[tid]
        # Get the Science Museum object vector representation
        sv = mm_scimu[sid]
        # Get the topics distribution for the given TED talk
        ttopics = lda_ted[tv]
        # Get the ID of the most contributing topic
        if len(ttopics) > 0:
            topic_id1 = ttopics[0][0]
            # Get the tokens distributions for the most contributing topic
            tdist1 = lda_ted.show_topic(topic_id1)
            for dist, token in tdist1:
                if ted_topic == '':
                    ted_topic = token
                else:
                    ted_topic = ted_topic + ' ' + token
        # Get the topics distribution for the given Science Museum object
        stopics = lda_ted[sv]
        # Get the ID of the most contributing topic
        if len(stopics) > 0:
            topic_id2 = stopics[0][0]
            # Get the tokens distributions for the most contributing topic
            tdist2 = lda_ted.show_topic(topic_id2)
            for dist, token in tdist2:
                if scimu_topic == '':
                    scimu_topic = token
                else:
                    scimu_topic = scimu_topic + ' ' + token

        res = (ted_topic, scimu_topic)
    except:
        print 'get_most_contributing_topic'
        traceback.print_exc()
    return res


def get_talks_similar2scimu_object(is_pos, doc_pos, object_id, processed_scimu_name, docs2corpus_ted, docs2corpus_scimu, dictionary_ted, mm_scimu, lda_ted, index_ted):
    """
    It returns the TED talks that are similar to the Science Museum object using the LDA model.
    PARAMETERS:
       1. is_pos: A flag saying if the parameter 'doc_pos' has the document 's ID in its VSM representation
       2. doc_pos: The document offset in the file 'docs2corpus_scimu_name' and also it is the ID in the Science Museum 's corpus (the file 
          'mm_scimu_name')
       3. object_id: The Science Museum object ID. It is used when is_pos == False and it is needed to get the document 's ID in its VSM 
          representation
       4. processed_scimu_name: The name of the file with the summary of all the processed Science Museum objects that belongs to the Science 
          Museum corpus (the file 'mm_scimu_name')
       5. docs2corpus_ted: The list with the translations between the TED Talks documents with the subtitles (a file line) and the IDs for these
          documents representation in the VSM (the position in the file) 
       6. docs2corpus_scimu: The list with the translations between the Science Museum documents with the generated text from the objects (a file 
          line) and the IDs for these documents representation in the VSM (the position in the file) 
       7. dictionary_ted: A generated dictionary for the TED talks corpus
       8. mm_scimu: The Market Matrix representation for the Science Museum corpus in the TED talks VSM. It means that the vectors representing
          a document in the Science Museum corpus are having as coordinates the tokens from the TED talks corpus. Thus it is very probably that
          the 'mm_scimu' is a very sparse matrix
       9. lda_ted: The trained LDA model for the TED talks corpus
      10. index_ted: The LDA model 's similarity matrix in order to compute similarities in the TED talks LDA space
    RETURNS:
       A list of tuples, where each tuple has the following format:
          (SIMILARITY_SCORE, TED_CORPUS_DOCUMENT_NAME, SCIMU_CORPUS_DOCUMENT_NAME, SCIMU_OBJECT_ID,  TED_ID_VSM, SCIMU_ID_VSM, SCIMU_MEDIA_ID)
    """
    res = []
    try:
        processed_scimu_data = get_scimu_processed(processed_scimu_name)
        if not is_pos:
            # Get the document 's ID in its VSM representation from the Science Museum object ID
            doc_pos = get_vsm_id_from_object_id(object_id, docs2corpus_scimu, processed_scimu_data)
            if doc_pos == -1:
                return res
        # Get a document from the corpus by offset
        doc = mm_scimu[doc_pos]
        # Get the document representation in the LDA VSM
        vlda = lda_ted[doc]
        # Perform a query (the 'vlda' vector is the query)
        # ---
        # It gets the TED talks similar to the doc
        # ---
        # The 'index' is set with the parameter 'num_best', 
        # so the results are sorted from high to low
        sims = index_ted[vlda]
        for ted_doc_pos, sim_score in sims:
            # Get the document name for the document from the TED talks corpus. In the case of the TED talks corpus, the document 's name  
            # without the extension ('.txt') matches with the TED talk ID
            talk_doc = docs2corpus_ted[ted_doc_pos]
            # Get the document name for the document from the Science Museum corpus. In the case of the Science Museum corpus, the
            # document 's name sometimes does not match with the Science Museum object ID (because sometimes the '/' characters in  
            # the object ID string are replaced by the '-' character. In order to get the real Object ID from the document name is 
            # needed to use the file 'processed_scimu_data'
            doc_file_name = docs2corpus_scimu[doc_pos]
            # It add the TED talks document name, the Science Museum document name, the Science Museum 's object ID, the TED talk ID in the VSM, 
            # the Science Museum object ID in the VSM, and the media ID related to the Science Museum 's object
            res.append((sim_score, talk_doc, doc_file_name, processed_scimu_data[doc_file_name][1], ted_doc_pos, doc_pos, processed_scimu_data[doc_file_name][-1]))
    except:
        print 'get_talks_similar2scimu_object'
        traceback.print_exc()
    return res
