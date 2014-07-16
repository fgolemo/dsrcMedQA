from pylab import *
import matplotlib.pyplot  as pyplot
import numpy as np

data = np.genfromtxt('bigMatTest.results.csv', delimiter=',', dtype=float)

# print (data[:6,0])
# print (data[:6,1])

fig = pyplot.figure()
ax = fig.add_subplot(2,1,1)
bx = fig.add_subplot(2,1,2)

line1, = ax.plot(data[:,0], data[:,1], color='blue', lw=2, marker='x')
line2, = bx.plot(data[:,0], data[:,2], color='red')

ax.set_xscale('log')
ax.set_yscale('log')
# ax.set_title("time per mat size")
ax.set_xlabel("size of each side of the square matrix")
ax.set_ylabel("CPU time in seconds")
bx.set_xscale('log')
bx.set_yscale('log')
# bx.set_title("matlab filesize per mat size")
bx.set_xlabel("size of each side of the square matrix")
bx.set_ylabel("file size in kB")

ax.grid()
bx.grid()
show()