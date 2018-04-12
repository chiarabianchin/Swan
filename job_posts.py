'''read the job posts'''

#general
import os
import itertools
import numpy as np

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

def createdfactivity(df_companies):
    # create DataFrame for activities
    mindex = []
    nacodes = []
    activitygroups = []
    nacever = []
    clas = []
    for comp in df_companies['EntityNumber']:
        for act in df_companies[df_companies['EntityNumber'] == comp]['activities']:
            mindex.append(list(zip([comp] * len(act),
                          list(range(0, len(act))))))

            #nacodes[comp] = {i: [a['NaceCode'], a['ActivityGroup'],
             #                  a['NaceVersion'], a['Classification']]
             #              for i, a in enumerate(act)}
            nacodes.append([a['NaceCode'] for i, a in enumerate(act)])
            activitygroups.append([a['ActivityGroup'] for i, a in enumerate(act)])
            nacever.append([a['NaceVersion'] for i, a in enumerate(act)])
            clas.append([a['Classification'] for i, a in enumerate(act)])

    # flatten lists
    mindex = [item for sublist in mindex for item in sublist]
    mi = pd.MultiIndex.from_tuples(mindex, names=['EntityNumber', 'ActivityN'])
    #print("Makes sense?", nacodes)
    actv_df = pd.DataFrame(index=mi) #,
                           #columns=['NaceCode', 'ActivityGroup', 'NaceVersion',
                           #        'Classification'])
    print("df", actv_df)

    actv_df['NaceCode'] = Series([item for sublist in nacodes for item in sublist], index=mi)
    actv_df['ActivityGroup'] = Series([item for sublist in activitygroups for item in sublist], index=mi)
    actv_df['NaceVersion'] = Series([item for sublist in nacever for item in sublist], index=mi)
    actv_df['Classification'] = Series([item for sublist in clas for item in sublist], index=mi)
    #actv_df.index.names = ['EntityNumber', 'ActivityN']
    actv_df.to_csv('actv_df.csv')
    return actv_df

def run_job_posts():
    try:
        offers = read_csv('belgian_job_posts_2017.csv')  # 'df_100.csv')
    except:
        offers = smalldataframe()
    print("========= Data description =========")
    print(offers.columns)
    onmap(offers)

    print("offers from ", len(set(offers['company'])), "companies")
    print("Offers per province")
    print(offers.groupby('state', as_index=False)['jobtitle'].count())
    print("----------------------")

    analysisjobs(offers)

def run_companies():
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
    #companies.to_csv('companies.csv')
    array_company = np.array(companies['EntityNumber'])
    print("len", len(array_company), len(set(array_company)))
    try:
        # read if it exists
        actv_df = pd.read_csv('actv_df.csv')
        print('Reading existing file')
    except:
        # create
        print("Creating the data frame of activities")
        actv_df = createdfactivity(companies)

    # add sector of activity
    actv_df_red = actv_df[(actv_df['NaceVersion'] == 2008) &
                          (actv_df['Classification'] == 'MAIN')]
    nace_codes_2008 = pd.read_csv('NaceCode2008.csv', header=0,
                                  names=['Section', 'Description', 'minCode',
                                       'maxCode', 'grater', 'smaller'],
                                  index_col=False)
    #print(nace_codes_2008)
    maxc = nace_codes_2008['maxCode'].tolist()
    sections = []
    for c in actv_df_red['NaceCode']:
        try:
            #   nace_codes_2008[nace_codes_2008['minCode'] ==
            #                          [n for n in minc if n >= c][0]]['Section']
            sections.append(nace_codes_2008[nace_codes_2008['maxCode'] ==
                                      [n for n in maxc if n+1 > c][0]]['Section'].tolist()[0])
        except:
            #print("Code", c, "Not found")
            sections.append(None)
            pass
    #print(sections)
    actv_df_red['Section'] = Series(sections, index=actv_df_red.index)

    # group by Section
    groups_section = actv_df_red[['Section', 'EntityNumber']]\
                     .groupby(['Section'], as_index=False).count()\
                     .rename(columns={'EntityNumber': 'NEntityPerSec'})
    print((groups_section))
    plt.figure('N companies per Section')
    ax2 = plt.subplot(111)
    groups_section.plot.bar(x='Section', y='NEntityPerSec', ax=ax2, color='blue')
    ax2.set_ylabel('# entities per Section')
    xlabels = ax2.get_xticklabels()
    new_labels = [l.get_text()[-1] for l in xlabels]
    ax2.set_xticklabels(new_labels, rotation=40)


def main():

    run_job_posts()
    #run_companies()
    plt.show()

if __name__ == "__main__":
    main()