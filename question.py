 # parsing questions


import nltk
from nltk import load_parser


cp = load_parser('grammars/book/sql0.cfg')

query = "What cities are located in China"

trees = cp.nbest_parse(query.split())
answer = trees[0].node['sem']
print answer

