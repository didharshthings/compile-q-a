from nltk import ne_chunk,pos_tag
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.treebank import TreebankWordTokenizer
import re
import nltk
from py2neo import neo4j
from py2neo import cypher
from nltk import ne_chunk,pos_tag
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.treebank import TreebankWordTokenizer
import string
from difflib import SequenceMatcher


def main():

    def question():
        # question asking part
        qText = raw_input('Enter a question...\n')
        graph_db = neo4j.GraphDatabaseService()
        batch = neo4j.WriteBatch(graph_db)

        TreeBankTokenizer = TreebankWordTokenizer()
        PunktTokenizer = PunktSentenceTokenizer()


        qIdentifiers = {
                        "What": ' ',
                        "Who": 'PERSON',
                        "Where": 'GPE',
                        "When": 'TIME',
                        "Why":'',
                        "How":''
                        }
        entities = []
        tokens = []
        for sentence in PunktTokenizer.tokenize(qText):
                chunks = ne_chunk(pos_tag(TreeBankTokenizer.tokenize(sentence)))
                for chunk in chunks:
                 if hasattr(chunk,'node'):
                    tmp_tree = nltk.Tree(chunk.node, [(''.join(c[0] for c in chunk.leaves()))])
                    tokens.append(tmp_tree)
                 else:
                    tokens.append(chunk[0])
                entities.extend([chunk for chunk in chunks if hasattr(chunk,'node')])

                #print chunks



        #print tokens
        #entities dict
        entities_dict = {}
        for entity in entities:
            leaves = entity.leaves()
            if len(leaves) > 1 :
             entities_dict[entity.leaves()[0][0]+' '+entity.leaves()[1][0]] = entity.node
            else :
             entities_dict[entity.leaves()[0][0]] = entity.node

        #print entities_dict


      # Q&A answering algorithm
        #  Find the type of question
        qId = ''
        for key in qIdentifiers.keys():
          if key in str(qText):
             #remove key from text
             qText = qText.split(key)[1]
             print qText
             qId = qIdentifiers[key]
        #  Find what kind of answer is required
        answerType = qId
        # find relation closese to the question text
        maximum = 0.0
        queryRel = ''
        for rel in relations.keys():
            # do string comparison
            #score =  stringcomp(str(qText),str(relations[int(rel)]))
            score = SequenceMatcher(None,str(qText),str(relations[int(rel)])).ratio()
            if score > maximum :
                maximum = score
                queryRel = "`"+str(rel)+"`"

        #print queryRel
        #  Find start node
        try:
            start_node = entities_dict.keys()[0]
        except Exception, err:
            print 'No entity found in the question'
            question()


        qText = qText.split(start_node)
        #print ''.join(qText)
        start_node_type = entities_dict[start_node]

        getAnswersQuery = "Match a-[r:"+queryRel+"]->b return b"

        ansQuery = neo4j.CypherQuery(graph_db, getAnswersQuery)
        for record in ansQuery.stream():

           answer_node = str(record[0]).split('"')[3]

        #  Build query, checking whether the answer is related to question entity
        cypherQuery = "START me=node:objects(name='"+start_node+"') MATCH p=a-[r:"+queryRel+"*..]-d WHERE d.name='"+answer_node+"' RETURN d;"
        query = neo4j.CypherQuery(graph_db, cypherQuery)
        for record in query.stream():
          if len(record) > 1: # a relationship exists
           break


        print "The answer is..."
        print answer_node
        raw_input ('Press enter to ask more')
        question()

    #Creating a Knowledge Graph sort of thing
    graph_db = neo4j.GraphDatabaseService()
    batch = neo4j.WriteBatch(graph_db)

    TreeBankTokenizer = TreebankWordTokenizer()
    PunktTokenizer = PunktSentenceTokenizer()

    filename = raw_input("Enter file name\n")
    f = open(filename,'rU')
    raw = f.read()
    #normalize text
    for p in string.punctuation:
        if p != ',' :
            raw = raw.replace(p, '')
    raw = raw.strip()

    #IN = re.compile(r'.*\bin\b(?!\b.+ing)')
    tokens = []



    entities = []
    for sentence in PunktTokenizer.tokenize(raw):
            chunks = ne_chunk(pos_tag(TreeBankTokenizer.tokenize(sentence)))
            for chunk in chunks:
             if hasattr(chunk,'node'):

                tmp_tree = nltk.Tree(chunk.node, [(''.join(c[0] for c in chunk.leaves()))])
                tokens.append(tmp_tree)
             else:
                tokens.append(chunk[0])

            entities.extend([chunk for chunk in chunks if hasattr(chunk,'node')])

            #print chunks
    #raw_input('Press <enter> to continue')
    #print entities
    #entities dict
    entities_dict = {}

    for entity in entities:
        leaves = entity.leaves()
        if len(leaves) > 1 :
         entities_dict[entity.leaves()[0][0]+' '+entity.leaves()[1][0]] = entity.node
        else :
         entities_dict[entity.leaves()[0][0]] = entity.node


    print entities_dict


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


    pairs = nltk.sem.relextract.mk_pairs(doc.text)
    reldicts = nltk.sem.relextract.mk_reldicts(pairs) #window as key

    entities = graph_db.get_or_create_index(neo4j.Node,"objects")

    def get_or_create_entity(name):
             nodes = entities.get("name", name)
             if len(nodes) == 1:
              return nodes[0]
             #elif nodes:
              #raise LookupError("Multiple objects found")
             else:
                return entities.create("name", name, {"name": name})

    relations = {}
    relId = 0
    f = open('relations.txt','w')
    for rel in reldicts:
     subjtext = rel['subjtext']
     objtext  = rel['objtext']
     filler   = rel['filler']
     relations[relId] = filler
     f.write(
     str(rel['subjtext']) + '==>' + str(rel['filler'])+ '==>' + str(rel['objtext']) + '\n')

     #subjText = entities.create_if_none("name",subjtext,{})
     #objText  = entities.create_if_none("name",objtext,{})
     #relation = neo4j.Path(subjText,filler,objText)
     subjTextNode = get_or_create_entity(subjtext)
     objTextNode  = get_or_create_entity(objtext)
     relation = subjTextNode.get_or_create_path(str(relId),objTextNode)
     relId = relId+1
     #batch.get_or_create_relationship(subjTextNode, filler , objTextNode)
     #relations = neo4j.Path((subjTextNode , filler , objTextNode))
     #path = relations.create(graph_db)

    #print relations
    rels = batch.submit()
    f.close()
    question()
    #Do something for AND

if __name__ == '__main__':
    main()
