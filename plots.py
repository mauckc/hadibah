import matplotlib
matplotlib.use('Agg')

from bokeh.embed import components
from bokeh.layouts import column, row
from bokeh.models import ColorBar, HoverTool, LinearColorMapper, Spacer
from bokeh.palettes import Viridis11, Inferno11, Plasma11
from bokeh.plotting import ColumnDataSource, figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import flash, redirect, render_template, session, url_for
import numpy as np
import pandas as pd
# from utils import colors, get_default, planetary_radius

from utils import get_default
import matplotlib.cm as cm
import matplotlib.pyplot as plt; plt.rcdefaults()
from mpld3 import fig_to_html, plugins
import time

ss_intake = {
    'Mercury': [0.39, 4878],
    'Venus': [0.723, 12104],
    'Earth': [1, 12756],
    'Mars': [1.524, 6787],
    'Jupiter': [5.203, 142796],
    'Saturn': [9.539, 120660],
    'Uranus': [19.18, 51118],
    'Neptune': [30.06, 48600],
    'Pluto': [39.53, 2274]}

colorschemes = {'Viridis': [Viridis11, 'Viridis256'],
                'Inferno': [Inferno11, 'Inferno256'],
                'Plasma':  [Plasma11,  'Plasma256']}

def barchart_counts( dataf, headers, n, numvals=16):
    cnts = dataf[headers[n]].value_counts()[0:numvals]
    keys = [ cnts.keys()[i] for i in range(0,len(cnts.keys())) ]
    y_pos = np.arange(len(keys))
    vals = cnts.values
    fig = plt.figure(figsize=(10,6))
    plt.bar(y_pos, vals, align='center', alpha=0.5, color=['red','blue','green','purple','orange','cyan','magenta'])
    plt.xticks(y_pos, keys)
    plt.ylabel('Animal Count')
    plt.title(headers[n].replace('_',' ').title() + ' Breakdown')
    plt.grid()
    # plot = fig_to_html(fig)
    return fig

def getdailyinventory( day, dataf ):
    dayinventory = dataf[(dataf.datetime < day) & (dataf.outcome_datetime > day)]
    return len(dayinventory)

# def dailyinventory( startdate, enddate, dataf ):
#     date_format = "%Y-%m-%d"
#     diff = datetime.strptime(enddate, date_format) - datetime.strptime(startdate, date_format)
#     numdays = diff.days
#     oneday = datetime.strptime("2015-01-02", date_format) - datetime.strptime("2015-01-01", date_format)
#     days = [ (oneday * x + datetime.strptime(startdate, date_format) ) for x in range(numdays) ]
#     print days
#     #days = [ datetime.strptime(startdate, date_format) + oneday * day for day in numdays ]# list of days between start and enddates in ISODate format
#     #print days
#     #dayinventory = dataf[(dataf.intake_date <= day) & (dataf.outcome_date > day)]
#     print oneday, numdays
#     return #dayinventory

def detail_plot(df, tlow, thigh):

    hz1 = get_default(df['datetime'].values[0], -2, float)
    hz2 = get_default(df['outcome_datetime'].values[0], -1, float)
    color = get_default(df['los'].values[0], 5777, float)
    tlow = get_default(max(2500, tlow), 2500, int)
    thigh = get_default(min(8500, thigh), 8500, int)

    R = df.iloc[0]['los']
    r = [ ri for  ri in df.loc[:, ['los']].values]
    LOSs = df['los'].values
    max_LOSs = max([losi for losi in LOSs if isinstance(losi, (int, float)) and not np.isnan(losi)])
    Rs = max(500, 500*R)
    rs = [max(80, 30*ri) for ri in r]

    fig, ax = plt.subplots(1, figsize=(14, 2))
    ax.scatter([0], [1], s=Rs, c=[color], vmin=tlow, vmax=thigh, cmap=cm.autumn)
    no_los = []

    if 0 < hz1 < hz2:
        x = np.linspace(hz1, hz2, 10)
        y = np.linspace(0.9, 1.1, 10)
        z = np.array([[xi]*10 for xi in x[::-1]]).T
        plt.contourf(x, y, z, 300, alpha=0.8, cmap=cm.summer)

    for i, los in enumerate(LOSs):
        if np.isnan(los):
            no_los.append('{} has no LOS'.format(df['plName'].values[i]))
            continue
        if los < hz1:
            dist = hz1-los
            ax.scatter(los, [1], s=rs[i], c=[dist], vmin=0, vmax=hz1, cmap=cm.autumn)
        elif hz1 <= los <= hz2:
            ax.scatter(los, [1], s=rs[i], c='k', alpha=0.8)
        else:
            dist = los-hz2
            ax.scatter(los, [1], s=rs[i], c=[dist], vmin=hz2, vmax=max_LOSs, cmap=cm.winter_r)

    for intake in ss_intake.keys():
        s = ss_intake[intake][0]
        r = 30*ss_intake[intake][1]/2.
        r /= float(ss_intake['Jupiter'][1])
        ax.scatter(s, [0.95], s=r*10, c='g')
        ax.text(s-0.01, 0.97, intake, color='white')

    ax.set_xlim(0.0, max_LOSs*1.2)
    ax.set_ylim(0.9, 1.1)
    ax.set_xlabel('Date')
    ax.yaxis.set_major_formatter(plt.NullFormatter())
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    # ax.set_facecolor('black')
    plt.tight_layout()

    for i, text in enumerate(no_los):
        ax.text(max_LOSs*0.8, 1.05-i*0.02, text, color='white')

    return fig_to_html(fig)



def plot_page_mpld3(df, columns, request, field=None, value=None):
    if request.method == 'POST':  # Something is being submitted
        x1 = str(request.form['x1'])
        x2 = str(request.form['x2'])
        y1 = str(request.form['y1'])
        y2 = str(request.form['y2'])
        z = str(request.form['z'])
        for requested_col in {x1, x2, y1, y2, z}:
            if requested_col not in columns:
                return redirect(url_for('sd'))
    else:
        x1, x2, y1, y2, z = 'days_old', 'los', 'los', 'los', 'days_old'

    if field and value is None:
        field = 'all fields'
        value = 'all values'

    # Does not work with NaN values! so we must remove rows with NaN values
    df = df.loc[:, {x1, x2, y1, y2, z}].dropna(axis=0)

    fig, ax = plt.subplots(2, 2, figsize=(12, 8), sharex='col', sharey='row')
    points = ax[0, 0].scatter(df[x1], df[y1], c=df[z], alpha=0.6)
    points = ax[1, 0].scatter(df[x1], df[y2], c=df[z], alpha=0.6)
    points = ax[0, 1].scatter(df[x2], df[y1], c=df[z], alpha=0.6)
    points = ax[1, 1].scatter(df[x2], df[y2], c=df[z], alpha=0.6)
    ax[0, 0].set_ylabel(y1)
    ax[0, 0].set_xlabel(x1)
    ax[1, 0].set_ylabel(y2)
    ax[1, 0].set_xlabel(x1)
    ax[1, 1].set_ylabel(y2)
    ax[1, 1].set_xlabel(x2)
    # ax[1, 0].set_title('Filtered by {} of {}'.format(field, value))
    # ax[1, 1].set_title('Filtered by {} of {}'.format(field, value))
    # ax[0, 0].set_title('Filtered by {} of {}'.format(field, value))
    size = df.shape[0]
    ax[0, 1].set_title('all plots filtered by {} with {} of size: {}'.format(field, value, str(size)))
    ax[0, 1].set_ylabel(y1)
    ax[0, 1].set_xlabel(x2)

    for axe in ax.flatten():
        for tk in axe.get_yticklabels():
            tk.set_visible(True)
        for tk in axe.get_xticklabels():
            tk.set_visible(True)

    ax[0, 0].grid(color='grey', linestyle='-', linewidth=2)
    ax[0, 1].grid(color='grey', linestyle='-', linewidth=2)
    ax[1, 0].grid(color='grey', linestyle='-', linewidth=2)
    ax[1, 1].grid(color='grey', linestyle='-', linewidth=2)
    plugins.connect(fig, plugins.LinkedBrush(points))
    plot = fig_to_html(fig)
    return render_template('plot_mpld3.html', plot=plot, columns=columns,
                           x1=x1, x2=x2, y1=y1, y2=y2, z=z)

def plot_page_counts(df, columns, request, field=None, value=None, rows=None):
    if request.method == 'POST':  # Something is being submitted
        z = str(request.form['z'])
        for requested_col in {z}:
            if requested_col not in columns:
                return redirect(url_for('counts_plot'))
    else:
        z = 'species'
    # Does not work with NaN values!
    df = df.loc[:, {z}].dropna(axis=0)
    # print(df.head())
    field_index = 2
    for i, col in enumerate(columns):
        if col == z:
            field_index = i
        else:
            pass

    fig = barchart_counts(df, columns, field_index)

    plot = fig_to_html(fig)
    return render_template('plot_counts.html', plot=plot, columns=columns, rows=rows,
                           z=z)

def plot_page_los(df, columns, request, field=None, value=None, rows=None):
    if request.method == 'POST':  # Something is being submitted
        z = str(request.form['z'])
        for requested_col in {z}:
            if requested_col not in columns:
                return redirect(url_for('los_plot'))
    else:
        z = 'los'
    # Does not work with NaN values!
    df = df.loc[:, {z}].dropna(axis=0)


    fig = plt.figure(figsize=(12,6))
    # An "interface" to matplotlib.axes.Axes.hist() method
    n, bins, patches = plt.hist(x=df[z], bins='auto', color='#0504aa',
                                alpha=0.7, rwidth=0.85)

    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Length of Stay')
    plt.ylabel('Frequency Count')
    plt.title('Length of Stay')
    # plt.text(43, 90, r'$\mu=15, b=3$')
    plt.xlim((0,60))
    maxfreq = n.max()
    # Set a clean upper y-axis limit.
    plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)

    field_index = 29
    print(columns)
    for i, col in enumerate(columns):
        if col == z:
            field_index = i
        else:
            pass

    # fig = barchart_counts(df, columns, field_index)
    plot = fig_to_html(fig)
    return render_template('plot_los.html', plot=plot, columns=columns,
                           z=z, rows=rows)


def plot_page_inventory(df, columns, request, field=None, value=None):
    if request.method == 'POST':  # Something is being submitted
        x = str(request.form['x'])
        y = str(request.form['y'])
        for requested_col in {x, y}:
            if requested_col not in columns:
                return redirect(url_for('sd'))
    else:
        x, y = 'date', 'inventory'

    if field and value is None:
        field = 'all fields'
        value = 'all values'

    nowtime = time.time()
    # current headers are:
    headers = list(df.columns.values)
    print('[Dimensions]: total ' + str(np.shape(df)) )
    # print('[Dimensions]: lost & found ' + str(np.shape(df[(df.intake_type == "LOST&FOUND")])))
    # print('[Dimensions]: dead and disposal intake ' + str(np.shape(df[(df.intake_type == "DEAD") | (df.intake_type == "Disposal") | (df.intake_subtype == "DEAD") | (df.intake_subtype == "DISPOSAL")])) )
    # Filter out LOST&FOUND group and DEAD intake types
    df = df[(df.intake_type != "Disposal") & (df.outcome_type != "Disposal")]
    print('[Dimensions]: total after lost&found and dead removed ' + str(np.shape(df)) )

    df = df[(df.animal_type == "Cat") | (df.animal_type == "Dog") | (df.animal_type == "Kitten" ) | (df.animal_type == "Puppy")]
    print('[Dimensions]: CATs DOGs KITTENs or PUPPPYs selected ' + str(np.shape(df)) )

    df['outcome_datetime'] = df['outcome_datetime'].fillna('2019-08-15 11:01:00')
    # df = df[(df.outcome_datetime != "") | (df.outcome_datetime.isnull())]
    print('[Dimensions]: total after still in shelter on data end-date removed ' + str(np.shape(df)) )

    print("[INFO] Filtered out Dead Intakes and Lost and Found Animals.")
    catdf = df[(df.animal_type == "Cat")]
    kittendf = df[(df.animal_type == "Kitten")]
    dogdf = df[(df.animal_type == "Dog")]
    puppydf = df[(df.animal_type == "Puppy")]
    felinedf = df[(df.animal_type == "Cat") | (df.animal_type == "Kitten")]
    caninedf = df[(df.animal_type == "Dog") | (df.animal_type == "Puppy")]

    dogmaxdate = dogdf['datetime'].max()
    dogmindate = dogdf['outcome_datetime'].min()
    daterange = pd.date_range(start=dogmindate, end=dogmaxdate)
    print("[INFO] Filtered by animal_type.")
    lasttime = nowtime
    nowtime = time.time()
    deltatime = nowtime - lasttime
    print("[TIMING] data loaded in {} seconds.".format(deltatime))

    # inv = [len(getdailyinventory(str(day), df)) for day in daterange ]
    invcat = [getdailyinventory(str(day), catdf) for day in daterange ]
    invkitten = [getdailyinventory(str(day), kittendf) for day in daterange ]
    invdog = [getdailyinventory(str(day), dogdf) for day in daterange ]
    invpuppy = [getdailyinventory(str(day), puppydf) for day in daterange ]
    # invfeline = [len(getdailyinventory(str(day), felinedf)) for day in daterange ]
    # invcanine = [len(getdailyinventory(str(day), caninedf)) for day in daterange ]
    #print dfinvcat['inventory'].values
    # tsinv = pd.Series(inv, index = daterange)
    tsinvcat = pd.Series(invcat, index = daterange)
    tsinvkitten = pd.Series(invkitten, index = daterange)
    tsinvdog = pd.Series(invdog, index = daterange)
    tsinvpuppy = pd.Series(invpuppy, index = daterange)
    # tsinvfeline = pd.Series(invfeline, index = daterange)
    # tsinvcanine = pd.Series(invcanine, index = daterange)
    # print dimensions of our pandas dataframe
    # print( np.shape(df) )
    # print('\nCat Inventory: ' + str(np.shape(tsinvcat)) )
    # print( '\nKitten Invenory: ' + str(np.shape(tsinvkitten)) )

    # print( '\nDog Inventory: ' + str(np.shape(tsinvdog)) )
    # print( '\nPuppy Inventory: ' + str(np.shape(tsinvpuppy)) )

    # print( '\nFeline Inventory: ' + str(np.shape(tsinvfeline))+ "\n" )
    # print( '\nCanine Inventory: ' + str(np.shape(tsinvcanine))+ "\n" )

    # # Does not work with NaN values!
    # tsinvcat = tsinvcat.loc[:, {x, y}].dropna(axis=0)
    # tsinvcdog = tsinvdog.loc[:, {x, y}].dropna(axis=0)
    # tsinvkitten = tsinvkitten.loc[:, {x, y}].dropna(axis=0)
    # tsinvpuppy = tsinvpuppy.loc[:, {x, y}].dropna(axis=0)
    # print(tsinvcat.index)
    # print(tsinvcat.columns)

    # print(df.head())
    fig, ax = plt.subplots(2, 2, figsize=(10, 6), sharex='col', sharey='row')
    points = ax[0, 0].plot_date(tsinvcat.index, tsinvcat.values,'bo-')
    points = ax[1, 0].plot_date(tsinvdog.index, tsinvdog.values,'ro-')
    points = ax[0, 1].plot_date(tsinvkitten.index, tsinvkitten.values,'go-')
    points = ax[1, 1].plot_date(tsinvpuppy.index, tsinvpuppy.values,'yo-')

    ax[1, 0].set_xlabel(x)
    ax[1, 0].set_ylabel('dog ' + y)
    ax[1, 0].set_title('Daily Inventory for {} of {}'.format(field, value))
    ax[1, 0].grid(color='black', linestyle='-', linewidth=2)


    ax[1, 1].set_xlabel(x)
    ax[1, 1].set_ylabel('puppy ' + y)
    ax[1, 1].set_title('Daily Inventory for {} of {}'.format(field, value))
    ax[1, 1].grid(color='black', linestyle='-', linewidth=2)

    ax[0, 0].set_ylabel('cat ' + y)
    ax[0, 0].set_xlabel(x)
    ax[0, 0].set_title('Daily Inventory for {} of {}'.format(field, value))
    ax[0, 0].grid(color='black', linestyle='-', linewidth=2)

    ax[0, 1].set_ylabel('kitten ' + y)
    ax[0, 1].set_xlabel(x)
    ax[0, 1].set_title('Daily Inventory for {} of {}'.format(field, value))
    ax[0, 1].grid(color='black', linestyle='-', linewidth=2)



    fig.autofmt_xdate()

    plugins.connect(fig, plugins.LinkedBrush(points))
    plot = fig_to_html(fig)
    return render_template('plot_inventory.html', plot=plot, columns=columns,
                           x=x, y=y)
