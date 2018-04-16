'''read the job posts'''

#general
import os
import itertools
import numpy as np

# drawing
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors
import seaborn

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
        print(c[2])
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
    ax1 = plt.subplot(111)
    #offers.groupby('month', as_index=False)['jobtitle'].count()

    offers.groupby('month')['jobtitle'].count().plot(ax=ax1)
    ax1.set_ylabel('# jobs per month')

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
    flatui = ["cadetblue", "magenta", "magenta","magenta", "magenta",
    "darkgoldenrod", "darkgoldenrod", "darkgoldenrod", "darkgoldenrod",
    "darkgoldenrod", "darkgoldenrod"]
    mkl = ['+', '.', '^', 'p', 'X', '*', '8', 's', 'P', '*', '-' ]
    seaborn.set_palette(flatui)
    offers.pivot_table('jobtitle', index='month', columns='state', aggfunc='count').plot()
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
            print(iv)
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
    year = []
    for comp in df_companies['EntityNumber']:
        for act in df_companies[df_companies['EntityNumber'] == comp]['activities']:
            mindex.append(list(zip([comp] * len(act),
                          list(range(0, len(act))))))
            # attention! year repeated for each activity, do not use for counting
            year.append([df_companies[df_companies['EntityNumber'] == comp]['StartYear'].values[0]
            for i in range(0, len(act))])
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
    actv_df['StartYear'] = Series([item for sublist in year for item in sublist], index=mi)
    actv_df['NaceCode'] = Series([item for sublist in nacodes for item in sublist], index=mi)
    actv_df['ActivityGroup'] = Series([item for sublist in activitygroups for item in sublist], index=mi)
    actv_df['NaceVersion'] = Series([item for sublist in nacever for item in sublist], index=mi)
    actv_df['Classification'] = Series([item for sublist in clas for item in sublist], index=mi)
    #actv_df.index.names = ['EntityNumber', 'ActivityN']
    actv_df.to_csv('actv_df.csv')
    print("df", actv_df.head())
    return actv_df

def createcompanygeo(companies):
    print("Create company geo")
    # 'canonical_denomination'
    comp_name, commune, entries, lang = [], [], [], []
    for comp in companies['canonical_denomination']:
        try:
            comp_name.append([comp])
        except:
            comp_name.append([""])
    for comp in companies['address']:
        try:
            commune.append([comp['MunicipalityNL']])
        except:
            commune.append([""])
    for proc in companies['processed']:
        try:
            entries.append([proc['geoloc']['longitude'],
                           proc['geoloc']['latitude'],
                           proc['geoloc']['zip_code']])
        except:
            entries.append(["", "", ""])
    dic_lang = {'0': 'all', '1': 'FR', '2': 'NL', '3': 'DE', '4':'EN'}
    for denom in companies['denominations']:
        lang.append(list(set([dic_lang[d['Language']] for d in denom])))
    #geo_lang_df
    idx = range(0, len(comp_name))
    print(len(comp_name), len(commune), len(entries), len(lang))
    geo_lan_df = pd.DataFrame(index=idx)
    geo_lan_df['company'] = Series([item for sublist in comp_name for item in sublist], index=idx)
    print("Company ok")
    geo_lan_df['longitude'] = Series([item[0] for item in entries], index=idx)
    print("Longitude okay")
    geo_lan_df['latitude'] = Series([item[1]  for item in entries], index=idx)
    print("Latitude okay")
    geo_lan_df['zip_code'] = Series([item[2]  for item in entries], index=idx)
    print("zip okay")
    geo_lan_df['MunicipalityNL'] = Series([item for sublist in commune for item in sublist], index=idx)
    print("commune okay")
    geo_lan_df['Languages'] = Series([item for item in lang], index=idx)
    print(geo_lan_df.head())
    geo_lan_df.to_csv('company_geo.csv')
    return geo_lan_df

def run_job_posts():

    plt.figure("Inhabitants")
    ax0 = plt.subplot(111)
    plt.plot(np.arange(0, len(INH.keys())), INH.values())

    print("Analysis of job offers")
    try:
        offers = read_csv('belgian_job_posts_2017.csv')  # 'df_100.csv')
    except:
        offers = smalldataframe()
    print("========= Data description =========")
    print(offers.columns)
    #onmap(offers)

    print(len(offers), "offers from ", len(set(offers['company'])), "companies")

    # density of jobs per region
    # city is not always present
    print("Ncities", len(set(offers['city'])))
    group_city = offers[['city', 'latitude','longitude', 'jobkey']]\
                 .groupby(['latitude','longitude'], as_index=False)\
                 .count()\
                 .rename(columns={'jobkey': 'NOffersPerCity'})
    group_city.to_csv('offer_per_city.csv')
    print("Groups of cities", len(group_city))
    group_prov = offers[['state','jobtitle']]\
                 .groupby('state', as_index=False).count()\
                 .rename(columns={'jobtitle': 'NOffersPerProvince'})
    group_prov.to_csv('offer_per_prov.csv')
    state_geo = 'belgium.geo.json'

    mapbe = folium.Map(location=[50, 4], zoom_start=8)
    #folium.Marker(group_city['city']).add_to(mapbe)
    print(group_city[['latitude', 'longitude','NOffersPerCity']])
    to_plot = group_city.pivot(index='longitude', columns='latitude', values='NOffersPerCity')
    seaborn.heatmap(to_plot)
    #seaborn.jointplot(x='longitude', y='latitude', data=group_prov, kind='kde')
    mapbe.choropleth(geo_data=state_geo, data=group_city,
                 columns=['city', 'NOffersPerCity'],
                 fill_color='YlGn',
                 key_on='feature.city',
                 fill_opacity=0.7, line_opacity=0.2,
                 legend_name='Number of job offers')
    #folium.LayerControl().add_to(mapbe)
    mapbe.save('noffers_provinceBE.html')
    print("Offers per province")
    job_state = offers.pivot_table('jobkey', index='state', aggfunc='count')
    print(job_state)
    #print(offers.groupby('state', as_index=False)['jobtitle'].count())
    print("----------------------")
    plt.figure("Job offers per province")
    ax1 = plt.subplot(111)
    job_state.plot.bar(legend=False, ax=ax1)
    ax1.set_xlabel("")
    ax1.set_ylabel("# jobs per province")

    analysisjobs(offers)


def run_companies():

    print("Analysis of companies")
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
    companies['StartDate'] = pd.to_datetime(companies['StartDate'])
    companies['StartYear'] = companies['StartDate'].map(lambda x: x.year)

    try:
        # read if it exists
        actv_df = pd.read_csv('actv_df.csv')
        print('Reading existing file actv_df.csv')
    except:
        # create
        print("Creating the data frame of activities")
        actv_df = createdfactivity(companies)
    print("table activities", actv_df.columns, actv_df.head())

    try:
        actv_df_red = pd.read_csv('actv_df_2008_MAIN_sections.csv')
        print('Reading existing file actv_df_2008_MAIN.csv')
    except:
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
        actv_df_red.to_csv('actv_df_2008_MAIN_sections.csv')
    print("table with Sections", actv_df_red.columns, actv_df_red.head())
    # group by Section
    sections_count = actv_df_red.pivot_table('NaceCode', index='Section', aggfunc='count')
    #print(sections_count)
    plt.figure('N companies per Section')
    ax2 = plt.subplot(111)
    sections_count.plot.bar(legend=False,ax=ax2, title="Nace Code Version 2008 - MAIN activity")
    ax2.set_ylabel('# entities per Section')
    xlabels = ax2.get_xticklabels()
    new_labels = [l.get_text()[-1] for l in xlabels]
    ax2.set_xticklabels(new_labels, rotation=40)
    reg_y_bins = pd.cut(actv_df_red['StartYear'],
                        [1950, 1965, 1970, 1980, 1990, 2000])
    sections_count_Y = actv_df_red.pivot_table('NaceCode', index='Section',
                                   columns=reg_y_bins, aggfunc='count')
    plt.figure('N companies per Section per Period')
    ax3 = plt.subplot(111)
    sections_count_Y.plot.bar(title="Nace Code Version 2008 - MAIN activity", ax=ax3)
    ax3.set_ylabel('# entities per Section per Period')
    xlabels = ax3.get_xticklabels()
    new_labels = [l.get_text()[-1] for l in xlabels]
    ax3.set_xticklabels(new_labels, rotation=40)

    # companies registered per year
    plt.figure("HistoricalData")
    ax1 = plt.subplot(111)
    companies.pivot_table('EntityNumber', index='StartYear', aggfunc='count')\
             .plot(legend=False, ax=ax1)
    ax1.set_ylabel("# registered companies per year")

    try:
        geo_lan_df = read_csv('company_geo.csv')
        print("Reading existing file company_geo.csv")
    except:
        geo_lan_df = createcompanygeo(companies)

    # geographical location
    #onmap(geo_lan_df)
    comp_lang = geo_lan_df.pivot_table('company', index='Languages', aggfunc='count')
    print(comp_lang)
    comp_lang.plot.bar()

def main():

    seaborn.set()
    seaborn.set_palette(seaborn.color_palette("bright", 11))
    run_job_posts()
    #run_companies()
    plt.show()

if __name__ == "__main__":
    main()