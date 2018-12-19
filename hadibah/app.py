from flask import Flask, render_template, request, url_for, redirect, send_from_directory, after_this_request
import os
import json
# from plot import plot_page, detail_plot, plot_page_mpld3
from utils import readSC, colors
from plots import plot_page_mpld3, plot_page_counts, plot_page_los, plot_page_inventory
# from side_plot import plot_page_inventory_mpld3
# from utils import table_convert, author_html, planetAndStar, hz
# Setup Flask
app = Flask(__name__)
app.config['DEBUG'] = 'On'
os.environ['SC_secret'] = '123124kjfdssdffdssz3'
app.config['SECRET_KEY'] = '123124kjfdssdffdssz3'
app.config['DEBUG_MODE'] = 1
# app.config['SECRET_KEY'] = os.environ['SC_secret']

# ['index','animal_id','animal_type','sex','primary_bree','dob','secondary_','kennel_no','impound_no','intake_type','intake_subtype','intake_date','s_n_date','intake_cond','weight','weight_1_week','outcome_type','outcome_subtype','outcome_date','due_out_date','outcome_cond','location_1','location_1_date','location_2','location_2_date','behavior_cond','outcome_behavior_cond','euth_reason','intake_date_form_2']

@app.route('/')
def homepage():
    """Home page for Hadibah with updated table"""
    df, _ = readSC()
    # df['alink'] = list(map(author_html, df['Author'], df['link']))
    dfs = df.sort_values('impound_no', ascending=False)  # [:50]  # TODO: Remove the slicing!
    cols = ['animal_id','animal_type','impound_no','intake_type','intake_subtype','intake_cond','outcome_type','outcome_subtype','outcome_cond','weight','intake_date','outcome_date','dob','primary_bree','secondary_','kennel_no','s_n_date','weight_1_week','due_out_date','location_1','location_1_date','location_2','location_2_date','los','days_old','los_1','los_2','age_s_n_date','weight_difference','in_to_due_out_date_diff','due_out_to_outcome_date_diff']
    decimals = dict.fromkeys(cols, 2)
    dfs = dfs.round(decimals=decimals)
    # dfs['HD'].fillna('...', inplace=True)
    # dfs['Comment'].fillna('...', inplace=True)
    # dfs['source'].fillna('...', inplace=True)
    dfs = dfs.to_dict('records')
    return render_template('main.html', rows=dfs)


@app.route("/publications/")
def publications():
    """Show relevant publications for Hadibah"""
    with open('data/publications.json') as pubs:
        pubs = json.load(pubs)
    return render_template('publications.html', publications=pubs)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def error_404(error):
    """Simple handler for status code: 404"""
    return render_template('404.html')

@app.route('/download/<path:fname>')
def download(fname):
    """Download SWEET-Cat table in different formats and clean afterwards"""
    if fname.startswith('animals'):
        print(fname)
        fmt = fname.split('.')[-1]
        if fmt in ['csv', 'hdf','xls']:
            table_convert(fmt=fmt)

            @after_this_request
            def remove_file(response):
                try:
                    pass
                    # os.remove('data/{}'.format(fname))
                except OSError:  # pragma: no cover
                    pass  # pragma: no cover
                return response
        return send_from_directory('data', fname)
    else:
        return send_from_directory('data', fname)

@app.route('/home/')
def gohome():
    return redirect(url_for('homepage'))

# @app.route('/login',methods=['GET','POST'])
# def login():
#     username = request.args.get('username')
#     password = request.args.get('password')

# :5000/filter?field=alex&value=pw1
@app.route('/filter/',methods=['GET','POST'])
def filter():
    field = request.args.get('field')
    value = request.args.get('value')
    # print(", ".join((field, value)))
    df, _ = readSC()
    filterdf = df[df[str(field)] == value]
    # df['alink'] = list(map(author_html, df['Author'], df['link']))
    filterdfs = filterdf.sort_values('impound_no', ascending=False)  # [:50]  # TODO: Remove the slicing!
    cols = ['animal_id','animal_type','impound_no','intake_type','intake_subtype','intake_cond','outcome_type','outcome_subtype','outcome_cond','weight','intake_date','outcome_date','dob','primary_bree','secondary_','kennel_no','s_n_date','weight_1_week','due_out_date','location_1','location_1_date','location_2','location_2_date']
    decimals = dict.fromkeys(cols, 2)
    filterdfs = filterdfs.round(decimals=decimals)
    # df = df[(df['intake_type']!="DEAD")&(df['intake_subtype']!="DEAD")&(df['intake_cond']!="DEAD")&(df['intake_type']!="DISPOSAL")&(df['intake_subtype']!="DISPOSAL")&(df['intake_cond']!="DISPOSAL")&(df['intake_type']!="DECEASED")&(df['intake_subtype']!="DECEASED")&(df['intake_cond']!="DECEASED")]
    filterdfs = filterdfs.to_dict('records')
    return render_template('main.html', rows=filterdfs)

@app.route("/linked/", methods=['GET', 'POST'])
def linked_plot():
    """Plot inventory over time"""
    df, columns = readSC()
    # print(", ".join(((df, columns))))
    return plot_page_mpld3(df, columns, request)

@app.route('/linked-filter/',methods=['GET','POST'])
def linked_plot_filter():
    field = request.args.get('field')
    value = request.args.get('value')
    # print(", ".join((field, value)))
    df, columns = readSC()
    filterdf = df[df[str(field)] == value]
    # filterdfs = filterdf.sort_values('impound_no', ascending=False)  # [:50]  # TODO: Remove the slicing!
    return plot_page_mpld3(filterdf, columns, request, field=field, value=value)

@app.route("/counts/", methods=['GET', 'POST'])
def counts_plot():
    """Plot inventory over time"""
    # df, columns = planetAndStar()
    df, columns = readSC()
    # print(", ".join(((df, columns))))
    # columns = df.columns.values
    # return plot_page(df, columns, request, page="plot_inventory")
    return plot_page_counts(df, columns, request)

@app.route("/length-of-stay/", methods=['GET', 'POST'])
def length_of_stay_plot():
    """Plot inventory over time"""
    # df, columns = planetAndStar()
    df, columns = readSC()
    # print(", ".join(((df, columns))))
    # columns = df.columns.values
    # return plot_page(df, columns, request, page="plot_inventory")
    return plot_page_los(df, columns, request)

@app.route("/inventory/", methods=['GET', 'POST'])
def inventory_plot():
    """Plot inventory over time"""
    # df, columns = planetAndStar()
    df, columns = readSC()
    # print(", ".join(((df, columns))))
    # columns = df.columns.values
    # return plot_page(df, columns, request, page="plot_inventory")
    return plot_page_inventory(df, columns, request)
    
@app.route('/inventory-filter/',methods=['GET','POST'])
def inventory_plot_filter():
    field = request.args.get('field')
    value = request.args.get('value')
    # print(", ".join((field, value)))
    df, columns = readSC()
    filterdf = df[df[str(field)] == value]
    # filterdfs = filterdf.sort_values('impound_no', ascending=False)  # [:50]  # TODO: Remove the slicing!
    return plot_page_inventory(filterdf, columns, request, field=field, value=value)

# @app.route('/inventory/', methods=['GET', 'POST'])
# def mpld3_plot():
#     df, columns = readSC()
#     print(", ".join((df,columns)))
#
#     return plot_page_inventory_mpld3(df, columns, request)

# @app.route("/los/", methods=['GET', 'POST'])
# def los_plot():
#     """Plot inventory over time"""
#     # df, columns = planetAndStar()
#     df, columns = readSC()
#     # print(", ".join(((df, columns))))
#     # columns = df.columns.values
#     # return plot_page(df, columns, request, page="plot_inventory")
#     return plot_page_mpld3(df, columns, request)


# @app.route('/filter/<string:filtervalue>')
# def filter(filtervalue):
#     """Home page for SWEETer-Cat with updated table"""
#     df, _ = readSC()
#     # filter DataFrame
#     df = df[(df['intake_type']!="DEAD")&(df['intake_subtype']!="DEAD")&(df['intake_cond']!="DEAD")&(df['intake_type']!="DISPOSAL")&(df['intake_subtype']!="DISPOSAL")&(df['intake_cond']!="DISPOSAL")&(df['intake_type']!="DECEASED")&(df['intake_subtype']!="DECEASED")&(df['intake_cond']!="DECEASED")]
#
#     filterdf = df[df['intake_type'] == filtervalue ]
#     # df['alink'] = list(map(author_html, df['Author'], df['link']))
#     dfs = filterdf.sort_values('impound_no', ascending=False)  # [:50]  # TODO: Remove the slicing!
#     cols = ['animal_id','animal_type','impound_no','intake_type','intake_subtype','intake_cond','outcome_type','outcome_subtype','outcome_cond','weight','intake_date','outcome_date','dob','primary_bree','secondary_','kennel_no','s_n_date','weight_1_week','due_out_date','location_1','location_1_date','location_2','location_2_date']
#     decimals = dict.fromkeys(cols, 2)
#     dfs = dfs.round(decimals=decimals)
#     # dfs['HD'].fillna('...', inplace=True)
#     # dfs['Comment'].fillna('...', inplace=True)
#     # dfs['source'].fillna('...', inplace=True)
#     dfs = dfs.to_dict('records')
#     return render_template('filtered.html', rows=dfs)




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # pragma: no cover
    app.run(host='0.0.0.0', port=port, debug=False)  # pragma: no cover
