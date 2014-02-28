import nltk
import re
import sys
import random

#================================================== SETUP
# read a file from disk
#text = ''
#for line in sys.stdin:
#    text += line

f = open('sample2.txt','rU')
text = f.read()
# compile expressions to use to identify relations between named entities
IN = re.compile (r'.*\bin\b')
TO = re.compile (r'.*\bto\b')
# a list of verb tags for reference
verbs = ['VB',  'VBG',  'VBD', 'VBN',  'VBP',  'VBZ']
expressions_of_futility = [' did not achieve anything.\n',  ' did not achieve anything.\n',  "'s efforts were futile.\n", "'s efforts were futile.\n", ' was doomed to fail.\n', ' also struggled to find joy in writing poetry with Python.\n',  ' was doomed to fail.\n',]

#================================================== SOURCE TEXT PREPARATION
#================================================== AND NAMED ENTITY EXTRACTION

def tokenize_text_and_tag_named_entities(text):
    tokens = []
    # split the source string into a list of sentences
    # for each sentence, split it into words and tag the word with its PoS
    # send the words to the named entity chunker
    # for each chunk containing a Named Entity, build an nltk Tree consisting of the word and its Named Entity tag
    # and append it to the list of tokens for the sentence
    # for each chunk that does not contain a NE, add the word to the list of tokens for the sentence
    for sentence in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence))):
            if hasattr(chunk,  'node'):
                if chunk.node != 'GPE':
                    tmp_tree = nltk.Tree(chunk.node,  [(' '.join(c[0] for c in chunk.leaves()))])
                else:
                    tmp_tree = nltk.Tree('LOCATION',  [(' '.join(c[0] for c in chunk.leaves()))])
                tokens.append(tmp_tree)
            else:
                tokens.append(chunk[0])
    print tokens
    return tokens

#================================================== RELATIONSHIP EXTRACTION
#================================================== AND POEM ASSEMBLY

def extract_people_in_locations():
    # extract tuples of the form Named Entity: Person, relation text matching a regex, Named Entity: Location
    # from the annotated classobj ('doc')
    # specify an annotated training corpus ('ieer') for the extractor to train with
    for rel in nltk.sem.extract_rels('PERSON','LOCATION',doc,corpus='ieer',pattern=IN):
        print 'just checking'
        filler_tokens = dict(nltk.pos_tag(nltk.word_tokenize(rel['filler'])))
        # identify the type of the verb(s) in the relation text
        verb = [verb for verb in verbs if verb in filler_tokens.values()]
        if len(verb) > 0:
            verb = verb[0]
            # currently all tenses are handled with the same print template
            # we're going to call these 'present' tense
            if verb == 'VBZ' or verb == 'VB' or verb == 'VBG' or verb == 'VBP':
                print 'Why is ' + rel['subjtext'] + ' in ' + rel['objtext'] + '?'
                print 'Though ' + rel['subjtext'] + ' ' + rel['filler'] + ' ' + rel['objtext'] + ', '
                print rel['subjtext']  + random.choice(expressions_of_futility)
            # past tenses
            elif verb =='VBD' or verb == 'VBN':
                print 'Why is ' + rel['subjtext'] + ' in ' + rel['objtext'] + '?'
                print 'Though ' + rel['subjtext'] + ' ' + rel['filler'] + ' ' + rel['objtext'] + ', '
                print rel['subjtext']  + random.choice(expressions_of_futility)
        # no verb
        else:
            print 'Why is ' + rel['subjtext'] + ' in ' + rel['objtext'] + '?'
            print 'There is nothing for ' + rel['subjtext'] + ' in ' + rel['objtext']  + '.\n'

def extract_organizations_in_locations():
    for rel in nltk.sem.extract_rels('ORGANIZATION','LOCATION',doc,corpus='ieer',pattern=IN):
        #print nltk.sem.show_raw_rtuple(rel)
        #person_location_relations.append(rel)
        filler_tokens = dict(nltk.pos_tag(nltk.word_tokenize(rel['filler'])))
        verb = [verb for verb in verbs if verb in filler_tokens.values()]
        if len(verb) > 0:
            verb = verb[0]
            # currently all tenses are handled with the same print template
            # we're going to call these 'present' tense
            if verb == 'VBZ' or verb == 'VB' or verb == 'VBG' or verb == 'VBP':
                print 'Why is the ' + rel['subjtext'] + ' in ' + rel['objtext'] + '?'
                print 'Though it ' + rel['filler'] + ' ' + rel['objtext']
                print " it's efforts were futile.\n"
            # past tenses
            elif verb =='VBD' or verb == 'VBN':
                print 'Why is the ' + rel['subjtext'] + ' in ' + rel['objtext'] + '?'
                print 'Though it ' + rel['filler'] + ' ' + rel['objtext']
                print " it's efforts were futile.\n"
        # no verb
        else:
            print 'Why is the ' + rel['subjtext'] + ' in ' + rel['objtext'] + '?'
            print 'There is nothing for it in ' + rel['objtext']  + '.\n'

#================================================== ANNOTATED SOURCE TEXT CLASS
# The relation extractor requires a classobj
# This empty class is used like a Struct and filled with the required variables
class doc():
  pass
doc.headline = ['this is expected by nltk.sem.extract_rels but not used in this script']

#================================================== FUNCTION CALLS
# annotate the source text and store it in doc
doc.text = tokenize_text_and_tag_named_entities(text)
extract_people_in_locations()
extract_organizations_in_locations()
