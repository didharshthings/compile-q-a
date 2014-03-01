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

#print entities
for entity in entities:
    print entity.node
    raw_input ('stop-observe')

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
print tokens	 
raw_input ('press enter to continute')
class doc():pass
doc.headline=['']
doc.text = tokens

#for rel in nltk.sem.extract_rels('PERSON','LOCATION', doc, corpus='ieer', pattern = IN):
# print nltk.sem.relextract.show_raw_rtuple(rel)  

#doc.text=[nltk.Tree('ORGANIZATION', ['WHYY']), 'in', nltk.Tree('LOCATION',['Philadelphia']), '.', 'Ms.', nltk.Tree('PERSON', ['Gross']), ',']
# doc.text = [Tree('ORGANIZATION', ['WHYY']), 'in', Tree('LOCATION', ['Philadelphia']), '.', 'Ms.', Tree('PERSON', ['Gross']), ',']
#for rel in  nltk.sem.extract_rels('ORG','LOC',doc,corpus='ieer',pattern=IN):
  # print nltk.sem.relextract.show_raw_rtuple(rel)


pairs = nltk.sem.relextract.mk_pairs(doc.text)
reldicts = nltk.sem.relextract.mk_reldicts(pairs) #window as key
#creating a Knowledge Graph sort of thing
entities = graph_db.get_or_create_index(neo4j.Node,"objects")

def get_or_create_entity(name):
		 nodes = entities.get("name", name)
		 if len(nodes) == 1:
		  return nodes[0]
	     #elif nodes:
		  #raise LookupError("Multiple people found")
		 else:
			return entities.create("name", name, {"name": name})

relations = {}
relId = 0
for rel in reldicts:
 subjtext = rel['subjtext']
 objtext  = rel['objtext']
 filler   = rel['filler']
 relations[relId] = filler 
# print rel['subjtext'] + '==>' + rel['filler'] + '==>' + rel['objtext'] + '\n'
 #subjText = entities.create_if_none("name",subjtext,{})
 #objText  = entities.create_if_none("name",objtext,{})
 #relation = neo4j.Path(subjText,filler,objText)
 subjTextNode = get_or_create_entity(subjtext)
 objTextNode  = get_or_create_entity(objtext)
 subjTextNode.get_or_create_path(relId,objTextNode)
 relId = relId+1    
 #batch.get_or_create_relationship(subjTextNode, filler , objTextNode)
 #relations = neo4j.Path((subjTextNode , filler , objTextNode))
 #path = relations.create(graph_db)

print relations
rels = batch.submit()

 

