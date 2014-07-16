# DSRC-quad2cm

import redis, re, sys, mmap
from sys import stdout

if(len(sys.argv) != 2):
	print 'dq2redis.py <inputfile>'
	sys.exit(2)

r = redis.StrictRedis(host='localhost', port=6379, db=0)

matcher = re.compile('(<.+>) (<.+>) (<.+>) <.+>')
# result = prog.match(string)

def mapcount(filename):
    f = open(filename, "r+")
    buf = mmap.mmap(f.fileno(), 0)
    lines = 0
    readline = buf.readline
    while readline():
        lines += 1
    return lines

def printProgress(i, lines, oldProgress):
	progress = round(i*1.0 / lines * 100, 1)
	if (oldProgress != progress):
		stdout.write('\r' + str(progress) + '%')
		stdout.flush()
		oldProgress = progress
	return oldProgress

def readFile():
	filename = str(sys.argv[1])
	lines = mapcount(filename)
	i = 0
	oldProgress = -1.0
	with open(filename) as f:
		for line in f:
			quad = matcher.match(line)
			#print(line)
			oldProgress = printProgress(i, lines, oldProgress)
			if (quad):
				first, second = 1, 3
				if (quad.group(1) > quad.group(3)):
					first, second = 3, 1
				key = quad.group(first) + " " + quad.group(second)
				count = r.incr(key)
				if (count == 1):
					r.append('dq2cm-keys',",,"+key)
					r.append('dq2cm-keys-unique'," "+key)
			i += 1
			# if (i == 10000):
			# 	break

	print(' ')
	print('total lines processed: '+ str(i))
	print('redis keys: '+ str(r.dbsize()) )

if __name__ == '__main__':

	# input file: C:\Users\Florian\Downloads\bio2rdf-data\drugbank_drugs.nq
	print('Counting connections... may take a while')
	readFile()
	print(' ')
	print('Finished! :)')
	
