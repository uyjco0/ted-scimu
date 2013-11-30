# -*- encoding: utf-8 -*-

#
# 'generate_vsm.py'
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
import gensim
from gensim import corpora, similarities, models

def tokenize(is_ted, is_only_nouns, files_path, docs2corpus_name, is_gen_dict, dictionary_name, market_matrix_name, is_tfidf, tfidf_min_weight, tfidf_name, texts_for_augmentation):
    """
    It is extracting the tokens for a document set (corpus) stored in given folder and building the corpus representation for the Vector Space
    Model (VSM) generated from the tokens.
    PARAMETERS:
       1. is_ted: A flag to say if use the extra stopwords list for the TED talks. It is a custom list created after manually analyzing the TED
          Talks corpus
       2. is_only_nouns: A flag to say if extract the tokens only from the identified documents 's nouns. Be careful, because if the flag is True
          the script takes longer to complete
       3. files_path: The directory storing the corpus documents
       4. docs2corpus_name: The name of the file where to store the translation between the documents names (the file line) and the documents IDs 
          (the position in the file) for the corpus representation in the Vector Space Model (VSM)
       5. is_gen_dict: A flag to say when to generate a new dictionary (is_gen_dict == True) and when to use an existing dictionary. When using
          an existing dictionary, the corpus is transformed to the VSM using the tokens obtained from another corpus or for the corpus itself but 
          in a previous phase
       6. dictionary_name: The name of the file with the dictionary to be generated (if is_gen_dict == True) or loaded (if is_gen_dict == False)
       7. market_matrix_name: The name of the file will be serialized in the Market Matrix format the corpus representation in the VSM from the
          tokens in the dictionary
       8. is_tfidf: A flag to say if to extract only the tokens having a TF-IDF weight greater that a given threshold. The flag also says if to
          generate the file with the corpus representation in the TF-IDF space
       9. tfidf_min_weight: The threshold being used when is_tfidf == True
      10. tfidf_name: The name of the file being generated when is_tfidf == True
      11. texts_for_augmentation: It is a dict indexed by the documents names and the value is the text to be used in order to augmentate the
          document information. It means that previously to the tokens extraction, the text from the dict 's value is concatenated to the text
          in the document 
    RETURNS:
       Nothing. It is only generating the files listed above.
    """
    texts_tokens = []
    docs2corpus = []
    # Get the all the files names under 'files_path'
    dirpath, filenames = base.get_all_filenames(files_path)
    if (dirpath is not None) and (len(filenames) > 0):
        print "Going to tokenize: %s"%(time.strftime("%H:%M:%S"))
        for i in range(0, len(filenames)):
            filepath = dirpath + '/' + filenames[i]
            doc = open(filepath).read()
            # If is_ted = True, then is adding the custom stop words for the TED talks
            # If is_only_nouns = True, then only the tokens that are nouns are preserved
            # ---
            # Transform the document from a string to a list of tokens
            #   string -> [token, token, .. , token]
            # ---
            # If there is extra text in order to augment the doc content, then this text
            # is in the 'texts_for_augmentation'
            if texts_for_augmentation is not None:
                if filenames[i] in texts_for_augmentation:
                    if texts_for_augmentation[filenames[i]] is not None:
                        doc = doc + ' ' + texts_for_augmentation[filenames[i]]
            tokens = base.tokenize_document(doc, is_ted, is_only_nouns)
            if len(tokens) > 0:
                texts_tokens.append(tokens)
                docs2corpus.append((filenames[i]))
        print "Finished tokenization: %s"%(time.strftime("%H:%M:%S"))

        # Saving to disc the documents id. The position in the file is the document id in the corpus
        with open(docs2corpus_name + '.docsid', 'wb') as f:
            for filename in  docs2corpus:
                f.write(filename + '\n')
            f.close()
       
        if is_gen_dict: 
            # Creating a dictionary
            # ---
            # The dictionary has:
            #   1. The set of unique tokens that are composing the document set
            #   2. A unique ID for each token
            #   3. The global frequency of the token in the document set
            # ---
            # The number of tokens in the dictionary represents the dimension
            # of the Vector Space to be used:
            #    It means that each document in the document set will be converted
            #    in a vector where:
            #        Each coordinate (item) in the vector is a tuple that
            #        has a token ID (from the dictionary) and the number of
            #        times that the token appears in the document (local frecuency)
            dictionary = corpora.Dictionary(texts_tokens)
        else:
            # It is loading a previously serialized dictionary
            # ---
            # When is not created a new dictionary, but loaded one already existing,
            # then the process is transforming a new corpus (NC) to the Vector Space of
            # (token_id, local_frecuency_in_doc) already created from a previous corpus (PC)
            # ---
            # It is needed if is wanted to compare the documents in NC in the Vector Space 
            # created from PC
            dictionary = corpora.Dictionary().load(dictionary_name + '.dict')

        # Transforming the document set from the surface representation
        # (strings) to a Vector Space where each unique token is a dimension
        # ---
        # The function 'doc2bow' takes the document 's surface representation 
        # (as a list of tokens) and returns its vector representation (as a 
        # list of tuples, where each tuple has the token ID and the token 
        # frecuency in the document:
        #    [token, .. , token] -> [(token_id, local_frecuency_in_doc), .. , (token_id, local_frecuency_in_doc)]
        corpus = [dictionary.doc2bow(text_tokens) for text_tokens in texts_tokens]

        if is_tfidf:
            # Using the TF-IDF model, transform the document set from the Vector Space of (token_id, local_frecuency_in_doc)
            # to a Vector Space of (token_id, locally/globally_weighted_frecuency_for_doc)
            # The new Vector Space still has as a dimension the number of unique tokens composing the document set
            print "Going to apply the TF-IDF model: %s"%(time.strftime("%H:%M:%S"))
            tfidf = gensim.models.tfidfmodel.TfidfModel(corpus, normalize=True)

            print "Going remove from the documents the tokens with weight less than: %s"%(tfidf_min_weight) 
            # Remove from the documents the tokens with a tfidf < tfidf_min_weight 
            pos = 0 
            # Loop through the documents 's representation in the Vector Space of (token_id, local_frecuency_in_doc)
            for db in corpus:
                # Get the document 's representation in the TF-IDF Vector Space
                vtf= tfidf[db]
                remove_tokens = []
                # Loop through the document 's coordinates in the TF-IDF Vector Space
                for tid, weight in vtf:
                    # If the document 's coordinate - a tuple (token_id, token_weight> - has its weight less than 
                    # tfidf_min_weight, then the associated token is selected for removal from the document
                    if weight < tfidf_min_weight:
                        # Get the token string from the token id
                        token = dictionary[tid]
                        remove_tokens.append(token)
                if len(remove_tokens) > 0:
                    # Get the original tokens for the document
                    tokens = texts_tokens[pos]
                    new_tokens = []
                    for t in tokens:
                        if t not in remove_tokens:
                            # Append only the tokens that are not selected for removal
                            new_tokens.append(t)
                    # Replace the document representation for a new one without the token selected for removal
                    texts_tokens[pos] = new_tokens
                pos = pos + 1

            # Re-creating the new representations from the document set with the updated tokens
            if is_gen_dict: 
                dictionary = corpora.Dictionary(texts_tokens)
            corpus = [dictionary.doc2bow(text_tokens) for text_tokens in texts_tokens]
            tfidf = gensim.models.tfidfmodel.TfidfModel(corpus, normalize=True)
            # Saving to disc the document set 's representation in the TF-IDF Vector Space
            tfidf.save(tfidf_name + '.tfidf')


            print "Finished the TF-IDF process: %s"%(time.strftime("%H:%M:%S"))

        if is_gen_dict:
            # Saving the dictionary to disc
            dictionary.save(dictionary_name + '.dict')
        # Using the Market Matrix format in order to serialize to disc the document set 's representation in the Vector Space
        corpora.MmCorpus.serialize(market_matrix_name + '.mm', corpus)
            
            

def train_lda_model(dictionary_name, corpus_name, ntopics, update, chunks, npasses, topics_model_name):
    """
    It is generating the Latent Dirichlet Allocation (LDA) model for a given corpus. The model is trained using the text from the
    documents in the corpus.
    PARAMETERS:
       1. dictionary_name: The name of the file with the information about he tokens that are generating the VSM in which the given corpus 
          is represented
       2. corpus_name: The name of the file with the corpus representation in the VSM from the tokens in the dictionary
       3. ntopics: The number of topics for the LDS model. This number of topics will be the dimension of the Vector Space generated by the
          LDA model
       4. update: It is saying the amount of chunks after which the model is updated when used online training. If update == 0, then the 
          training is batch. If update > 0, then the training in online. Here online means that the model is updated before a full pass over 
          the corpus is completed. If the corpus has an accurate and stable representation from the domain (hence not much topic drift), then 
          the online version is prefered because it converges faster. Otherwise the batch version is better to use
       5. chunks: The amount of documents after which to update the model in the online training. If the chunks size is very large (near to the
          total number of documents in the corpus), then the training is more batch than online, then the number of passes must be increased
       6. passes: The number of complete training cycles over the corpus. In one pass the whole corpus is being processed. If the training is
          online, then in 1 pass the complete corpus was consumed but the model was updated several times according the chuncks number. If the
          training is batch, then in 1 pass the complete corpus was consumed but the model was updated only 1 time. Thus the batch training
          requires a higher number of passes than the online training
       7. topics_model_name: The name of the file where will be serialized the  LDA model being generated
    RETURNS:
       The in-memory representation of the LDA model trained from the given corpus
    """
    res = None
    try:
        # Load the serialized dictionary
        dictionary = corpora.Dictionary().load(dictionary_name + '.dict')
        # Load the document set 's representation in the Vector Space (using the serialized file in the Market Matrix format)
        mm = corpora.MmCorpus(corpus_name + '.mm')

        print "Going to train: %s"%(time.strftime("%H:%M:%S"))
        # Using the Latent Dirichlet Allocation model, transform the document set from the Vector Space of (token_id, local_frecuency_in_doc)
        # to a Vector Space of (topic_id, local_topic_contribution_in_doc)
        # The dimension of the new Vector Space is the number of topics
        lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=dictionary, num_topics=ntopics, update_every=update, chunksize=chunks, passes=npasses)
        print "Finished the training: %s"%(time.strftime("%H:%M:%S"))
        # Saving to disc the document set 's representation in the new Vector Space
        lda.save(topics_model_name + '.lda')
        res = lda
    except:
        print "train_lda_model"
        print ""
        traceback.print_exc()

    return res
    

#tokenize(True, True, 'training_ted', 't1', True, 't1', 't1', True, 0.05, 't1', None)
#lda = train_lda_model('t1', 't1', 150, 1, 80, 7, 't1')

#texts_for_augmentation = test4.augment_corpus_information('sc-ind', 'sc-ind', 'sc-ind', 'sc-ind', 'docs_augmentated')
#tokenize(True, True, 'rel_scimu', 'sc1', False, 't1', 'sc1', True, 0.05, 'sc1', texts_for_augmentation)

#tokenize(True, True, 'rel_scimu', 'sc-ind', True, 'sc-ind', 'sc-ind', True, 0.05, 'sc-ind', None)
