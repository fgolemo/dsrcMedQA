def uniquify(seq):
	seen = set()
	seen_add = seen.add
	return [ x for x in seq if not (x in seen or seen_add(x))]

def printMatrix(mat):
	print '\n'.join([' '.join(str(row)) for row in mat])

def makeHeaders(mat, keys):
	mat = [keys] + mat
	printMatrix(mat)
	return mat

def fillMatrix(mat, keys, data):
	for y in range(len(keys)):
		for x in range(y, len(keys)):
			key = keys[y] + ' ' + keys[x]
			if(key in data):
				mat[y][x] = data[key]	
			# mat[y][x] = str(x)+','+str(y)
	return mat

def writeFile(mat, filename):
	import csv
	with open(filename, 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',',
		                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for y in range(len(mat)):
			writer.writerow(mat[y])

def writeOutput():
	d = {'a a' : 3, 'a b' : 1, 'a f' : 5, 'c d' : 7}
	ins = 'a a c c a c b d a d f a c'
	keys = uniquify(ins.split(' '))
	keys.sort()
	mat = [[0 for y in range(len(keys))] for x in range(len(keys))]
	fillMatrix(mat, keys, d)
	mat = makeHeaders(mat, keys)
	writeFile(mat, 'eggs.csv')

if __name__ == '__main__':
	writeOutput()