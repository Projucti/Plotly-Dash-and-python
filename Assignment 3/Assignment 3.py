import numpy as np
from matplotlib import pylab as plt
import math


#------------------------File read------------------------------
filename= 'i170b2h0_t0.txt'
array = []
def file_read(filename):
    with open(filename) as my_file:
        array = my_file.readlines()
        #print("File Read Start:", array)
    i=0
    result_array=[]
    j=0
    for i in range(len(array)):
        splited_array= array[i].split(',')
        for j in range(len(splited_array)):
                value= splited_array[j]
                value=value[1:]
                if(j==len(splited_array)-1):
                    value= value[:-2]
                value=value[:-1]
                result_array.append(float(value))



    print(len(result_array))
    return result_array
#------------------------Assignment 3(a)------------------------

result_array=file_read(filename)
maximum_value= np.max(result_array)
print('Maximum value = ',maximum_value)
minimum_value= np.min(result_array)
print('Minimum value = ',minimum_value)
mean= np.mean(result_array)
print('Mean = ',mean)
variance= np.var(result_array)
print('Variance = ',variance)


#------------------------Assignment 3(b)--------------------------
result_array=file_read(filename)
B = np.reshape(result_array, (500, 500))
row= str(len(B))
cols = len(list(zip(*B)))
def getLine(y,B):
	return B[y*500:y*500+500]
A=getLine(431,result_array)
plt.plot(A)
plt.xlabel("Pixel values")
plt.ylabel("Frequency")
plt.title("Profile Line through the Line which holds maximum value")
plt.savefig('profile line of assignment 3.png')
plt.show()

#------------------------Assignment 3(c)----------------------------
result_array=file_read(filename)
unique_value,count_unique_value=np.unique(result_array,return_counts=True)
print(len(unique_value))
print(count_unique_value)
plt.plot(math.log(unique_value,count_unique_value))
plt.xlabel("Pixel values")
plt.ylabel("Frequency")
plt.title("Histogram of 2D Data Set")
plt.savefig('Histogram of Assignment 3.png')
plt.show()


#------------------------Assignment 3(d) ------------------------------
filename2= 'i170b2h0_t0.txt'
result_array=file_read(filename2)
sp = []
#dif=maximum_value-minimum_value
for n in range(len(result_array)):
    if result_array[n]>=0 and result_array[n]<= mean:
        sp.append(result_array[n]*7)
    elif result_array[n]>=mean and result_array[n]<=10:
        sp.append(result_array[n]*15)
    else:
	    sp.append(int(155/(1+math.exp(-result_array[n]))))

snew_l=[]
snew_l = np.reshape(sp, (500, 500))
new_maximum_value= np.max(snew_l)
new_minimum_value= np.min(snew_l)

plt.imshow(np.flipud(snew_l),cmap='gray')
plt.title("Linear Transformation")
plt.xlabel("Pixel values along X axis")
plt.ylabel("Pixel values along Y axis")
plt.annotate("max-min",(new_minimum_value,new_maximum_value),textcoords="offset points", xytext=(0,10),ha='center')

plt.savefig('Linear Transformation.png')
plt.show()




#------------------------Histrogram Equilization------------------------------
def get_array(result_array):
        pdf=[]
        unique_value,count_unique_value=np.unique(result_array,return_counts=True)
        for n in range(len(count_unique_value)):
            pdf.append(count_unique_value[n]/250000)

        asd = 0
        cdf=[]
        for n in range(len(pdf)):
            asd += pdf[n]
            cdf.append(asd)
        #print(cdf)

        t=0
        l=0
        non_linear_array=[]
        for t in range(len(result_array)):
                temp= result_array[t]
                f_index= unique_value.tolist().index(temp)
                non_linear_array.append(cdf[f_index]*255)


        snew=[]
        snew = np.reshape(non_linear_array, (500, 500))
        #print(snew)
        return snew



#------------------------Assignment 3(e) part 1------------------------------
filename1= 'i170b1h0_t0.txt'
result_array=file_read(filename1)
snew1= get_array(result_array)
plt.imshow(np.flipud(snew1), cmap='gray')
plt.title("Histogram Equalization of Figure 1")
plt.xlabel("Pixel values along X axis")
plt.ylabel("Pixel values along Y axis")
plt.savefig('Histogram Equalization of Figure 1.png')
plt.show()

#------------------------Assignment 3(e) part 2------------------------------
filename2= 'i170b2h0_t0.txt'
result_array=file_read(filename2)
snew2= get_array(result_array)
plt.imshow(np.flipud(snew2), cmap='gray')
plt.xlabel("Pixel values along X axis")
plt.ylabel("Pixel values along Y axis")
plt.title("Histogram Equalization of Figure 2")
plt.savefig('Histogram Equalization of Figure 2.png')
plt.show()

#------------------------Assignment 3(e) part 3------------------------------
filename3= 'i170b3h0_t0.txt'
result_array=file_read(filename3)
snew3= get_array(result_array)
plt.imshow(np.flipud(snew3), cmap='gray')
plt.xlabel("Pixel values along X axis")
plt.ylabel("Pixel values along Y axis")
plt.title("Histogram Equalization of Figure 3")
plt.savefig('Histogram Equalization of Figure 3.png')
plt.show()

#------------------------Assignment 3(e) part 4------------------------------
filename4= 'i170b4h0_t0.txt'
result_array=file_read(filename4)
snew4= get_array(result_array)
plt.imshow(np.flipud(snew4), cmap='gray')
plt.title("Histogram Equalization of Figure 4")
plt.xlabel("Pixel values along X axis")
plt.ylabel("Pixel values along Y axis")
plt.savefig('Histogram Equalization of Figure 4.png')
plt.show()

#------------------------Assignment 3(f) ------------------------------
rgb = np.zeros((500,500,3), 'uint8')
rgb[..., 0] = snew4
rgb[..., 1] = snew3
rgb[..., 2] = snew1
plt.imshow(np.flipud(rgb))
plt.xlabel("Pixel values along X axis")
plt.ylabel("Pixel values along Y axis")
plt.title("RGB image from Histo-Equalized Data")
plt.savefig('combined image.png')
plt.show()


