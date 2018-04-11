'''read the job posts'''

#general
import os
import itertools
import math

# drawing
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors

# import for data frame
from pandas import read_csv, read_json, Series
import pandas as pd


# map visualization
import folium

INH = {'WNA': 489204, 'WLX': 280327, 'VAN': 1824136, 'WBR': 396840,
       'VWV': 1181828, 'VLI': 863725, 'WHT': 1337157, 'VOV': 1486722,
       'WLG': 1098688, 'BRU': 1187890, 'VBR': 1121693}

def onmap(dataframe):
    test = folium.Map(location=[50.5039, 4.4699])
    coords = dataframe[['latitude', 'longitude', 'company']].values.tolist()
    for c in coords:
        #print(c[2])
        try:
            folium.Marker([c[0], c[1]], popup=c[2]).add_to(test)
        except:
            pass

    test.save('index.html')


def analysisjobs(offers):
    # transform date to datetime and pick the month
    offers['date'] = pd.to_datetime(offers['date'])
    offers['month'] = offers['date'].map(lambda x: x.month)
    offers.sort_values(by=['state'])
    # offers per month integrated over all provinces
    plt.figure("Integrated jobs per month")
    #offers.groupby('month', as_index=False)['jobtitle'].count()

    offers.groupby('month')['jobtitle'].count().plot()

    # group by month and state (province)
    off_state_month = offers.groupby(['state', 'month'],
                                     as_index=False)['jobtitle']\
                            .count().set_index(['month'])
    off_state_month['popul'] = Series([INH[k] for k in off_state_month['state']],
                                    index=off_state_month.index)
    print(type(off_state_month.popul))#, set(off_state_month.pop))
    off_state_month['njobdivpop'] = off_state_month.jobtitle / off_state_month.popul
    print("result", off_state_month[off_state_month['state'] == 'VLI'].head())
    # list of provinces
    states = set(offers['state'])
    print(states)
    plt.figure("Job offers per month")
    ax = plt.subplot(111)
    plt.figure("Normalized job offers per month")
    axn = plt.subplot(111)
    n_j_m = []
    # colors
    colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

    by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
    sorted_names = [name for hsv, name in by_hsv]
    print(sorted_names)
    # markers
    mk = itertools.cycle(('.', '^', 'p', 'X', '*', '8', 's', 'P'))
    mkl = ['.', '^', 'p', 'X', '*', '8', 's', 'P']
    iv, iw = -1, -1
    for i, s in enumerate(states):
        if not isinstance(s, str):
            continue
        print(s)
        #curmk = next(mk)
        if s == 'BRU':
            curmk = '+'
            curcl = 'cadetblue'
            curfacec = curcl
        elif s[0] == 'V':
            iv += 1
            curcl = 'magenta'  # sorted_names[iv+sorted_names.index('magenta')]
            curfacec = 'none'
            curmk = mkl[iv]
        else:
            iw += 1
            curcl = 'darkgoldenrod' #  sorted_names[iw+sorted_names.index('darkgoldenrod')]
            curfacec = curcl
            curmk = mkl[iw]

        n_j_m.append(off_state_month[off_state_month['state'] == s]\
        .plot(y='jobtitle', color=curcl, marker=curmk, markerfacecolor=curfacec,
             label=s, ax=ax))
        off_state_month[off_state_month['state'] == s]\
        .plot(y='njobdivpop', color=curcl, marker=curmk, markerfacecolor=curfacec,
             label=s, ax=axn)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    ax.set_ylabel("# jobs per month")
    handles, labels = axn.get_legend_handles_labels()
    axn.legend(handles, labels)
    axn.set_ylabel("# jobs per month / population")



def smalldataframe(filename='belgian_job_posts_2017.csv', nlines=100):
    df = read_csv(filename)
    small = df.head(nlines)
    small.to_csv('df_' + str(nlines) + '.csv')
    return small


def main():
    # df = read_csv('belgian_job_posts_2017.csv')
    try:
        offers = read_csv('belgian_job_posts_2017.csv')  # 'df_100.csv')
    except:
        offers = smalldataframe()
    print("========= Data description =========")
    print(offers.columns)
    #onmap(offers)

    print("offers from ", len(set(offers['company'])), "companies")
    print("Offers per province")
    print(offers.groupby('state', as_index=False)['jobtitle'].count())
    print("----------------------")

    analysisjobs(offers)

    curd = os.getcwd()
    print('file://localhost' + curd + '/bce_big_companies.jsonl')
    try:
        companies = read_json(path_or_buf='file://localhost' + curd +
                             '/bce_big_companies.jsonl',
                             lines=True)
    except:
        companies = None
        print("failed to read json")
    print(companies.columns)
    companies.to_csv('companies.csv')

    plt.show()

if __name__ == "__main__":
    main()