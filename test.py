	# Q&A system . Who? What? Where? When? Why? Does/did?
	#

	import nltk
	import re

	from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk
	from nltk.sem import relextract

	IN = re.compile(r'.*\bin\b')
	TO = re.compile(r'.*\bto\b')

	def preprocesses(document):

	    sentences = nltk.sent_tokenize(document)
	    print 'sentences tokenized'
	    sentences = [nltk.word_tokenize(sent) for sent in sentences]
	    print 'words tokenized'
	    sentences = [nltk.pos_tag(sent) for sent in sentences]
	    print 'POS tagging done'
	    return sentences

	def NNPchunker(chunks):
	     grammar = r"""
			NP:{<DT|PP\$>?<JJ>*<NN>}
			   {<NNP>+}
			"""
	     cp = nltk.RegexpParser(grammar)
	     chunks =  [cp.parse(chunk) for chunk in chunks]
	     for chunk in chunks:
	       tree = cp.parse(chunk)
	      # tree.draw()
	      # raw_input('Press <ENTER> to continute')
	     return chunks

	def extract_people_in_locations(chunks):
	    print 'extracting relations'
	    class doc(): pass
	    doc.headline = ['This is expected but not used']
	    doc.text = ne_chunk(chunks)
	    for rel in nltk.sem.extract_rels('','',doc,corpus='ieer',pattern=IN):
		print 'checking'
		print rel['subjtext'] + rel['filler'] + rel['objtext']


	def extract_entitites (text):
	    entities = []
	    for sentence in sent_tokenize(text):
		chunks = ne_chunk(pos_tag(word_tokenize(sentence)))
		print chunks
		#entities.extend([chunk for chunk in chunks if hasattr(chunk,'node')])
	    return entities


	def main(argv):
	    print argv
	    break
	    f = open(filename,'rU')
	    raw = f.read()
	    chunks = preprocesses(raw)
	    chunks = NNPchunker(chunks)
	    pairs = relextract.mk_pairs(chunks)
	    reldicts = relextract.mk_reldicts(pairs)
            for r in reldicts:
             print ('=' * 20 )
             print(r['subjtext'])
             print(r['filler'])
             print(r['objtext'])

        #extract_people_in_locations(chunks)

        #extract_entitites(raw)

        if __name__ == '__main__':
         main(sys.argv[1:])
