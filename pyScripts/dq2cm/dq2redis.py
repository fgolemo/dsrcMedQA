# DSRC-quad2cm

import redis, re, sys, mmap, time
from sys import stdout

if(len(sys.argv) != 2):
	print 'dq2redis.py <inputfile>'
	sys.exit(2)


# result = prog.match(string)

class NQtoRedis():
	avgTimePerMilliPercent = []
	lastTime = time.time()
	startTime = lastTime
	r = None
	matcher = None
	oldProgress = -1.0
	lines = 0
	filename = ""

	def __init__(self, filename):
		self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
		self.matcher = re.compile('(<.+>) (<.+>) (<.+>) <.+>')
		self.filename = filename

	def mapcount(self):
	    f = open(self.filename)
	    buf = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
	    lines = 0
	    readline = buf.readline
	    while readline():
	        lines += 1
	    self.lines = lines

	def printProgress(self,i):
		progress = round(i*1.0 / self.lines * 100, 1)
		if (self.oldProgress != progress):
			timeDiff = time.time() - self.lastTime
			self.lastTime = time.time()
			self.avgTimePerMilliPercent.append(timeDiff)
			avgTime = sum(self.avgTimePerMilliPercent) / float(len(self.avgTimePerMilliPercent))
			runTime = avgTime * 1000 / 60
			tFormat = "min"
			if (runTime > 120):
				runTime /= 60
				tFormat = "h"
			stdout.write('\r' + str(progress) + '% estimated runtime: ' + str(round(runTime,1)) + tFormat)
			stdout.flush()
			self.oldProgress = progress

	def readFile(self):
		self.mapcount()
		i = 0
		with open(self.filename) as f:
			lastKeyStoreIndex = self.r.get('dq2cm-keysIndices')
			if (lastKeyStoreIndex == None):
				lastKeyStoreIndex = 1
			else:
				lastKeyStoreIndex = int(lastKeyStoreIndex) + 1
				self.r.incr('dq2cm-keysIndices')
			sizeCheckIndex = 0
			print("starting with key store index:"+str(lastKeyStoreIndex))
			for line in f:
				quad = self.matcher.match(line)
				#print(line)
				self.printProgress(i)
				if (quad):
					first, second = 1, 3
					if (quad.group(1) > quad.group(3)):
						first, second = 3, 1
					key = quad.group(first) + " " + quad.group(second)
					count = self.r.incr(key)
					if (count == 1):
						sizeCheckIndex += 1
						if (sizeCheckIndex == 10000):
							sizeCheckIndex = 0
							if (sys.getsizeof(self.r.get('dq2cm-keys'+str(lastKeyStoreIndex))) > 500000000):
								# it maxes out at 512MB
								lastKeyStoreIndex += 1
								self.r.incr('dq2cm-keysIndices')
								print("\nredis key store is full, increasing index: "+str(lastKeyStoreIndex))

						self.r.append('dq2cm-keys'+str(lastKeyStoreIndex),'\%\%\%'+key)
						self.r.append('dq2cm-keys-unique'+str(lastKeyStoreIndex)," "+key)
				i += 1
				# if (i == 10000):
				# 	break

		print(' ')
		print('total lines processed: '+ str(i))
		print('redis keys: '+ str(self.r.dbsize()) )

if __name__ == '__main__':

	# input file: C:\Users\Florian\Downloads\bio2rdf-data\drugbank_drugs.nq
	print('Counting connections... may take a while')
	nq2r = NQtoRedis(sys.argv[1])
	nq2r.readFile()
	print(' ')
	print('Finished! :)')
	
