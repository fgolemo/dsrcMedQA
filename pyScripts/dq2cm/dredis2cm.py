# DSRC-quad2cm

import redis, re, sys, mmap
from sys import stdout
from scipy import io, sparse, uint8
from apgl.graph import SparseGraph
import cPickle as pickle

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def printProgress(i, lines, oldProgress):
	progress = round(i*1.0 / lines * 100, 1)
	if (oldProgress != progress):
		stdout.write('\r' + str(progress) + '%')
		stdout.flush()
		oldProgress = progress
	return oldProgress

def uniquify(seq):
	seen = set()
	seen_add = seen.add
	return [ x for x in seq if not (x in seen or seen_add(x))]

def fillMatrix(keys, hashes, filename):
	oldProgress = -1
	keyslen = len(keys)
	hasheslen = len(hashes)
	empty = False
	keyDict = dict(zip(keys, range(keyslen)))
	matrix = sparse.dok_matrix((keyslen,keyslen), dtype=uint8)
	connList = []
	for y in range(hasheslen):
		oldProgress = printProgress(y, hasheslen, oldProgress)
		# val = r.get(hashes[y])
		keys = hashes[y].split(' ')
		m,n = keyDict[keys[0]], keyDict[keys[1]]
		strength = r.get(hashes[y])
		connList.append([m,n,strength])
		matrix[m,n] = strength
	print("finished filling... now writing")
	sys.stdout.flush()
	io.savemat(filename + '.connMatrix', matrix, appendmat=True, format='5', do_compression=True)
	pickle.dump( matrix, open( filename + ".connMatrix.p", "wb" ) )
	pickle.dump( connList, open( filename + ".connList.p", "wb" ) )
	pickle.dump( keyDict, open( filename + ".vertexNames.p", "wb" ) )
	return matrix


def writeOutput():
	i = 1
	keys = []
	hashes = []
	keyString = r.get('dq2cm-keys-unique'+str(i))
	while (keyString != None and keyString != ""):
		print("found keys with index "+str(i))
		keys += uniquify(r.get('dq2cm-keys-unique'+str(i)).split(' '))
		if (i == 1):
			keys.pop(0)
		hashes += uniquify(r.get('dq2cm-keys'+str(i)).split(',,'))
		if (i == 1):
			hashes.pop(0)
		i+=1
		keyString = r.get('dq2cm-keys-unique'+str(i))
	keys.sort()
	hashes.sort()
	print("got a total of "+str(len(keys)) + " keys")
	filename = str(sys.argv[1])
	W = fillMatrix(keys, hashes, filename)
	print('Finished writing MAT file. Now check the output at: ' + filename)
	return (len(keys),W)

def graphInfo(keyslen, wheigts):
	graph = SparseGraph(keyslen, W=wheigts.tocsr())
	print('graph size:' + str(graph.size))
	print('graph density:' + str(graph.density()) )
	#print('graph distribution:')
	#print(graph.degreeDistribution()) # too memory-intense


if __name__ == '__main__':

	# input file: C:\Users\Florian\Downloads\bio2rdf-data\drugbank_drugs.nq
	print('Creating matrix... may take a while, too')
	matInfo = writeOutput()
	graphInfo(matInfo[0],matInfo[1])
	print(' ')
	print('Finished! :)')
