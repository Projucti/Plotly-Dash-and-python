import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

from matplotlib import ticker
from  matplotlib import colors as cl
import matplotlib.cm as cm
from matplotlib import markers as marker
def plotparallelcoordinate(pandadf, coloumns, min_max_range, normalizeddf):
    x = [i for i, _ in enumerate(coloumns)]
    fig, axes = plt.subplots(1, len(coloumns) - 1, sharey=False, figsize=(25, 15),
                             gridspec_kw={'wspace': 0, 'hspace': 0})

    for i, ax in enumerate(axes):
        for idx in pandadf.index:
            ax.plot(x, normalizeddf.loc[idx, coloumns])
        ax.set_xlim([x[i], x[i + 1]])

    for dim, ax in enumerate(axes):
        ax.xaxis.set_major_locator(ticker.FixedLocator([dim]))
        min_val, max_val, val_range = min_max_range[coloumns[dim]]
        arr = normalizeddf[coloumns[dim]]
        ticks = len(np.unique(arr))
        step = val_range / float(ticks - 1)
        tick_labels = [round(min_val + step * i, 2) for i in range(ticks)]
        norm_min = normalizeddf[coloumns[dim]].min()
        norm_range = np.ptp(normalizeddf[coloumns[dim]])
        norm_step = norm_range / float(ticks - 1)
        ticks = [round(norm_min + norm_step * i, 2) for i in range(ticks)]
        ax.yaxis.set_ticks(ticks)
        if coloumns[dim] == 'professor_cat':
            ax.set_yticklabels(np.unique(pandadf['professor']))
        elif coloumns[dim] == "lecture_cat":
            ax.set_yticklabels(np.unique(pandadf['lecture']))
        else:
            ax.set_yticklabels(tick_labels)

        ax.set_xticklabels([coloumns[dim]])

    ax = plt.twinx(axes[-1])
    dim = len(axes)
    ax.xaxis.set_major_locator(ticker.FixedLocator([x[-2], x[-1]]))
    # set_ticks_for_axis(dim, ax, ticks=6)
    min_val, max_val, val_range = min_max_range[coloumns[dim]]
    ticks = len(x)
    step = val_range / float(ticks - 1)
    tick_labels = [round(min_val + step * i, 2) for i in range(ticks)]
    norm_min = normalizeddf[coloumns[dim]].min()
    norm_range = np.ptp(normalizeddf[coloumns[dim]])
    norm_step = norm_range / float(ticks - 1)
    ticks = [round(norm_min + norm_step * i, 2) for i in range(ticks)]
    ax.yaxis.set_ticks(ticks)
    ax.set_yticklabels(tick_labels)
    ax.set_xticklabels([coloumns[dim]])
    ax.set_xticklabels([coloumns[-2], coloumns[-1]])
    plt.savefig('parallelcoordinate.png', dpi=72)
    plt.show()


def scatterplot_matrix(data, names, min_max_range,originaldf,**kwargs):
    numvars, numdata = data.shape
    #data = data.as_matrix()
    #data = data.astype(str)
    fig, axes = plt.subplots(nrows=len(names), ncols=len(names), figsize=(25, 25),sharex=False,sharey=False)
    fig.subplots_adjust(hspace=0.1, wspace=0.1)
    cmap = cm.get_cmap('Paired')
    norm = plt.Normalize()
    professorsArray = np.array(originaldf['professor_cat'])
    marker = np.array(originaldf['professor_cat'])
    face = []
    for i in range(1, len(professorsArray)):
        marker[i] = marker[i] * 20
        face.append(i)
    colors = cmap(norm(professorsArray))
    lines= []
    for ax in axes.flat:
        # Hide all ticks and labels
        # Set up ticks only on one side for the "edge" subplots...
        if ax.is_first_col():
            ax.yaxis.set_ticks_position('left')
        elif ax.is_last_col():
            ax.yaxis.set_ticks_position('right')
        else:
            ax.yaxis.set_visible(False)
            #ax.xaxis.set_visible(False)
        if ax.is_first_row():
            #ax.yaxis.set_visible(False)
            ax.xaxis.set_ticks_position('top')
        elif ax.is_last_row():
            ax.xaxis.set_ticks_position('bottom')
        else:
            ax.xaxis.set_visible(False)

    # Plot the data.
    k = 0
    for i, j in zip(*np.triu_indices_from(axes, k=1)):
        for x, y in [(i, j), (j, i)]:
            rowval = names[y]
            colval = names[x]
            x_min_val, x_max_val, x_val_range = min_max_range[rowval]
            y_min_val, y_max_val, y_val_range = min_max_range[colval]
            x_arr = data[rowval]
            y_arr = data[colval]
            x_ticks = 5
            y_ticks = 5
            x_step = x_val_range / float(x_ticks - 1)
            y_step = y_val_range / float(y_ticks - 1)
            x_tick_labels = [round(x_min_val + x_step * i, 2) for i in range(x_ticks)]
            y_tick_labels = [round(y_min_val + y_step * i, 2) for i in range(y_ticks)]
            x_norm_min = data[rowval].min()
            y_norm_min = data[colval].min()
            x_norm_range = np.ptp(data[rowval])
            y_norm_range = np.ptp(data[colval])
            x_norm_step = x_norm_range / float(x_ticks - 1)
            y_norm_step = y_norm_range / float(y_ticks - 1)
            x_ticks = [round(x_norm_min + x_norm_step * i, 2) for i in range(x_ticks)]
            y_ticks = [round(y_norm_min + y_norm_step * i, 2) for i in range(y_ticks)]
            if rowval == 'professor_cat':
                j=0
                for val in x_tick_labels:
                    val = int(val)
                    professors = np.unique(originaldf['professor'])
                    x_tick_labels[j] = professors[val]
                    j=j+1
            if colval == 'professor_cat':
                j = 0
                for val in y_tick_labels:
                    val = int(val)
                    professors = np.unique(originaldf['professor'])
                    y_tick_labels[j] = professors[val]
                    j = j + 1
            if rowval == 'lecture_cat':
                j = 0
                for val in x_tick_labels:
                    val = int(val)
                    lectures = np.unique(originaldf['lecture'])
                    x_tick_labels[j] = lectures[val]
                    j = j + 1
            if colval == 'lecture_cat':
                j = 0
                for val in y_tick_labels:
                    val = int(val)
                    lectures = np.unique(originaldf['lecture'])
                    y_tick_labels[j] = lectures[val]
                    j=j+1
            axes[x, y].yaxis.set_ticks(y_ticks)
            axes[x, y].xaxis.set_ticks(x_ticks)
            axes[x, y].set_xticklabels(x_tick_labels,rotation= 75)
            axes[x, y].set_yticklabels(y_tick_labels)

            axes[x, y].scatter(x_arr, y_arr,c=colors,label=np.array(originaldf['professor']))
            k = k + 1


            #plt.setp(axes[x, y].get_xticklabels(), rotation=30, horizontalalignment='right')

        # Label the diagonal subplots...
    for i, label in enumerate(names):
        if label == 'professor_cat':
            label = 'professor'
        if label == 'lecture_cat':
            label = 'lecture'
        axes[i, i].annotate(label, (0.5, 0.5), xycoords='axes fraction',
                            ha='center', va='center')
        axes[i, i].xaxis.set_visible(False)
        axes[i, i].yaxis.set_visible(False)
        # Turn on the proper x or y axes ticks.
    #handles, labels = axes[x, y].data.values(),axes[x, y].data.values()
    #fig.legend(colors,np.unique(professors))
    plt.savefig('scattermatrix.png', dpi=72)
    plt.show()


def doFourthAssignment():
    sns.set(style="ticks", color_codes=True)

    pandadf = pd.read_csv("DataWeierstrass.csv", delimiter=";")
    obj_df = pandadf.select_dtypes(include=['object']).copy()
    obj_df["professor"] = obj_df["professor"].astype('category')
    obj_df["lecture"] = obj_df["lecture"].astype('category')
    obj_df["professor_cat"] = obj_df["professor"].cat.codes
    obj_df["lecture_cat"] = obj_df["lecture"].cat.codes

    pandadf.insert(2, column='professor_cat', value=obj_df['professor_cat'], allow_duplicates=True)
    pandadf.insert(3, column='lecture_cat', value=obj_df['lecture_cat'], allow_duplicates=True)

    coloumns = ['professor_cat', 'lecture_cat', 'participants', 'professional expertise', 'motivation',
                'clear presentation', 'overall impression']
    min_max_range = {}
    normalizedpandadf = pd.DataFrame()
    for col in coloumns:
        min_max_range[col] = [pandadf[col].min(), pandadf[col].max(), np.ptp(pandadf[col])]
        normalizedpandadf[col] = np.true_divide(pandadf[col] - pandadf[col].min(), np.ptp(pandadf[col]))
    plotparallelcoordinate(pandadf,coloumns, min_max_range, normalizedpandadf)

    scatterplot_matrix(normalizedpandadf,  coloumns, min_max_range, pandadf,linestyle='none', marker='o', color='black', mfc='none')



def main():
    doFourthAssignment()


if __name__ == '__main__':
    main()
