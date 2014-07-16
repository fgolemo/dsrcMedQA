import cPickle as pickle

baseFilename = 'C:/Users/Florian/Downloads/bio2rdf-data/drugbank_drugs.nq'

vertexNames = pickle.load( open( baseFilename + '.vertexNames.p', "rb" ) )
connList = pickle.load( open( baseFilename + '.connList.p', "rb" ) )

print ('len vertexNames: ',len(vertexNames))
print ('len connList: ',len(connList))

print ('first 3 elements from vertexNames:')
print (vertexNames.keys()[:3])
print (vertexNames.values()[:3])
print ('first 3 elements from connList:')
print (connList[:3])
