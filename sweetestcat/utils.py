import numpy as np
import pandas as pd
from astropy import constants as c
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

colors = {
    'Blue': '#1f77b4',
    'Orange': '#ff7f0e',
    'Green': '#2ca02c',
    'Red': '#d62728',
    'Purple': '#9467bd',
}

# df = pd.read_csv('./data/010116 through 100118.csv')
def readAnimalData():
    """Read the exoplanet.eu database from the 'data' folder and store as
    pandas DataFrame
    ['A1433734', 'DOG', 'N', 'MALTESE', '01/01/2015', '1', '0.00', '1.1', 'STRAY', 'SANTA ANA', '01/01/2016', '11:36 am', 'NORMAL', 'SANTA ANA.1', 'FLOWER/CHESTNUT', 'ADOPTION', 'DOG 5', '01/08/2016', ' 2:53 pm', 'Unnamed: 19']
    """
    df = cache.get('animalDB')
    if df is None:
        input_headers = ['animal_id','animal_type','sex','breed','DOB','years_old','months_old','intake_total','intake_type','intake_subtype','intake_date','intake_time','intake_condition','intake_jurisdiction','crossing','outcome_type','outcome_subtype','outcome_date','outcome_time','outcome_condition']
        df = pd.read_csv('./data/010116 through 100118.csv', header=None, names=input_headers, engine='c')
        idx = np.zeros(len(df), dtype=bool)
        # for pl in 'abcdefgh':
        #     idx = idx | df['plName'].str.endswith(' {}'.format(pl))
        # df.loc[idx, 'stName'] = df.loc[idx, 'plName'].str[:-2]
        # df.loc[~idx, 'stName'] = df.loc[~idx, 'plName']
        # df['plDensity'] = plDensity(df['plMass'], df['plRadius'])  # Add planet density
        cache.set('animalDB', df, timeout=5*60)
    return df

def readAnimalDatawithColumns():
    """Read the exoplanet.eu database from the 'data' folder and store as
    pandas DataFrame
    ['A1433734', 'DOG', 'N', 'MALTESE', '01/01/2015', '1', '0.00', '1.1', 'STRAY', 'SANTA ANA', '01/01/2016', '11:36 am', 'NORMAL', 'SANTA ANA.1', 'FLOWER/CHESTNUT', 'ADOPTION', 'DOG 5', '01/08/2016', ' 2:53 pm', 'Unnamed: 19']
    """
    input_headers = ['animal_id','animal_type','sex','breed','DOB','years_old','months_old','intake_total','intake_type','intake_subtype','intake_date','intake_time','intake_condition','intake_jurisdiction','crossing','outcome_type','outcome_subtype','outcome_date','outcome_time','outcome_condition']
    df = pd.read_csv('./data/010116 through 100118.csv', header=None, names=input_headers, engine='c')
    df = cache.get('animalDB')
    if df is None:
        input_headers = ['animal_id','animal_type','sex','breed','DOB','years_old','months_old','intake_total','intake_type','intake_subtype','intake_date','intake_time','intake_condition','intake_jurisdiction','crossing','outcome_type','outcome_subtype','outcome_date','outcome_time','outcome_condition']
        df = pd.read_csv('./data/010116 through 100118.csv', header=None, names=input_headers, engine='c')
        idx = np.zeros(len(df), dtype=bool)
        # for pl in 'abcdefgh':
        #     idx = idx | df['plName'].str.endswith(' {}'.format(pl))
        # df.loc[idx, 'stName'] = df.loc[idx, 'plName'].str[:-2]
        # df.loc[~idx, 'stName'] = df.loc[~idx, 'plName']
        # df['plDensity'] = plDensity(df['plMass'], df['plRadius'])  # Add planet density
        cache.set('animalDB', df, timeout=5*60)
    return df, input_headers

# def readSC(nrows=None):
#     """Read the SWEET-Cat database and cache it (if it isn't already).
#     Output
#     ------
#     df : pd.DataFrame
#       The DataFrame of SWEET-Cat
#     plots : list
#       The columns that can be used for plotting
#     """
#     df = cache.get('animalDB')
#     plots = cache.get('animalCols')
#     if (df is None) or (plots is None):
#         df = pd.read_table('data/010116 through 100118.csv', engine='c')
#         # df = pd.read_table('data/sweet-cat.tsv', engine='c')
#         # df.drop('tmp', axis=1, inplace=True)
#         # df['flag'] = df['flag'] == 1  # Turn to bool
#         # df['Vabs'] = absolute_magnitude(df['par'], df['Vmag'])
#         # df['lum'] = list(map(luminosity, df['teff'], df['Vmag'], df['par']*1E-3, df['mass']))
#         # df['Star'] = df['Star'].str.strip()
#
#         # Generate missing link https://github.com/DanielAndreasen/SWEETer-Cat/issues/135
#         # for star in df.Star[df['link'].isnull()].values:
#         #     df.loc[df['Star'] == star, ['link']] = generate_missing_link(star)
#
#         plots = ['intake_type', 'intake_subtype', 'intake_condition', 'par', 'parerr', 'teff', 'tefferr',
#                  'logg', 'loggerr', 'logglc', 'logglcerr', 'vt', 'vterr',
#                  'feh', 'feherr', 'mass', 'masserr', 'lum']
#         cache.set('animalDB', df, timeout=5*60)
#         cache.set('animalCols', plots, timeout=5*60)
#
#     if nrows is not None:
#         return df.loc[:nrows-1, :], plots

def animalAndIntakes(how='inner'):
    """Read the SWEET-Cat and ExoplanetEU databases and merge them.

    Input
    -----
    how : str (default: 'inner')
      How to merge the two DataFrames. See pd.merge for documentation

    Output
    ------
    d : pd.DataFrame
      The DataFrame of merged DataFrame
    c : list
      The columns that can be used for plotting
    """
    df, columns = readAnimalDatawithColumns()
    # deu = readExoplanetEU()
    cols = ['animal_id','animal_type','sex','breed','DOB','years_old','months_old','intake_total','intake_type','intake_subtype','intake_date','intake_time','intake_condition','intake_jurisdiction','crossing','outcome_type','outcome_subtype','outcome_date','outcome_time','outcome_condition']
    # d = pd.merge(df, deu, left_on='animal_id', right_on='impound_id', how=how)
    # d['radius'] = list(map(stellar_radius, d['mass'], d['logg']))
    # d['teq0'] = d.teff * np.sqrt((d.radius*700000)/(2*d.sma*150000000))
    c = columns #+ cols[1:]
    d = df
    return d, c


# def plDensity(mass, radius):
#     """Calculate planet density.
#
#     Assumes Jupiter mass and radius given."""
#     mjup_cgs = 1.8986e30     # Jupiter mass in g
#     rjup_cgs = 6.9911e9      # Jupiter radius in cm
#     return 3 * mjup_cgs * mass / (4 * np.pi * (rjup_cgs * radius)**3)  # g/cm^3


def table_convert(fmt="csv"):
    """Convert the SC data into different formats.

    To make available for download.
    """
    # others netcdf, fits?
    # https://pandas.pydata.org/pandas-docs/stable/io.html
    if fmt not in ['tsv', 'csv', 'hdf']:
        raise NotImplementedError("Conversion format to {} not available.".format(fmt))
    name = "data/sweet-cat.{}".format(fmt)
    if fmt is "tsv":  # This is the standard
        pass
    else:
        df = pd.read_table('data/sweet-cat.tsv')
        if fmt == "hdf":
            df.to_hdf(name, key="sweetcat", mode="w", format='table')
        elif fmt == "csv":
            df.to_csv(name, sep=",", index=False)

def get_default(value, default, dtype, na_value='...'):
    if isinstance(value, dtype) and (value != na_value):
        return value
    else:
        return default


def hz(teff, lum, model=1):
    """Calculate inner and outer HZ limits using different models.

    Lum is in solar units.
    Reference: Kopparapu+ 2013
    http://adsabs.harvard.edu/abs/2013ApJ...765..131K
    """
    for parameter in (teff, lum):
        if not isinstance(parameter, (int, float)):
            return np.nan
    if not (2500 < teff < 7200):
        return np.nan

    if model == 1:  # Recent Venus
        p = [1.7753, 1.4316E-4, 2.9875E-9, -7.5702E-12, -1.1635E-15]
    elif model == 2:  # Runaway greenhouse
        p = [1.0512, 1.3242E-4, 1.5418E-9, -7.9895E-12, -1.8328E-15]
    elif model == 3:  # Moist greenhouse
        p = [1.0140, 8.1774E-5, 1.7063E-9, -4.3241E-12, -6.6462E-16]
    elif model == 4:  # Maximum greenhouse
        p = [0.3438, 5.8942E-5, 1.6558E-9, -3.0045E-12, -5.2983E-16]
    elif model == 5:  # Early Mars
        p = [0.3179, 5.4513E-5, 1.5313E-9, -2.7786E-12, -4.8997E-16]

    seff_sun = p[0]
    ts = teff-5780
    a, b, c, d = p[1], p[2], p[3], p[4]
    seff = seff_sun + a*ts + b*ts**2 + c*ts**3 + d*ts**4
    dist = np.sqrt(lum/seff)
    return dist

def author_html(author, link):
    """
    Create HTML anchor tag for author with correct link to ADSABS

    Inputs
    ------
    author : str
      Name of the author(s)
    link : str
      Link to article

    Output
    ------
    alink : str
      Author anchor tag to link
    """
    if (',' in author) and (',' in link):
        authors = author.split(',')
        links = link.split(',')
        alinks = []
        for author, link in zip(authors, links):
            alinks.append('<a target="_blank" href="{}">{}</a>'.format(link.strip(), author.strip()))
        alink = ', '.join(alinks)
    else:
        alink = '<a target="_blank" href="{}">{}</a>'.format(link, author)
    return alink
