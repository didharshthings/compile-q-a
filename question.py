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
graph_db = neo4j.GraphDatabaseService()
batch = neo4j.WriteBatch(graph_db)
		
TreeBankTokenizer = TreebankWordTokenizer()
PunktTokenizer = PunktSentenceTokenizer()

f = open('questions.txt','rU')
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

pairs = nltk.sem.relextract.mk_pairs(doc.text)
reldicts = nltk.sem.relextract.mk_reldicts(pairs) #window as key


