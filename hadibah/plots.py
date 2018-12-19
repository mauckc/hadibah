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

import matplotlib.cm as cm
import matplotlib.pyplot as plt
from mpld3 import fig_to_html, plugins
import time


colorschemes = {'Viridis': [Viridis11, 'Viridis256'],
                'Inferno': [Inferno11, 'Inferno256'],
                'Plasma':  [Plasma11,  'Plasma256']}

def barchart_counts( dataf , n ):
    cnts = dataf[headers[n]].value_counts()[0:8]
    keys = [ cnts.keys()[i] for i in xrange(0,len(cnts.keys())) ]
    y_pos = np.arange(len(keys))
    vals = cnts.values
    plt.bar(y_pos, vals, align='center', alpha=0.5)
    plt.xticks(y_pos, keys)
    plt.ylabel('Counts')
    plt.title(headers[n] + ' breakdown')

    plt.show()
    return


def getdailyinventory( day, dataf ):
    dayinventory = dataf[(dataf.intake_date <= day) & (dataf.outcome_date > day)]
    return dayinventory

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


# Name: [distance (AU), diameter (km)]
# From http://www.enchantedlearning.com/subjects/astronomy/planets/
# ss_planets = {
#     'Mercury': [0.39, 4878],
#     'Venus': [0.723, 12104],
#     'Earth': [1, 12756],
#     'Mars': [1.524, 6787],
#     'Jupiter': [5.203, 142796],
#     'Saturn': [9.539, 120660],
#     'Uranus': [19.18, 51118],
#     'Neptune': [30.06, 48600],
#     'Pluto': [39.53, 2274]}

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
        x1, x2, y1, y2, z = 'weight', 'los', 'los', 'age_s_n_date', 'days_old'

    if field and value is None:
        field = 'all fields'
        value = 'all values'
    
    # Does not work with NaN values! so we must remove rows with NaN values
    df = df.loc[:, {x1, x2, y1, y2, z}].dropna(axis=0)
    
    fig, ax = plt.subplots(2, 2, figsize=(14, 8), sharex='col', sharey='row')
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

def plot_page_counts(df, columns, request):
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
        x1, x2, y1, y2, z = 'weight', 'los', 'los', 'age_s_n_date', 'days_old'
    # Does not work with NaN values!
    df = df.loc[:, {x1, x2, y1, y2, z}].dropna(axis=0)
    # print(df.head())
    fig, ax = plt.subplots(2, 2, figsize=(14, 8), sharex='col', sharey='row')
    points = ax[0, 0].scatter(df[x1], df[y1], c=df[z], alpha=0.6)
    points = ax[1, 0].scatter(df[x1], df[y2], c=df[z], alpha=0.6)
    points = ax[0, 1].scatter(df[x2], df[y1], c=df[z], alpha=0.6)
    points = ax[1, 1].scatter(df[x2], df[y2], c=df[z], alpha=0.6)
    # ax[1, 0].set_title('Filtered by {} of {}'.format(field, value))
    # ax[1, 1].set_title('Filtered by {} of {}'.format(field, value))
    # ax[0, 0].set_title('Filtered by {} of {}'.format(field, value))
    # ax[0, 1].set_title('Filtered by {} of {}'.format(field, value))

    ax[1, 0].set_xlabel(x1)
    ax[1, 1].set_xlabel(x2)
    ax[0, 0].set_ylabel(y1)
    ax[1, 0].set_ylabel(y2)


    plugins.connect(fig, plugins.LinkedBrush(points))
    plot = fig_to_html(fig)
    return render_template('plot_counts.html', plot=plot, columns=columns,
                           x1=x1, x2=x2, y1=y1, y2=y2, z=z)

def plot_page_los(df, columns, request):
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
        x1, x2, y1, y2, z = 'weight', 'los', 'los', 'age_s_n_date', 'days_old'
    # Does not work with NaN values!
    df = df.loc[:, {x1, x2, y1, y2, z}].dropna(axis=0)
    # print(df.head())
    fig, ax = plt.subplots(2, 2, figsize=(14, 8), sharex='col', sharey='row')
    points = ax[0, 0].scatter(df[x1], df[y1], c=df[z], alpha=0.6)
    points = ax[1, 0].scatter(df[x1], df[y2], c=df[z], alpha=0.6)
    points = ax[0, 1].scatter(df[x2], df[y1], c=df[z], alpha=0.6)
    points = ax[1, 1].scatter(df[x2], df[y2], c=df[z], alpha=0.6)
    ax[1, 0].set_xlabel(x1)
    ax[1, 0].set_ylabel(y2)
    ax[1, 1].set_xlabel(x2)
    ax[1, 1].set_ylabel(y2)
    ax[0, 0].set_ylabel(y1)
    ax[0, 0].set_xlabel(x1)
    ax[1, 0].set_ylabel(y2)
    ax[1, 0].set_xlabel(x1)
    ax[1, 1].set_ylabel(y2)
    ax[1, 1].set_xlabel(x2)
    ax[0, 0].grid(color='black', linestyle='-', linewidth=2)
    ax[0, 1].grid(color='black', linestyle='-', linewidth=2)
    ax[1, 0].grid(color='black', linestyle='-', linewidth=2)
    ax[1, 1].grid(color='black', linestyle='-', linewidth=2)
    plugins.connect(fig, plugins.LinkedBrush(points))
    plot = fig_to_html(fig)
    return render_template('plot_los.html', plot=plot, columns=columns,
                           x1=x1, x2=x2, y1=y1, y2=y2, z=z)

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
    print('[Dimensions]: lost & found ' + str(np.shape(df[(df.intake_type == "LOST&FOUND")])))
    print('[Dimensions]: dead and disposal intake ' + str(np.shape(df[(df.intake_type == "DEAD") | (df.intake_type == "DISPOSAL") | (df.intake_subtype == "DEAD") | (df.intake_subtype == "DISPOSAL")])) )
    # Filter out LOST&FOUND group and DEAD intake types
    df = df[(df.intake_type != "LOST&FOUND") & (df.intake_type != "DEAD") & (df.intake_subtype != "DEAD") & (df.intake_type != "DISPOSAL") & (df.intake_subtype != "DISPOSAL") & (df.intake_type != "DISPO REQ")]
    print('[Dimensions]: total after lost&found and dead removed ' + str(np.shape(df)) )

    df = df[(df.animal_type == "CAT") | (df.animal_type == "DOG") | (df.animal_type == "KITTEN" ) | (df.animal_type == "PUPPY")]
    print('[Dimensions]: CATs DOGs KITTENs or PUPPPYs selected ' + str(np.shape(df)) )

    df = df[(df.outcome_date != "")]
    print('[Dimensions]: total after still in shelter on data end-date removed ' + str(np.shape(df)) )

    print("[INFO] Filtered out Dead Intakes and Lost and Found Animals.")
    catdf = df[(df.animal_type == "CAT")]
    kittendf = df[(df.animal_type == "KITTEN")]
    dogdf = df[(df.animal_type == "DOG")]
    puppydf = df[(df.animal_type == "PUPPY")]
    felinedf = df[(df.animal_type == "CAT") | (df.animal_type == "KITTEN")]
    caninedf = df[(df.animal_type == "DOG") | (df.animal_type == "PUPPY")]

    dogmaxdate = dogdf['intake_date'].max()
    dogmindate = dogdf['intake_date'].min()
    daterange = pd.date_range(start=dogmindate, end=dogmaxdate)
    print("[INFO] Filtered by animal_type.")
    lasttime = nowtime
    nowtime = time.time()
    deltatime = nowtime - lasttime
    print("[TIMING] data loaded in {} seconds.".format(deltatime))

    inv = [len(getdailyinventory(str(day), df)) for day in daterange ]
    invcat = [len(getdailyinventory(str(day), catdf)) for day in daterange ]
    invkitten = [len(getdailyinventory(str(day), kittendf)) for day in daterange ]
    invdog = [len(getdailyinventory(str(day), dogdf)) for day in daterange ]
    invpuppy = [len(getdailyinventory(str(day), puppydf)) for day in daterange ]
    # invfeline = [len(getdailyinventory(str(day), felinedf)) for day in daterange ]
    # invcanine = [len(getdailyinventory(str(day), caninedf)) for day in daterange ]
    #print dfinvcat['inventory'].values
    tsinv = pd.Series(inv, index = daterange)
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
    fig, ax = plt.subplots(2, 2, figsize=(14, 8), sharex='col', sharey='row')
    points = ax[0, 0].plot_date(tsinvcat.index, tsinvcat.values)
    points = ax[1, 0].plot_date(tsinvdog.index, tsinvdog.values)
    points = ax[0, 1].plot_date(tsinvkitten.index, tsinvkitten.values)
    points = ax[1, 1].plot_date(tsinvpuppy.index, tsinvpuppy.values)

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
