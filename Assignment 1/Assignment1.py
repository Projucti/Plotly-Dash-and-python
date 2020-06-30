import matplotlib.pyplot as plot
import numpy as np

#https://stackoverflow.com/questions/3277503/how-to-read-a-file-line-by-line-into-a-list
#https://stackabuse.com/read-a-file-line-by-line-in-python/
with open('field2.irreg.txt') as my_file:
    array = my_file.readlines()
    print("File Read Start:", array)


i = 6 #data started from 6 lines in the data file field2.irreg

min_arr = []
while i < len(array):
    min_arr.append(array[i])
   # print(array[i])
    i += 1
#print(min_arr)

small_array= []
X = []
Y = []
dX = []
dY = []
j=0
while j < len(min_arr):
    small_array = min_arr[j].split(" ")
    X.append(float(small_array[0]))
    Y.append(float(small_array[1]))
    dX.append(float(small_array[3]))
    dY.append(float(small_array[4]))
    print("Line",j,":",small_array)
    j += 1

#ref: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.quiver.html
distx = np.add(X,dX)
disty = np.add(Y,dY)
colors = np.arctan2(disty, distx)
plot.quiver(X, Y, dX, dY, colors, pivot="tail",scale_units='xy',angles='xy',scale=6)
plot.title("Movement of Water Particle(caused by winds)[scaled by 6]")
plot.colorbar(orientation='vertical')
#ref:https://chartio.com/resources/tutorials/how-to-save-a-plot-to-a-file-using-matplotlib/
plot.savefig('Water_Movement.png', bbox_inches='tight')
plot.show()