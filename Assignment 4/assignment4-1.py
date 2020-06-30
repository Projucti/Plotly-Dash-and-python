import numpy as np
import collections
import math
from matplotlib import pylab as plt
import pandas as pd
from scipy.stats import gaussian_kde
from pandas.plotting import scatter_matrix, parallel_coordinates

DIM = 122

with open('DataWeierstrass.csv', "r") as f:
    content = f.readlines()

feedback = []
profs = []
lectures = []
participants = []
expertise = []
motivation = []
presentation = []
overall = []

x = 0
for i in range(1, len(content)):
    line = content[i]
    items = line.split(';')

    feedback.append(float(i + 1))
    profs.append(float(items[0][4:]))
    lectures.append(float(items[1][7:]))
    participants.append(float(items[2]))
    expertise.append(float(items[3]))
    motivation.append(float(items[4]))
    presentation.append(float(items[5]))
    overall.append(float(items[6][:-1]))


df = pd.DataFrame({'profs': profs, 'lectures': lectures,
                   'participants': participants, 'expertise': expertise, 'motivation': motivation,
                   'presentation': presentation, 'overall': overall},
                  columns=['profs', 'lectures', 'participants', 'expertise', 'motivation', 'presentation', 'overall'])

#df.profs = df.profs.astype('category')
#df['profs_encoded'] = df.profs.cat.codes

#plt.figure(1)
scatter_matrix(df, alpha=0.2, figsize=(8, 8), diagonal='kde')
plt.show()

df['feedback'] = feedback
print(df)

plt.figure(2)
parallel_coordinates(df, 'feedback')
plt.yscale('log')
plt.show()
