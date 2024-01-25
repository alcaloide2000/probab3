
"""
Created on Thu Jan 25 11:22:41 2024

@author: alcaloide200
"""


from dash import dcc, html, callback, Output, Input, Dash
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import yfinance as yf  # para importar ticker
from datetime import date




start = '1970-01-02'
end = date.today()
litickers = ['^GSPC','^IXIC','^RUT']  # lista de tickers a analizar

liyears = [1,2]

dicctickers ={} # diccionario , a cada ticker le corresponde una serie de cotizaciones al cierre entre las fechas establecidas
for i in litickers:
    dicctickers[i] = yf.download(i, start, end)['Close']

index_options = []
for indice in litickers:
    index_options.append({'label':str(indice),'value':indice})
year_options = []
for year in liyears:
    year_options.append({'label':str(year),'value':year})

#
carinput = dbc.Card(
    [
        dbc.CardBody([
            html.H4("INDEX SELECTOR", className="card-title"),
            html.P("CHOOSE AN INDEX AND A PERIOD OF TIME IN YEARS", className="card-text"),
            dcc.Dropdown(id='index-picker',options=index_options,value=litickers[0]),
            dcc.Dropdown(id='year-picker', options=year_options, value=liyears[0]),
        ]),
    ], color="#d5def5",
)


app = Dash()
server = app.server

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(carinput,width=4),
                dbc.Col(html.Div(id='caroutput0', children=[]), width=8)
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(html.Div(id='caroutput', children=[]), width=12)
            ]
        ),
        html.Br(),
        dbc.Row(
        [
            dbc.Col(html.Div(id='caroutput2', children=[]), width=12),
            dbc.Col(html.Div(id='caroutput3', children=[]), width=12),
            dcc.Store(id="didata_stored", data=[])
        ]
        )
    ]
)

@callback(Output('caroutput', 'children'),
            Output('caroutput2', 'children'),
            Output('didata_stored', 'data'),
            Output('caroutput0', 'children'),
                Input('index-picker', 'value'),
                Input('year-picker', 'value')
          )

def esperanzatickera(ticker,year):
    secoti0 = dicctickers[ticker]
    dfcoti0 = pd.DataFrame(secoti0)
    data = dfcoti0.copy()
    data['crece_n'] = data['Close'].pct_change(periods=int(year)*252)
    data['crece_n2'] = round(data['crece_n'],2)
    data = data[pd.notnull(data["crece_n2"])]
    lastyearcgar = list(data["crece_n2"])[-1]
    listacrecen2 = list(data['crece_n2'])
    listadesp = [listacrecen2[x + 252] for x in range(0, len(listacrecen2) - 252)]
    listaceros = [0] * 252
    listadesp.extend(listaceros)
    data['crecen2desp'] = listadesp
    data = data.iloc[0:len(data) - 252, :]

    migraf10 = px.line(dfcoti0['Close'])

    migraf5 = px.histogram(data['crece_n2'],marginal="box")

    caroutput0 = dbc.Card(
        [
            dbc.CardBody([
                dbc.Row(
                    [dbc.Col(dcc.Graph(figure= migraf10))
                     ]
                )

            ]),
        ], color="#d5def5", inverse= False
    )

    caroutput = dbc.Card(
        [
            dbc.CardBody([
                html.H4("INDEX SELECTED: {} LAST YEAR CGAR {}".format(ticker,lastyearcgar), className="card-title"),
                dbc.Row(
                    [dbc.Col(dcc.Graph(figure= migraf5),width=12)
                     ]
                ),
                html.H4("PROBABILTY DISTRIBUTION FOR {} YEAR INVESTED FOR THE TICKER{}".format(year,ticker), className="card-title"),
            ]),
        ], color="#d5def5", inverse= False
    )

    lidataunique = sorted(data.crece_n2.unique())
    valmin = lidataunique[0]
    valmax = lidataunique[-1]
    # for crecen2 in lidataunique:
    #     licrecen2_options.append({'label': str(crecen2), 'value': crecen2 })
    didata = data.to_dict('records')

    caroutput2 = dbc.Card(
        [
            dbc.CardBody([
                html.H4("SELECT A RANGE FOR NEXT YEAR CAGR", className="card-title"),
                dcc.RangeSlider(id ='slider1',min=valmin, max =valmax, step = 0.04, value=[lastyearcgar-0.02, lastyearcgar+0.02],persistence=True)
            ]),
        ], color="#d5def5",
    )
    return caroutput, caroutput2, didata, caroutput0


@callback(Output('caroutput3', 'children'),
        Input('didata_stored', 'data'),
              Input('slider1', 'value'))

def esperanzadesp(didata,licrecen2):
    data = pd.DataFrame(didata)
    dffiltrada = data.loc[(data['crece_n2'] >= licrecen2[0]) & (data['crece_n2'] <= licrecen2[1])]
    migraf9 = px.histogram(dffiltrada['crecen2desp'],marginal="box")
    caroutput3 = dbc.Card(
        [
            dbc.CardBody([


                dcc.Graph(figure=migraf9),
                html.H4("PROBABILTY DISTRIBUTION FOR THE NEXT YEAR FOR A RANGE {}-{}".format(licrecen2[0],licrecen2[1]),
                        className="card-title"),
            ]),
        ], color="#d5def5",
    )

    return caroutput3

if __name__=='__main__':
    app.run(debug=False)
