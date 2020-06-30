import pandas as pd
import plotly.express as px
import matplotlib.cm as cm
import seaborn as sns
from matplotlib import pyplot as plt



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

#------------------------Parallel Matrix-----------------------------

fig = px.parallel_coordinates(data,dimensions=['lectures','participants','expertise','motivation','presentation','overall','Professor'],
                              color='Professor',title="Parallel Mattrix of Evaluation Data from DataWeierstrass.csv")
fig.show()

#------------------------Scatter Matrix-----------------------------


plt.style.use("seaborn")
plt.title('Scatterplot Mattrix of Evaluation Data from DataWeierstrass.csv')
g = sns.PairGrid(data, hue="Professor")
g.map(plt.scatter)
g.add_legend()
g.savefig("Scatter Matrix of assignment 4.png")


#------------------------other try of scatter mattrix-----------------------------

fig = px.scatter_matrix(data, dimensions=['lectures','participants','expertise','motivation','presentation','overall'],
                        color='Professor', title="Scatterplot Mattrix of Evaluation Data from DataWeierstrass.csv")

#fig.show()

