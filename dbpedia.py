# -*- encoding: utf-8 -*-

#
# 'dbpedia.py'
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

import urllib
import urllib2
import json
from lxml import html
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords

import traceback

# The endpoint for the Dbpedia web service: 
#    https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/Web-service
ENDPOINT = 'http://spotlight.dbpedia.org/rest/annotate'
# The header to be used in the HTTP requests
HEADER = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0.1', 'accept': 'application/json'}
# The time in seconds to be set for the HTTP request timeout
TIMEOUT = 15

def get_annotations(text, **kwargs):
    """
    It retrieves from the Dbpedia Spotlight 's Web Service the annotations for a given text.
    PARAMETERS:
       1. text: The text from which are wanted the annotations. It is the only mandatory parameter
       2. confidence: The value being used to filter the entities to be choosen
       3. support: The value being used to filter the entities to be choosen
       4. spotter: The algorithm being used to extract from the text the candidates to be annotated
       5. coreferenceResolution: Heuristic being used to infer the surface form
       6. types: The values being used to the filter the entities to be choosen
       7. disambiguators: The value being used to choose the disambiguation method
    RETURNS:
      A string with the response from the Dbpedia Spotlight 's Web Service 
    """
    annotations = ''
    # In order to see more about the parameters:
    #    https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/Lucene---Web-Service-Parameters
    parameters = {}
    confidence = 0.4
    support = 20
    spotter = 'LingPipeSpotter'
    coreferenceResolution = None
    types = None
    disambiguators = None

    for key, value in kwargs.iteritems():
        if key == 'confidence' and value is not None:
            confidence = value
        elif key == 'support' and value is not None:
            support = value
        elif key == 'spotter' and value is not None:
            spotter = value
        elif key == 'coreferenceResolution' and value is not None:
            coreferenceResolution = value
        elif key == 'types' and value is not None:
            types = value
        elif key == 'disambiguators' and value is not None:
            disambiguators = value

    parameters['text'] = text
    parameters['confidence'] = confidence
    parameters['support'] = support
    parameters['spotter'] = spotter

    if coreferenceResolution is not None:
        parameters['coreferenceResolution'] = coreferenceResolution

    if types is not None:
        parameters['types'] = types

    if disambiguators is not None:
        parameters['disambiguators'] = disambiguators

    try:
        data = urllib.urlencode(parameters)
        req = urllib2.Request(ENDPOINT, data, HEADER)
        res = urllib2.urlopen(req, timeout=TIMEOUT)
        annotations = res.read()

    except:
        print "get_annotations"
        print ENDPOINT
        print ""
        traceback.print_exc()

    return annotations

def get_results(annotations):
    """
    It parses the string with the response from the Dbpedia Spotlight 's Web Service and extract the relevant information for each annotation in
    the response.
    PARAMETERS:
       1. annotations: The string with the response from the Dbpedia Spotlight 's Web Service
    RETURNS:
       A list with a tuple for each annotation in the response. The tuples are having the following format:
          (ANNOTATION_URI, ANNOTATION_SURFACE_FORM, ANNOTATION_ONTOLOGY_TYPES, SUPPORT_SCORE, SIMILARITY_SCORE)
    """
    res = []
    try:
        if annotations and (annotations != ''):
            ann = json.loads(annotations)
            if 'Resources' in ann:
                resources = ann['Resources']
                for annotation in resources:
                    if annotation:
                        # 0: URI, 1: base tokens, 2: Ontology types, 3: support, 4: similarity score
                        res.append((annotation['@URI'], annotation['@surfaceForm'], annotation['@types'], annotation['@support'], annotation['@similarityScore']))
    except:
        print "get_results"
        print ""
        traceback.print_exc()

    return res


def get_text_in_eng(texts):
    """
    For a list of the same text in different languages, the script is choosing the text in the english language.
    PARAMETERS:
       1. texts: The list containing the same text in different languages
    RETURNS:
       A string with the text in the english language
    """
    res = None
    # Get the predefined stopwords for the english language
    eset = set(stopwords.words('english'))
    matches = []
    for text in texts:
        # Get the tokens from the current text
        tokens = wordpunct_tokenize(text)
        # Apply a minimal pre-processing to each token (lower it)
        ptokens = [token.lower() for token in tokens]
        # Create a set from the pre-processed tokens
        ptset = set(ptokens)
        # It holds the english stopwords contained in the current text
        commons = ptset.intersection(eset)
        # If there are some english stopwords in the text, then add the
        # amount of them to a list
        if len(commons) > 0:
            matches.append((text, len(commons)))
    if len(matches) > 0:
        # Sort from high to low by the amount of english stopwords
        # If we are lucky, then the english text has the more english stopwords
        matches = sorted(matches, key=lambda info: info[1], reverse=True)
        # Select the text with the higher amount of english stopwords
        res = matches[0][0]
    return res

def get_abstract(url):
    """
    From the given Dbpedia entry 's URL, the script retrieves the page, parses it and extract the english abstract.
    PARAMETERS:
       1. url: It is the URI being referenced by a Dbpedia Spotlight 's annotation 
    RETURNS:
       A string with the english abstract for the Dbpedia Spotlight 's annotation
    """
    res = None
    try:
        # Replacing some HTML encoding
        url = url.replace("%28", "(")
        url = url.replace("%29", ")")
        url = url.replace("%27", "'")
        url = url.replace("%2D", "-")

        req = urllib2.Request(url)
        req.add_header('User-Agent', HEADER['User-Agent'])
        res = urllib2.urlopen(req, timeout=TIMEOUT)
        page = res.read()
        tree = html.fromstring(page)
        # Parse the page and extract the SPAN sections with the abstracts
        items = tree.xpath("//span[re:match(@property, '.*dbpedia-owl:abstract.*')]", namespaces={"re": "http://exslt.org/regular-expressions"})
        texts = []
        if len(items) > 0:
            for item in items:
                # Extract the text from each selected SPAN section
                abstract = item.xpath('./text()')
                if len(abstract) > 0:
                    texts.append(abstract[0])
            # The same abstract could be in several languages
            # It gets the english abstract
            res = get_text_in_eng(texts)
    except:
        print "get_abstract"
        print url
        print ""
        traceback.print_exc()
    
    return res
