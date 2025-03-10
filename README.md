
           TED-SCIMU
==============================

The system is able to make the following:

1. Extract the english subtitles for all the availables TED talks [1] and generate a local corpus (TED talks corpus).
   The local corpus is stored in files and also it is possible to store them in a PostgreSql database.

2. Get the data available at the Science Museum collections [2] and generate a local corpus (Science Museum corpus).
   The local corpus is stored in files and also it is possible to store them in a PostgreSql database.

3. Pre-process the generated corpus in order to generate better representation for later analysis over the corpus.
   This pre-processing includes:
      * Replacing non ASCII characters for their closest ASCII equivalent
      * Removing punctuation and stopwords
      * Tokenization, tagging (including filtering by tagging) and lemmatization
          It is accomplished using the excelent NLTK software [3]

4. For each document from the available local corpus, augment the document information with the english abstract from 
   Dbpedia Spotlight annotations [4]

5. Generate models for the available local corpus in different Vector Space Models (VSMs).
   The used Vector Space Models are:
      * The Term Frequency–Inverse Document Frequency (TF-IDF) [5]
      * The Latent Dirichlet Allocation (LDA) [6]
   The generation of these Vector Space Models is done through the use of excellent gensim software [7]

6. Using all the functionality described above, TED-SCIMU is enabling a new way to navigate and discover TED talks:
      To the user is displayed a list of images associated with the objects from the Science Museum collection, and when the 
      user selects an image according her/his interests and preferences, then it is possible to show her/him a related TED talk.
      The relationship between the images and the TED talks is found through the main topics discovered in the TED talks using 
      the Latent Dirichelt Allocation model for the TED talks corpus.


[1] http://on.ted.com/23
[2] http://api.sciencemuseum.org.uk/documentation/collections
[3] http://nltk.org
[4] https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki
[5] http://en.wikipedia.org/wiki/Tf%E2%80%93idf
[6] http://en.wikipedia.org/wiki/Latent_Dirichlet_allocation
[7] https://github.com/piskvorky/gensim
