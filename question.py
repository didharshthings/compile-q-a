from nltk import ne_chunk,pos_tag
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.treebank import TreebankWordTokenizer
import re
import nltk
from py2neo import neo4j
from py2neo import cypher


def main():

    text = raw_input('Enter a question...\n')
    print text
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
    for sentence in PunktTokenizer.tokenize(text):
            chunks = ne_chunk(pos_tag(TreeBankTokenizer.tokenize(sentence)))
            for chunk in chunks:
             if hasattr(chunk,'node'):
                tmp_tree = nltk.Tree(chunk.node, [(''.join(c[0] for c in chunk.leaves()))])
                tokens.append(tmp_tree)
             else:
                tokens.append(chunk[0])
            entities.extend([chunk for chunk in chunks if hasattr(chunk,'node')])

            #print chunks



    print tokens
    #entities dict
    entities_dict = {}
    for entity in entities:
        leaves = entity.leaves()
        if len(leaves) > 1 :
         entities_dict[entity.leaves()[0][0]+entity.leaves()[1][0]] = entity.node
        else :
         entities_dict[entity.leaves()[0][0]] = entity.node

    print entities_dict

    class doc():pass
    doc.headline=['']
    doc.text = tokens



  # Q&A answering algorithm
    #  Find the type of question
    qId = ''
    for key in qIdentifiers.keys():
      if key in str(text):
         print key
         qId = qIdentifiers[key]
    #  Find what kind of answer is required
    answerType = qId
    #  Find start node
    start_node = entities_dict.keys()[0]
    start_node_type = entities_dict[start_node]
    #  Run string similarity between relation text and question text
       # for the time being reading from the file

    #  Build query
    cypherQuery = "START me=node:objects(name='" + start_node + "') MATCH me-[r]->obj  RETURN r,obj.name LIMIT 10 "
    #  Start Graph traversal
    query = neo4j.CypherQuery(graph_db, cypherQuery)
    for record in query.stream():
      print 'printing records'
      print record[0]
      print record[1]
      print '\n'
    #  Traverse till the Entity is wrong



if __name__ == '__main__':
    main()
