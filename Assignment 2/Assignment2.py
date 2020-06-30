import numpy as np
from matplotlib import pyplot as plt
import collections

grid = plt.GridSpec(2, 2)
fig, ax = plt.subplots()
fig.set_size_inches(8, 8)
dataArr = []
#--------------File reading-------------------
with open("slice150.raw", "rb") as f:
	byte = f.read(2)
	while byte:
		byte    = f.read(2)
		byteInt = int.from_bytes(byte, byteorder='little')
		dataArr.append(byteInt)

print(str(len(dataArr)))
print("data arrays")
#print(str(dataArr))
B = np.reshape(dataArr, (512, 512))
#print(B)
#--------------Profile line-------------
row= str(len(B))
#cols = str(B[0])
cols = len(list(zip(*B)))

def getLine(y,B):
	return B[y*512:y*512+512]

print(int(row))
print(int(cols))

A=getLine(256,dataArr)
plt.plot(A)
plt.title("Profile Line through the Center Line")

plt.savefig('profileline.png')
plt.show()
#---------mean and variance-----------------
mean= np.mean(dataArr)
print("Mean=",mean)
variance= np.var(dataArr)
print('variance=', variance)
outputfile = open("Assignment2.txt", 'w')
outputstring = "Mean= " + str(mean) + "\n" + "Variance= " + str(variance)
outputfile.write(outputstring)
outputfile.close()
#-------------Histogram---------------------

data_dist = {}
for i in dataArr:
    data_dist[i] = data_dist.get(i, 0) + 1
data_dist = collections.OrderedDict(sorted(data_dist.items()))
occurrence = list(data_dist.values())
unique_values = list(data_dist.keys())
plt.plot(unique_values, occurrence)

#bin =np.unique(dataArr)
#print("bin:",len(bin))
#histo= np.histogram(dataArr)
#plt.hist(dataArr,bin,histtype = 'step')
plt.title("Histogram of 2D Data Set")
plt.savefig('Histogram.png')
plt.show()

#-------------------------Linear Transformation---------------------
min= min(dataArr)
max= max(dataArr)
print('rmin=',min, 'rmax=',max)

s = []
for n in range(len(dataArr)):
	s.append(int(dataArr[n]*255)/2123)

snew=[]
snew = np.reshape(s, (512, 512))
ax2 = plt.subplot(grid[0, 0])
ax2.imshow(np.flipud(snew),cmap='gray', origin='lower',aspect='auto')
plt.title("2(d): Linear Transformation")
#plt.colorbar(orientation='vertical')
#plt.savefig('Linear Transformation.png')
#plt.show()

#----------------non-linear Transformation from https://www.cse.unr.edu/~looney/cs674/unit2/unit2.pdf--------------------
transformedval = []
for val in dataArr:
	nonlinearVal = 31.875 * np.log(val + 1)
	transformedval.append(nonlinearVal)
ax3 = plt.subplot(grid[1, 0])
ax3.imshow(np.reshape(transformedval, (512, 512)), cmap='gray', origin='lower',aspect='auto')
plt.title("2(e): Non-Linear Transformation")


#---------------Smoothing Filter-----------
boxcar_filter = np.empty([501, 501])
for i in range(501):
    for j in range(501):
        t = 0
        for k in range(11):
            for l in range(11):
                t = t + B[i+k][j+l]
        boxcar_filter[i][j] = int(t/(11*11))
plt.subplot(grid[1, 1])
plt.imshow(boxcar_filter, cmap='bone', origin='lower',aspect='auto')
plt.title('2(f): Boxcar Filter')
#plt.colorbar(orientation='vertical')

#----------------Median Filter--------------
median_filter = np.empty([501, 501])
for i in range(501):
    for j in range(501):
        temp = []
        for k in range(11):
            for l in range(11):
                temp = np.append(temp, B[i+k][j+l])
        temp.sort()
        median_filter[i][j] = temp[60]
plt.subplot(grid[0, 1])
#plt.set_aspect('equal')
plt.imshow(median_filter, cmap='bone', origin='lower',aspect='auto')
plt.title('2(g): Median Filter')
#plt.colorbar(orientation='vertical')
plt.savefig("Assignment2-1.png",dpi=4096)
plt.gca().set_aspect('auto');
plt.show()

