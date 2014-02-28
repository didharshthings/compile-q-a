from nltk import ne_chunk,pos_tag
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.treebank import TreebankWordTokenizer
import re
import nltk
'''
	import nltk
	nltk.download('words')
	nltk.download('punkt')
	nltk.download('maxent_treebank_pos_tagger')
	nltk.download('maxent_ne_chunker')
'''

from py2neo import neo4j
graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

TreeBankTokenizer = TreebankWordTokenizer()
PunktTokenizer = PunktSentenceTokenizer()

f = open('sample2.txt','rU')
raw = f.read()

#sentences = PunktTokenizer.tokenize(raw)
#tokens = [TreeBankTokenizer.tokenize(sentence) for sentence in sentences]
#tagged = [pos_tag(token) for token in tokens]
#chunked = [ne_chunk(taggedToken) for taggedToken in tagged]

entities = []
for sentence in PunktTokenizer.tokenize(raw):
        chunks = ne_chunk(pos_tag(TreeBankTokenizer.tokenize(sentence)))
        entities.extend([chunk for chunk in chunks if hasattr(chunk,'node')])
        #print chunks
#raw_input('Press <enter> to continue')

print entities


IN = re.compile(r'.*\bin\b(?!\b.+ing)')
tokens = []

#print "printing tokens"
for sentence in nltk.sent_tokenize(raw):
	for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence))):
		if hasattr(chunk,'node'):
			if chunk.node != 'GPE':
				tmp_tree = nltk.Tree(chunk.node, [(''.join(c[0] for c in chunk.leaves()))])
			else:				
				tmp_tree = nltk.Tree('LOCATION',[(''.join(c[0] for c in chunk.leaves()))])
			tokens.append(tmp_tree)
		else:
			tokens.append(chunk[0])
#print tokens	 

class doc():pass
doc.headline=['']
doc.text = tokens

#for rel in nltk.sem.extract_rels('PERSON','LOCATION', doc, corpus='ieer', pattern = IN):
# print nltk.sem.relextract.show_raw_rtuple(rel)  

#doc.text=[nltk.Tree('ORGANIZATION', ['WHYY']), 'in', nltk.Tree('LOCATION',['Philadelphia']), '.', 'Ms.', nltk.Tree('PERSON', ['Gross']), ',']
# doc.text = [Tree('ORGANIZATION', ['WHYY']), 'in', Tree('LOCATION', ['Philadelphia']), '.', 'Ms.', Tree('PERSON', ['Gross']), ',']
#for rel in  nltk.sem.extract_rels('ORG','LOC',doc,corpus='ieer',pattern=IN):
  # print nltk.sem.relextract.show_raw_rtuple(rel)

people = graph_db.get_or_create_index(neo4j.Node, "people")

def get_person(name):
    """ A simple, nïeve function to fetch the first person indexed with a
    particular name.
    """
    person_nodes = people.get("name", name)
    return person_nodes[0]

def get_person_if_exists(name):
    """ An extension of the function above, dealing with the case where no-one
    has that name.
    """
    person_nodes = people.get("name", name)
    if person_nodes:
        return person_nodes[0]
    else:
        return None

def get_person_safely(name):
    """ A further extension, recognising the case where multiple nodes are
    indexed under the same name.
    """
    person_nodes = people.get("name", name)
    if len(person_nodes) == 1:
        return person_nodes[0]
    elif person_nodes:
        raise LookupError("Multiple people found")
    else:
        return None

def get_or_create_person(name):
    """ Now, if the person doesn't exist, create them and return the new node
    instead.
    """
    person_nodes = people.get("name", name)
    if len(person_nodes) == 1:
        return person_nodes[0]
    elif person_nodes:
        raise LookupError("Multiple people found")
    else:
        return people.create("name", name, {"name": name})

def get_or_create_person_safely(name):
  :

pairs = nltk.sem.relextract.mk_pairs(doc.text)
reldicts = nltk.sem.relextract.mk_reldicts(pairs) #window as key
for rel in reldicts:
 print rel['subjtext'] + '==>' + rel['filler'] + '==>' + rel['objtext'] + '\n'
 # add to the graph
 

 
