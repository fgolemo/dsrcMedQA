from scipy import io, sparse, uint8
import time, os, csv, sys, random

trials = 8
size = 100
results = []

print ("start")

with open('bigMatTest.results.csv', 'wb') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter=',',
		quotechar='"', quoting=csv.QUOTE_MINIMAL)
	
	for i in range(1, trials+1):

		print("round: "+str(i)+" start")
		timeStart = time.clock()
		sys.stdout.flush()

		A = sparse.dok_matrix((size,size), dtype=uint8)
		
		print("round: "+str(i)+" filling")
		sys.stdout.flush()

		for amount in range(int(size * 0.05)):
			A[random.randrange(size),random.randrange(size)] = random.randrange(1,20)
		
		print("round: "+str(i)+" writing")
		sys.stdout.flush()

		io.savemat("bigMatTest", A, appendmat=True, format='5', do_compression=True)

		timeEnd = time.clock()
		timeElapsed = timeEnd - timeStart
		filesize = os.path.getsize("./bigMatTest.mat")
		resultsLine = [size, timeElapsed, filesize/1024]
		results.append(resultsLine)
		spamwriter.writerow(resultsLine)

		A = None
		size *= 10
		os.remove("./bigMatTest.mat")
		print("round: "+str(i)+" finished")
		print("")


print(results)


    
    