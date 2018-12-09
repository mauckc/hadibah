
from flask import Flask, render_template, request, url_for, redirect, send_from_directory, after_this_request
import os
import json
from plot import plot_page, plot_page_mpld3, detail_plot
from utils import animalAndIntakes, hz, table_convert, author_html, readAnimalData, readAnimalDatawithColumns#, readSC
# from utils import readSC, readExoplanetEU, table_convert

# Setup Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SC_secret']


@app.route('/')
def homepage():
    """Home page for SWEETer-Cat with updated table"""
    df, _ = readAnimalDatawithColumns()
    # df['alink'] = list(map(author_html, df['Author'], df['link']))
    # dfs = df.sort_values('updated', ascending=False)  # [:50]  # TODO: Remove the slicing!
    # dfs.drop(['Author', 'link'], axis=1, inplace=True)
    cols = ['animal_id','animal_type','sex','breed','DOB','years_old','months_old','intake_total','intake_type','intake_subtype','intake_date','intake_time','intake_condition','intake_jurisdiction','crossing','outcome_type','outcome_subtype','outcome_date','outcome_time','outcome_condition']
    decimals = dict.fromkeys(cols, 2)
    dfs = df
    # dfs = dfs.round(decimals=decimals)
    # dfs['HD'].fillna('...', inplace=True)
    # dfs['Comment'].fillna('...', inplace=True)
    # dfs['source'].fillna('...', inplace=True)
    dfs = dfs.to_dict('records')
    return render_template('main.html', rows=dfs)


@app.route('/animal/<string:animal>/')
def animaldetail(star=None):
    """Page with details on the individual system"""
    if animal:
        df, _ = animalAndIntakes(how='left')
        # get range
        t1, t2 = min(df['intake_date']), max(df['intake_date'])
        index = df['impound_id'] == star
        d = df.loc[index, :].copy()
        if len(d):
            show_animal = bool(~d['impound_id'].isnull().values[0])
            if show_animal:
                s = d['impound_id'].values
                s = [si.decode() if isinstance(si, bytes) else si for si in s]
                s = ['{} {}'.format(si[:-2], si[-1].lower()) for si in s]
                # d['exolink'] = ['http://exoplanet.eu/catalog/{}/'.format(si.lower().replace(' ', '_')) for si in s]
            d['los'] = d['los']# Convert to string of days between intake date and outcome date  (d.teff/5777)**4 * (d.mass/((10**d.logg)/(10**4.44)))**2
            d['days_old'] = d['days_old'] # convert to string of days between date of birth and intake date
            # ADD OTHER METRICS LIKE INTAKE_ MONTHYEAR AND INTAKE MONTHWEEK
            # d['hz2'] = round(hz(d['teff'].values[0], d['lum'].values[0], model=4), 5)

            if len(d) == sum(d['animal_id'].isnull()):
                plot = None
            else:
                plot = detail_plot(d, t1, t2)
            d.fillna('...', inplace=True)
            info = d.to_dict('records')

            return render_template('detail.html', info=info, show_animal=show_animal, plot=plot)
    return redirect(url_for('homepage'))


@app.route('/linked/', methods=['GET', 'POST'])
def mpld3_plot():
    df, columns = animalAndIntakes()
    return plot_page_mpld3(df, columns, request)


@app.route("/plot/", methods=['GET', 'POST'])
def plot():
    """Plot stellar parameters"""
    df, columns = readSC()
    return plot_page(df, columns, request, page="plot")


@app.route("/plot-exo/", methods=['GET', 'POST'])
def plot_exo():
    """Plot stellar and planetary parameters"""
    df, columns = animalAndIntakes()
    return plot_page(df, columns, request, page="plot_exo")


@app.route("/publications/")
def publications():
    """Show relevant publications for SWEET-Cat"""
    with open('data/publications.json') as pubs:
        pubs = json.load(pubs)
    return render_template('publications.html', publications=pubs)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/local/')
def local():
    return render_template('local.html')


@app.errorhandler(404)
def error_404(error):
    """Simple handler for status code: 404"""
    return render_template('404.html')


@app.route('/download/<path:fname>')
def download(fname):
    """Download SWEET-Cat table in different formats and clean afterwards"""
    if fname.startswith('sweet-cat'):
        print(fname)
        fmt = fname.split('.')[-1]
        if fmt in ['csv', 'hdf']:
            table_convert(fmt=fmt)

            @after_this_request
            def remove_file(response):
                try:
                    os.remove('data/{}'.format(fname))
                except OSError:  # pragma: no cover
                    pass  # pragma: no cover
                return response
        return send_from_directory('data', fname)
    else:
        return send_from_directory('data', fname)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # pragma: no cover
    app.run(host='0.0.0.0', port=port, debug=False)  # pragma: no cover
