import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import scatter_matrix
from pandas.plotting import parallel_coordinates


#------------------------File read------------------------------
filename= 'DataWeierstrass.csv'
array = []

with open(filename) as my_file:
    array = my_file.readlines()
        #print("File Read Start:", array)
    prof = []
    lec = []
    students = []
    exp = []
    moti = []
    pre = []
    over = []
    j=0
    temp_prof= []
    temp_lec= []
    temp_over=[]
    model= []

    for i in range(1,len(array)):
        every_line_array= array[i].split(';')
        temp_prof.append(every_line_array[j])
        temp_lec.append(every_line_array[j+1])
        students.append(float(every_line_array[j+2]))
        exp.append(float(every_line_array[j+3]))
        moti.append(float(every_line_array[j+4]))
        pre.append(float(every_line_array[j+5]))
        temp_over.append(every_line_array[j+6])
        model.append(float(i+1))

for j in range(len(temp_prof)):
    prof.append(float(temp_prof[j][4:]))

#print(prof)
for j in range(len(temp_lec)):
    lec.append(float(temp_lec[j][7:]))

for j in range(len(temp_over)):
    over.append(float(temp_over[j][:-1]))


#------------------------Data Frame-----------------------------

df = {'Professor': prof, 'lectures': lec,'participants': students, 'expertise': exp, 'motivation': moti,'presentation': pre,'overall': over}
data=pd.DataFrame(df)
print(data)

#------------------------Scatter Matrix-----------------------------
color_wheel = {1: "#0392cf",
               2: "#7bc043",
               3: "#ee4035"}
scatter_matrix(data, alpha=0.2, figsize=(8, 8), diagonal='kde')
plt.savefig('Scatter Matrix of assignment 4.png')
plt.show()

#------------------------Parallel Matrix-----------------------------
data['Model'] = model
print(df)
parallel_coordinates(data,'Model')
plt.title("Parallel Co-ordinates")
plt.yscale('log')
plt.savefig('Parallel Coordinates of assignment 4.png')
plt.show()