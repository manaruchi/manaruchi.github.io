#!/usr/bin/env python
# coding: utf-8

# # CURE India USAID Dehradun Water Balance Portal
#
# Powered by RBased Services Pvt. Ltd.

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import json
import dash_daq as daq
import plotly.express as px
import os

# ## Setup the Dash Application and Theme
#
# Available themes:  CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, LUMEN, LUX, MATERIA, MINTY, PULSE, SANDSTONE, SIMPLEX, SKETCHY, SLATE, SOLAR, SPACELAB, SUPERHERO, UNITED, YETI


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.COSMO],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}])
app.title = 'Water Balance Plan Dehradun'

cur_folder = os.getcwd()

# ## Setup Paths to External Files and Initial JSON Setup

with open(os.path.join(cur_folder, 'main.geojson')) as f:
    json_file = json.load(f)
for x in range(len(json_file['features'])):
    json_file['features'][x]['id'] = int(json_file['features'][x]['key'])
    del json_file['features'][x]['key']
df = pd.read_csv(os.path.join(cur_folder, 'values.csv'))

df['GRID_ID'] = df['OID_'].values

df = df.round(3)

ground_water_df = pd.read_csv(os.path.join(cur_folder, 'Maps', 'ground_water_level', 'values.csv')).round(3)
other_details_df = pd.read_csv(os.path.join(cur_folder, 'Maps', 'zones.csv')).round(3)
other_details_df = other_details_df[other_details_df['Litho']>0]
lulc_df = other_details_df[other_details_df['LULC_Code']!=0]


with open(os.path.join(cur_folder, 'jalsansthan_zones_for_dash.geojson')) as f:
    zones_json = json.load(f)
zones_df = pd.read_csv(os.path.join(cur_folder, 'Maps', 'zones_jalsansthan', 'Jalsansthan_Zone.csv'))

stream_json = dict()

with open(os.path.join(cur_folder, 'streams', '1990.geojson')) as f:
    stream_json['1990'] = json.load(f)
with open(os.path.join(cur_folder, 'streams', '1994.geojson')) as f:
    stream_json['1994'] = json.load(f)
with open(os.path.join(cur_folder, 'streams', '1999.geojson')) as f:
    stream_json['1999'] = json.load(f)
with open(os.path.join(cur_folder, 'streams', '2004.geojson')) as f:
    stream_json['2004'] = json.load(f)
with open(os.path.join(cur_folder, 'streams', '2009.geojson')) as f:
    stream_json['2009'] = json.load(f)
with open(os.path.join(cur_folder, 'streams', '2014.geojson')) as f:
    stream_json['2014'] = json.load(f)
with open(os.path.join(cur_folder, 'streams', '2019.geojson')) as f:
    stream_json['2019'] = json.load(f)

pumps_df = pd.read_csv(os.path.join(cur_folder, 'Jal Location.csv'))
oht_df = pd.read_csv(os.path.join(cur_folder, 'oht.csv'))
well_df = pd.read_csv(os.path.join(cur_folder, 'well.csv'))


# ## Initiate the Mapbox Object in order to plot the JSON file

trace = [go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id, marker_opacity=1, marker_line_width = 2, showlegend=False, showscale=False, name = 'Divisions'),
         go.Choroplethmapbox(geojson=json_file, locations=df.GRID_ID, z=df.ET_mean_2010,
                                    colorscale="Blues", marker_opacity=0.7, marker_line_width = 0, hovertext = 'ET Mean 2010',showlegend=False, showscale=False)]
fig = go.Figure(data=trace)
fig.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=10.5, mapbox_center = {"lat": 30.335 , "lon": 78.0737})
fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


# ## Layout of the Page
#
# ### First Column - Layers List and Some Layer Controls such as Zone Toggle, Opacity Slider and Basemap Selector

first_column = dbc.Card(
    [
        dbc.CardHeader("Layers", style = {'color': 'white'}),
        dbc.CardBody(
            [

                dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        "Zones", id="button-item0", action=True, n_clicks = 1
                    ),
                    dbc.ListGroupItem(
                        "Physical Features", id="button-item", action=True, n_clicks = 0
                    ),
                    dbc.ListGroupItem(
                        "Evapotranspiration", id="button-item2", action=True, n_clicks = 0
                    ),
                    dbc.ListGroupItem(
                        "Surface Water", id="button-item3", action=True,n_clicks = 0
                    ),

                    dbc.ListGroupItem(
                        "Urbanisation", id="button-item5", action=True,n_clicks = 0
                    ),
                    dbc.ListGroupItem(
                        "Land Cover", id="button-item7", action=True, n_clicks = 0
                    ),
                    dbc.ListGroupItem(
                        "Ground Water Potential", id="button-item6", action=True,n_clicks = 0
                    ),

                    dbc.ListGroupItem(
                        "Ground Water Level", id="button-item8", action=True, n_clicks = 0
                    ),

                ], id = 'layers-list'),

                dbc.Button("Multi Layer Mode", id = 'button-item_back_front', color="success", href = '/dash-multilayer', style = {'width': '90%', 'margin': '5%'}),
                dbc.Tooltip("Dashboard in Multilayer Mode", target="button-item_back_front", placement='bottom'),

                dbc.Tooltip("Water lost in the atmosphere by evaporation and transpiration", target="button-item2", placement='bottom'),
                dbc.Tooltip("Elevation, Aspect, Curvature, Slope and Hillshade", target="button-item", placement='bottom'),
                dbc.Tooltip("Total amount of permanent storage that exists in the aquifers.", target="button-item6", placement='bottom'),
                dbc.Tooltip("Rivers and Streams.", target="button-item3", placement='bottom'),
                dbc.Tooltip("Zones of Dehradun City.", target="button-item0", placement='bottom'),
                dbc.Tooltip("Change in Urban Land Cover in Dehradun", target="button-item5", placement='bottom'),
                dbc.Tooltip("Land Use Land Cover Information", target="button-item7", placement='bottom'),
                dbc.Tooltip("Depth below the earth's surface that is saturated with water.", target="button-item8", placement='bottom'),
                html.Table([
                    html.Tr([
                        html.Td('Zones', style = {'margin-top': '5px','margin-bottom': '5px'}),
                        html.Td(daq.ToggleSwitch(id='zoneswitch',value = True), style = {'margin-top': '5px','margin-bottom': '5px'})
                    ]),

                    html.Tr([
                        html.Td('Opacity', style = {'margin-top': '5px','margin-bottom': '5px'}),
                        html.Td(dbc.Select(id="opslider", options=[ {"label": "Invisible", "value": 0}, {"label": "10%", "value": 0.1}, {"label": "20%", "value": 0.2}, {"label": "30%", "value": 0.3}, {"label": "40%", "value": 0.4}, {"label": "50%", "value": 0.5}, {"label": "60%", "value": 0.6}, {"label": "70%", "value": 0.7}, {"label": "80%", "value": 0.8}, {"label": "90%", "value": 0.9}, {"label": "100%", "value": 1}, ], value = 0.8, style = {'font-size': 'small'} ), style = {'margin-top': '5px','margin-bottom': '5px'})
                    ]),

                    html.Tr([
                        html.Td('Basemap', style = {'margin-top': '5px','margin-bottom': '5px'}),
                        html.Td(dbc.Select(id="basemap", options=[ {"label": "No Basemap", "value": "white-bg"}, {"label": "Open Street Map", "value": "open-street-map"}, {"label": "Carto Positron", "value": "carto-positron"}, {"label": "Carto Darkmatter", "value": "carto-darkmatter"} ,{"label": "Stamen Terain", "value": "stamen-terrain"}, {"label": "Stamen Toner", "value": "stamen-toner"}, {"label": "Stamen Watercolor", "value": "stamen-watercolor"}, ], value = 'stamen-terrain', style = {'font-size': 'small'}), style = {'margin-top': '5px','margin-bottom': '5px'})
                    ]),
                ], style = {'margin-left': '15px', 'margin-top': '15px', 'color':'#ffffff', 'font-size': 'small', 'height': '100px' ,'width': '90%', 'padding': '5px'}),

                dbc.Tooltip("Show/Hide the Zones Layer", target='zoneswitch', placement='bottom'),
                dbc.Tooltip("Adjust Opacity of the Layer", target='opslider', placement='bottom'),
                dbc.Tooltip("Select Basemap for the Map", target='basemap', placement='bottom'),

            ],
        style = {'padding': '0px',"border-radius": "0px"}),
        dbc.CardFooter("Powered by RBased Services Pvt. Ltd.", style = {'font-size': 'small', 'color': 'white'}),
    ],
    style={"height": "700px",
          "border-radius": "0px"},
    color="secondary"
)


# ### Second Column - Mapbox Map
#
# This column contains the main Map.


overlay_contents = html.Div([


])

card_header = dbc.Row(
    [
        dbc.Col(html.Div("Map", id = 'map-caption')),
        dbc.Col(dbc.Select(id='year-select',
                           style = {'padding': '2px','height': '25px', 'width': '150px', 'float':'right', 'font-size': 'small'}), id = 'select-col-space')

    ],
    no_gutters=True,
    style = {'width':'100%'}
)




second_column = dbc.Card(
    [
        dbc.CardHeader(card_header, style = {'color': 'white'}),
        dbc.CardBody(
            [

                html.Div([dcc.Loading(id = 'maparea', type = 'dot'),
                    html.Div(overlay_contents,id = 'overlay', style = {'top': '85%', 'left': '17%', 'z-index': 2,'position': 'absolute', 'padding': 10, 'border-radius': 0, 'border': '2px solid #ffffff', 'width': 200, 'background-color': '#ffffff', 'opacity': 0.8, 'align-content': 'center'})], style = {'padding': '0px'})

            ],
        style = {'padding': '0px',"border-radius": "0px", 'background-color': 'white'}),

    ],
    style={"height": "700px",
          "border-radius": "0px","position":"relative"},
    color="info"
)



# ### Third Column - Statistics and Dynamic Information on Click
#


third_column = dbc.Card(
    [
        dbc.CardHeader("Statistics", style = {'color': 'white'}),
        dbc.CardBody(
            [
                html.Div(id='selection', style = {'overflow': 'auto'}),
                html.Div('Loading Data...',id='stats', style = {'height': '100%'})


            ],
        style = {'padding': '5px',"border-radius": "0px", 'background-color': 'white', 'overflow': 'auto'}),

    ],
    style={"height": "700px",
          "border-radius": "0px",
          },
    color="secondary"
)


# ### Other Page Elements - Including Top Navigation Bar


rbs_logo = 'http://www.rbasedservices.com/wp-content/uploads/2020/06/cropped-RBS_LOGO.png'
cure_logo = 'https://cureindia.org/assets/images/icon-90x90.png'
impact_dash_logo = 'https://impactdash.com/assets/img/logo/impactdash_logo.svg'
usaid_logo = 'https://www.usaid.gov/sites/all/themes/usaid/logo.png'
ministry_logo = 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/105px-Emblem_of_India.svg.png'
amrut_logo = 'http://amrut.gov.in/images/amrut-logo.png'
deh_logo = 'https://nagarnigamdehradun.com/images/logo1.png'
everyulb_logo = 'https://media.licdn.com/dms/image/C510BAQEYqRwFUxE44g/company-logo_200_200/0?e=2159024400&v=beta&t=t2smPxGGio5z8Egn1CmuGcaLFzFyJWj7Es8a7inikI8'


navbar = dbc.Navbar(
    [
        dbc.Col(html.Div("Water Balance Plan Dehradun", style = {'color': 'black', 'font-size': 'x-large'})),

        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(id = 'usaidlogo', src=usaid_logo, height="40px", alt = 'U.S. Agency for International Development')),

                ],
                align="center",
                no_gutters=True,
            ),
            href="https://www.usaid.gov/",
            style = {'padding-left': '10px', 'padding-right': '10px'}
        ),

        dbc.Tooltip("U.S. Agency for International Development",
            target="usaidlogo",
        ),

        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(id = 'ministrylogo', src=ministry_logo, height="40px", alt = 'Ministry of Housing and Urban Affairs')),

                ],
                align="center",
                no_gutters=True,
            ),
            href="https://www.mohua.gov.in/",
            style = {'padding-left': '10px', 'padding-right': '10px'}
        ),

        dbc.Tooltip("Ministry of Housing and Urban Affairs",
            target="ministrylogo",
        ),

        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(id = 'amrutlogo', src=amrut_logo, height="40px", alt = 'AMRUT')),

                ],
                align="center",
                no_gutters=True,
            ),
            href="http://amrut.gov.in/content/",
            style = {'padding-left': '10px', 'padding-right': '10px'}
        ),

        dbc.Tooltip("Atal Mission for Rejuvenation and Urban Transformation",
            target="amrutlogo",
        ),

        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(id = 'dehlogo', src=deh_logo, height="40px", alt = 'Nagar Nigam Dehradun')),

                ],
                align="center",
                no_gutters=True,
            ),
            href="https://nagarnigamdehradun.com/",
            style = {'padding-left': '10px', 'padding-right': '10px'}
        ),

        dbc.Tooltip("Nagar Nigam Dehradun",
            target="dehlogo",
        ),






        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(id = 'curelogo', src=cure_logo, height="40px", alt = 'Centre for Urban and Regional Excellence')),

                ],
                align="center",
                no_gutters=True,
            ),
            href="https://cureindia.org/",
            style = {'padding-left': '10px', 'padding-right': '10px'}
        ),


        dbc.Tooltip("Centre for Urban and Regional Excellence",
            target="curelogo",
        ),

        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(id = 'impactdashlogo',src=impact_dash_logo, height="20px", alt = 'ImpactDash')),

                ],
                align="center",
                no_gutters=True,
            ),
            href="https://impactdash.com/",
            style = {'padding-left': '10px', 'padding-right': '10px'}
        ),

        dbc.Tooltip("ImpactDash",
            target="impactdashlogo",
        ),



        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(id = 'rbslogo', src=rbs_logo, height="40px", alt = 'RBased Services Pvt. Ltd.')),

                ],
                align="center",
                no_gutters=True,
            ),
            href="http://www.rbasedservices.com/",
            style = {'padding-left': '10px', 'padding-right': '10px'}
        ),

        dbc.Tooltip("RBased Services Pvt. Ltd.",
            target="rbslogo",
        ),

    ],
    color="light",

    style = {'height': '65px'},

)




row = dbc.Row(
    [
        dbc.Col(html.Div(first_column, id = 'first-col', style = {'height': '700px', 'overflow': 'auto'}), className = 'col-12 col-lg-2'),
        dbc.Col(html.Div(second_column, style = {'height': '700px'}), className = 'col-12 col-lg-7'),
        dbc.Col(html.Div(third_column, style = {'height': '700px'}), className = 'col-12 col-lg-3'),
    ],
    no_gutters=True,
    style = {'height': '600px'}
)


# ## Callbacks

# ### Callback for Layer List Interactivity


ncc = [1,0,0,0,0,0,0,0]

@app.callback(Output("layers-list", 'children'),
             [Input('button-item0', 'n_clicks'),Input('button-item', 'n_clicks'),Input('button-item2', 'n_clicks'),Input('button-item3', 'n_clicks'),Input('button-item5', 'n_clicks'),Input('button-item6', 'n_clicks'),Input('button-item7', 'n_clicks'),Input('button-item8', 'n_clicks')])
def select_layer(a1,a2,a3,a4,a6,a7,a8,a9):

    nc = [a1,a2,a3,a4,a6,a7,a8,a9]

    global ncc

    ncc = nc

    print('The ncc is ', nc)

    return [dbc.ListGroupItem( "Zones", id="button-item0", action=True, n_clicks = 0, active = bool(nc[0])),
            dbc.ListGroupItem( "Physical Features", id="button-item", action=True, n_clicks = 0, active = bool(nc[1])),
            dbc.ListGroupItem( "Evapotranspiration", id="button-item2", action=True, n_clicks = 0, active = bool(nc[2])),
            dbc.ListGroupItem( "Surface Water", id="button-item3", action=True, n_clicks = 0, active = bool(nc[3])),

            dbc.ListGroupItem( "Urbanisation", id="button-item5", action=True, n_clicks = 0, active = bool(nc[4])),
            dbc.ListGroupItem( "Ground Water Potential", id="button-item6", action=True, n_clicks = 0, active = bool(nc[5])),
            dbc.ListGroupItem( "Land Cover", id="button-item7", action=True, n_clicks = 0, active = bool(nc[6])),
            dbc.ListGroupItem( "Ground Water Level", id="button-item8", action=True, n_clicks = 0 , active = bool(nc[7]))]


@app.callback(Output("map-caption", 'children'),
             [Input('button-item0', 'n_clicks'),Input('button-item', 'n_clicks'),Input('button-item2', 'n_clicks'),Input('button-item3', 'n_clicks'),Input('button-item5', 'n_clicks'),Input('button-item6', 'n_clicks'),Input('button-item7', 'n_clicks'),Input('button-item8', 'n_clicks')])
def select_layer(a0,a1,a2,a3,a5,a6,a7,a8):

    global ncc

    if(ncc[0] == 1):
        return "Zones"
    elif(ncc[1] == 1):
        return "Physical Features Map"

    elif(ncc[2] == 1):
        return "Evapotranspiration Map"

    elif(ncc[3] == 1):
        return "Surface Water Map"



    elif(ncc[4] == 1):
        return "Urbanisation Map"

    elif(ncc[5] == 1):
        return "Ground Water Potential Map"

    elif(ncc[6] == 1):
        return "Land Use Land Cover Map"

    elif(ncc[7] == 1):
        return "Ground Water Level Map"

    print('The ncc is ', ncc)


# ### Callback for setting the values of the year selector combo box


@app.callback(Output('year-select', 'options'),
             [Input('button-item8', 'active'), Input('button-item2', 'active'), Input('button-item', 'active'), Input('button-item7', 'active'), Input('button-item5', 'active'), Input('button-item3', 'active'), Input('button-item0', 'active')])
def select_ground_water16(n1,n2,n3,n4,n5,n6,n7):
    if(n1):
        return [{"label": "January, 2011", "value": "jan11"},
                {"label": "May, 2011", "value": "may11"},
                {"label": "August, 2011", "value": "aug11"},
                {"label": "November, 2011", "value": "nov11"},
                {"label": "January, 2015", "value": "jan15"},
                {"label": "May, 2015", "value": "may15"},
                {"label": "August, 2015", "value": "aug15"},
                {"label": "November, 2015", "value": "nov15"},
                {"label": "January, 2019", "value": "jan19"},
                {"label": "May, 2019", "value": "may19"},
                {"label": "August, 2019", "value": "aug19"},
                {"label": "November, 2019", "value": "nov19"},]

    if(n2):
        return [{"label": "2001", "value": "2001"},
                {"label": "2005", "value": "2005"},
                {"label": "2010", "value": "2010"},
                {"label": "2015", "value": "2015"},
                {"label": "2020", "value": "2020"},

                ]

    if(n7):
        return [{"label": "Overview", "value": "overview"},
                {"label": "Pump Locations", "value": "pump"},
                {"label": "Overhead Tanks", "value": "oht"},
                {"label": "Tube Wells", "value": "well"},
                ]

    if(n3):
        return [{"label": "Elevation", "value": "elevation"},
                {"label": "Aspect", "value": "aspect"},
                {"label": "Curvature", "value": "curvature"},
                {"label": "Slope", "value": "slope"},
                {"label": "Hillshade", "value": "hillshade"}

                ]
    if(n4):
        return [{"label": "LULC", "value": "LULC_Code"},
                {"label": "Lithology", "value": "Litho"},
                ]
    if(n5):           #Urbanisation
        return [{"label": "1995", "value": "1995"},
                {"label": "2000", "value": "2000"},
                {"label": "2005", "value": "2005"},
                {"label": "2010", "value": "2010"},
                {"label": "2015", "value": "2015"},
                ]
    if(n6):           #Surface Water
        return [{"label": "1990", "value": "1990"},
                {"label": "1994", "value": "1994"},
                {"label": "1999", "value": "1999"},
                {"label": "2004", "value": "2004"},
                {"label": "2009", "value": "2009"},
                {"label": "2014", "value": "2014"},
                {"label": "2019", "value": "2019"},
                ]

@app.callback(Output('year-select', 'value'),
             [Input('button-item8', 'active'), Input('button-item2', 'active'), Input('button-item', 'active'), Input('button-item7', 'active'), Input('button-item5', 'active'), Input('button-item3', 'active'), Input('button-item0', 'active')])
def select_ground_water17(n1,n2,n3,n4,n5,n6,n7):
    if(n1):
        return "jan11"
    if(n2):
        return '2001'
    if(n3):
        return 'elevation'
    if(n4):
        return 'LULC_Code'
    if(n5):    #Urbanisation
        return '1995'
    if(n6):
        return '2019'
    if(n7):
        return 'overview'

# ### Callback to control what is to be shown on the main map



@app.callback(Output('maparea', 'children'),
             [Input('year-select', 'value'), Input('zoneswitch', 'value'), Input('opslider', 'value'), Input('basemap', 'value')])
def select_ground_water18(selected_val, zoneshow, op, bmap):

    op = float(op)

    global ncc



    if(ncc == [0,0,0,0,0,0,0,1]):

        if(zoneshow):

            trace2 = [go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id, hovertext=zones_df.Name ,marker_opacity=1, marker_line_width = 2, showlegend=False, showscale=False, name = 'Divisions'), go.Choroplethmapbox(geojson=json_file, locations=ground_water_df.OID_, z=ground_water_df['GWL_{}'.format(selected_val)], hovertext=ground_water_df['GWL_{}'.format(selected_val)],
                                            colorscale="RdBu_r", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = 'Ground Water Level (m): %{hovertext}', name = selected_val.upper())]
        else:

            trace2 = [go.Choroplethmapbox(geojson=json_file, locations=ground_water_df.OID_, z=ground_water_df['GWL_{}'.format(selected_val)], hovertext=ground_water_df['GWL_{}'.format(selected_val)],
                                            colorscale="RdBu_r", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = 'Ground Water Level (m): %{hovertext}', name = selected_val.upper())]


        fig = go.Figure(data=trace2)
        fig.update_layout(mapbox_style=bmap,
                          mapbox_zoom=10.35, mapbox_center = {"lat": 30.33 , "lon": 78.068})
        fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


        graphobjmap = dcc.Graph(id = 'map-plot', figure = fig)

        return graphobjmap

    elif(ncc == [0,0,0,0,1,0,0,0]):

        if(zoneshow):

            trace2 = [go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id, hovertext=zones_df.Name ,marker_opacity=1, marker_line_width = 2, showlegend=False, showscale=False, name = 'Divisions'), go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df['urban_{}'.format(selected_val)], hovertext=lulc_df['urban_name_{}'.format(selected_val)],
                                            colorscale="RdBu_r", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = 'Ground Water Level (m): %{hovertext}', name = selected_val.upper())]
        else:

            trace2 = [go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df['urban_{}'.format(selected_val)], hovertext=lulc_df['urban_name_{}'.format(selected_val)],
                                            colorscale="RdBu_r", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = 'Ground Water Level (m): %{hovertext}', name = selected_val.upper())]


        fig = go.Figure(data=trace2)
        fig.update_layout(mapbox_style=bmap,
                          mapbox_zoom=10.97, mapbox_center = {"lat": 30.323 , "lon": 78.04})
        fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


        graphobjmap = dcc.Graph(id = 'map-plot', figure = fig)

        return graphobjmap

    elif(ncc == [1,0,0,0,0,0,0,0]):

        if(selected_val == 'overview'):

            if(zoneshow):

                trace2 = [go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id, hovertext=zones_df.Name, hovertemplate = '%{hovertext}' ,marker_opacity=op, marker_line_width = 2, showlegend=False, showscale=False, name = '')]
            else:

                trace2 = [go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id, hovertext=zones_df.Name ,hovertemplate = '%{hovertext}' ,marker_opacity=0, marker_line_width = 2, showlegend=False, showscale=False, name = '')]

            fig = go.Figure(data=trace2)

        elif(selected_val == 'pump'):



            fig = px.scatter_mapbox(pumps_df, lat="Lat", lon="Long", hover_name = pumps_df['Area'].values, hover_data = {'Year of Construction': pumps_df['Construction year'],
                                                                                                              'Power of Motor': pumps_df['Motar Power'],
                                                                                                              'Pump Head': pumps_df['Head'],
                                                                                                              'Pump Discharge': pumps_df['Discharge'],
                                                                                                              'MLD': pumps_df['Per day (MLD)'],
                                                                                                              },
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=30, zoom=10,
                        color = 'Zone')

        elif(selected_val == 'oht'):



            fig = px.scatter_mapbox(oht_df, lat="Lat", lon="Long", hover_name = oht_df['OHT'].values, hover_data = {'Year of Construction': oht_df['Year'],

                                                                                                              'Inlet Line Size (mm)': oht_df['Inlet Line Size mm'],
                                                                                                              'Delivery Line': oht_df['Delivery_line'],

                                                                                                              },
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=30, zoom=10,
                        color = 'Division')

        elif(selected_val == 'well'):



            fig = px.scatter_mapbox(well_df, lat="Lat", lon="Long", hover_name = well_df['Tubewell_Name'].values, hover_data = {'Year of Construction': well_df['Year'],

                                                                                                              'Q (lpm)': well_df['Q_lpm'],
                                                                                                              'Motor Power (HP)': well_df['Motor_HP'],

                                                                                                              },
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=30, zoom=10,
                        color = 'Division')


        fig.update_layout(mapbox_style=bmap,
                          mapbox_zoom=10.97, mapbox_center = {"lat": 30.323 , "lon": 78.04})
        fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


        graphobjmap = dcc.Graph(id = 'map-plot', figure = fig)

        return graphobjmap

    elif(ncc == [0,0,1,0,0,0,0,0]):

        if(zoneshow):
            trace2 = [go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id, hovertext=zones_df.Name,marker_opacity=1, marker_line_width = 2, showlegend=False, showscale=False, name = 'Divisions'),go.Choroplethmapbox(geojson=json_file, locations=df.GRID_ID, z=df['ET_mean_{}'.format(selected_val)], hovertext=df['ET_mean_{}'.format(selected_val)],
                                            colorscale="Viridis", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = 'Evapotranspiration: %{hovertext}', name = selected_val.upper())]

        else:

            trace2 = [go.Choroplethmapbox(geojson=json_file, locations=df.GRID_ID, z=df['ET_mean_{}'.format(selected_val)], hovertext=df['ET_mean_{}'.format(selected_val)],
                                            colorscale="Viridis", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = 'Evapotranspiration: %{hovertext}', name = selected_val.upper())]
        fig = go.Figure(data=trace2)
        fig.update_layout(mapbox_style=bmap,
                          mapbox_zoom=10.35, mapbox_center = {"lat": 30.33 , "lon": 78.068})
        fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


        graphobjmap = dcc.Graph(id = 'map-plot', figure = fig)

        return graphobjmap

    elif(ncc == [0,0,0,1,0,0,0,0]):





        trace2 = [go.Scattermapbox(
                    lat=np.array(feature["geometry"]["coordinates"])[:, 1],
                    lon=np.array(feature["geometry"]["coordinates"])[:, 0],
                    mode="lines",
                    hoverinfo = 'none',
                    showlegend=False,
                    line=dict(width=8, color="#5834eb")
                )
                for feature in stream_json[selected_val]["features"]]

        fig = go.Figure(data=trace2)
        fig.update_layout(mapbox_style=bmap,
                          mapbox_zoom=10.35, mapbox_center = {"lat": 30.33 , "lon": 78.068})
        fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


        graphobjmap = dcc.Graph(id = 'map-plot', figure = fig)

        return graphobjmap

    elif(ncc == [0,0,0,0,0,0,1,0]):

        if(zoneshow):
            trace2 = [go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id, hovertext=zones_df.Name,marker_opacity=1, marker_line_width = 2, showlegend=False, showscale=False, name = 'Divisions'),
                      go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df[selected_val], hovertext=lulc_df['names_' + selected_val],
                                            colorscale="Viridis", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = selected_val + ': %{hovertext}', name = 'Class')]

        else:

            trace2 = [go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df[selected_val], hovertext=lulc_df['names_' + selected_val],
                                            colorscale="Viridis", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = selected_val + ': %{hovertext}', name = 'Class')]
        fig = go.Figure(data=trace2)
        fig.update_layout(mapbox_style=bmap,
                          mapbox_zoom=10.35, mapbox_center = {"lat": 30.33 , "lon": 78.068})
        fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


        graphobjmap = dcc.Graph(id = 'map-plot', figure = fig)

        return graphobjmap

    elif(ncc == [0,0,0,0,0,1,0,0]):

        if(zoneshow):
            trace2 = [go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id, hovertext=zones_df.Name,marker_opacity=1, marker_line_width = 2, showlegend=False, showscale=False, name = 'Divisions'),
                      go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df['gwp_class'], hovertext=lulc_df['gw_pot'],
                                            colorscale="Viridis", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = 'Ground Water Potential : %{hovertext}', name = 'GWP')]

        else:


            trace2 = [go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df['gwp_class'], hovertext=lulc_df['gw_pot'],
                                            colorscale="Viridis", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = 'Ground Water Potential : %{hovertext}', name = 'GWP')]
        fig = go.Figure(data=trace2)
        fig.update_layout(mapbox_style=bmap,
                          mapbox_zoom=10.35, mapbox_center = {"lat": 30.33 , "lon": 78.068})
        fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


        graphobjmap = dcc.Graph(id = 'map-plot', figure = fig)

        return graphobjmap

    elif(ncc == [0,1,0,0,0,0,0,0]):

        if(selected_val == 'elevation'):

            hover_prefix = 'Elevation'
            hover_suffix = 'meters'
        elif(selected_val == 'aspect'):

            hover_prefix = 'Aspect'
            hover_suffix = 'Aspect'
        elif(selected_val == 'curvature'):

            hover_prefix = 'Curvature'
            hover_suffix = 'Curvature'
        elif(selected_val == 'slope'):

            hover_prefix = 'Slope'
            hover_suffix = 'Slope'

        elif(selected_val == 'hillshade'):

            hover_prefix = 'Hillshade'
            hover_suffix = 'Hillshade'


        if(zoneshow):
            trace2 = [go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id, hovertext=zones_df.Name,marker_opacity=1, marker_line_width = 2, showlegend=False, showscale=False, name = 'Divisions'),
                      go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df[selected_val], hovertext=lulc_df[selected_val],
                                            colorscale="Viridis", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = hover_prefix +  ' : %{hovertext}', name = hover_suffix)]

        else:

            trace2 = [go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df[selected_val], hovertext=lulc_df[selected_val],
                                            colorscale="Viridis", marker_opacity=op, marker_line_width = 0,showlegend=False, showscale=False, hovertemplate = hover_prefix +  ' : %{hovertext}', name = hover_suffix)]
        fig = go.Figure(data=trace2)
        fig.update_layout(mapbox_style=bmap,
                          mapbox_zoom=10.35, mapbox_center = {"lat": 30.33 , "lon": 78.068})
        fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


        graphobjmap = dcc.Graph(id = 'map-plot', figure = fig)

        return graphobjmap


# ### Callback to control the Legend Box (overlay)


@app.callback(Output('overlay', 'children'),
             [Input('year-select', 'value'), Input('button-item8','active'), Input('button-item2','active'), Input('button-item7','active'), Input('button-item','active'), Input('button-item6','active'), Input('button-item5','active'), Input('button-item0','active')])
def select_ground_water19(selected_val, activeornot, n2, n4, n5, n6, n7,zonebut):
    if(activeornot):

        return html.Div([

            html.P('Ground Water Level (m)', style = {'font-weight': 'bold', 'text-align': 'center'}),

            html.Img(src='https://manaruchi.github.io/rdbu.png', style = {'margin-left': '8px', 'transform':'rotate(180deg)',  'width': '80%', 'height': '20px','align-content': 'center'}),

            html.Table(html.Tr([html.Td('{}'.format(round(ground_water_df['GWL_{}'.format(selected_val)].min(),2))), html.Td('{}'.format(round(ground_water_df['GWL_{}'.format(selected_val)].max(),2)), style = {'text-align': 'right'})]), style = {'width': '90%'})
        ])

    if(n2):

        return html.Div([

            html.P('Evapotranspiration (mm)', style = {'font-weight': 'bold', 'text-align': 'center', 'font-size': 'small'}),

            html.Img(src='https://manaruchi.github.io/viridis.png', style = {'margin-left': '8px', 'width': '80%', 'height': '20px','align-content': 'center'}),

            html.Table(html.Tr([html.Td('{}'.format(round(df['ET_mean_{}'.format(selected_val)].min(),2))), html.Td('{}'.format(round(df['ET_mean_{}'.format(selected_val)].max(),2)), style = {'text-align': 'right'})]), style = {'width': '90%'})
        ])


    if(n4):

        if(selected_val == 'LULC_Code'):

            return html.Div([

                html.P('Land Use Land Cover', style = {'font-weight': 'bold', 'text-align': 'center'}),



                html.Table([html.Tr([html.Th('Color'), html.Th('Description')]),
                           html.Tr([html.Td(style = {'background-color': '#5c2269'}), html.Td('Urban Area', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#5984a2'}), html.Td('Cropland', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#55c18d'}), html.Td('Barrenland', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#fcea49'}), html.Td('Forest', style = {'padding-left': '2px'})])],style = {'width': '90%', 'font-size': 'small'})
            ])

        elif(selected_val == 'Litho'):

            return html.Div([

                html.P('Lithology', style = {'font-weight': 'bold', 'text-align': 'center'}),



                html.Table([html.Tr([html.Th('Color'), html.Th('Description'),html.Th('Color'), html.Th('Description'),html.Th('Color'), html.Th('Description'),html.Th('Color'), html.Th('Description')]),
                           html.Tr([html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 1', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 2', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 3', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 4', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 5', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 6', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 7', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 8', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 9', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#488d9d'}), html.Td('Class 10', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 11', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 12', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 13', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 14', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#56bd93'}), html.Td('Class 15', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#63c78f'}), html.Td('Class 16', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#75cf84'}), html.Td('Class 17', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 20', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 21', style = {'padding-left': '2px'}),html.Td(style = {'background-color': '#5c2269'}), html.Td('Class 22', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#5984a2'}), html.Td('Class 23', style = {'padding-left': '2px'})]),
                           ],style = {'width': '90%', 'font-size': 'small'})
            ])

    if(n5):

        if(selected_val == 'elevation'):

            title_val = 'Elevation (m)'

        elif(selected_val == 'aspect'):

            title_val = 'Aspect'

        elif(selected_val == 'curvature'):

            title_val = 'Curvature'

        elif(selected_val == 'slope'):

            title_val = 'Slope'

        elif(selected_val == 'hillshade'):

            title_val = 'Hillshade'

        return html.Div([

            html.P(title_val, style = {'font-weight': 'bold', 'text-align': 'center'}),

            html.Img(src='https://manaruchi.github.io/viridis.png', style = {'margin-left': '8px', 'width': '80%', 'height': '20px','align-content': 'center'}),

            html.Table(html.Tr([html.Td('{}'.format(round(other_details_df[selected_val].min(),2))), html.Td('{}'.format(round(other_details_df[selected_val].max(),2)), style = {'text-align': 'right'})]), style = {'width': '90%'})
        ])

    if(n6):



        return html.Div([

            html.P('Ground Water Potential', style = {'font-weight': 'bold', 'text-align': 'center'}),



            html.Table([html.Tr([html.Th('Color'), html.Th('Description')]),
                       html.Tr([html.Td(style = {'background-color': '#5c2269'}), html.Td('Low', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#5984a2'}), html.Td('Moderate', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#55c18d'}), html.Td('High', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#fcea49'}), html.Td('Very High', style = {'padding-left': '2px'})])],style = {'width': '90%', 'font-size': 'small'})
        ])

    if(n7):   #Urbanization

        return html.Div([

            html.P('Urbanisation', style = {'font-weight': 'bold', 'text-align': 'center'}),



            html.Table([html.Tr([html.Th('Color'), html.Th('Description')]),
                       html.Tr([html.Td(style = {'background-color': '#053061'}), html.Td('Urban Area', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#a7d0e4'}), html.Td('Cropland', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#f7b799'}), html.Td('Barrenland', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#67001f'}), html.Td('Forest', style = {'padding-left': '2px'})])],style = {'width': '90%', 'font-size': 'small'})
        ])

    if(zonebut):   #Zone

        return html.Div([

            html.P('Zones', style = {'font-weight': 'bold', 'text-align': 'center'}),



            html.Table([html.Tr([html.Th('Color'), html.Th('Description')]),
                       html.Tr([html.Td(style = {'background-color': '#0d0887'}), html.Td('Raipur Division', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#6901a6'}), html.Td('Pithuwala Division', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#b02a90'}), html.Td('South Division', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#e06561'}), html.Td('North Division', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#fba836'}), html.Td('ADB', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#f0f921'}), html.Td('Maintenance Division', style = {'padding-left': '2px'})]),],style = {'width': '90%', 'font-size': 'small'})
        ])


@app.callback(Output('overlay', 'style'),
             [Input('year-select', 'value'), Input('button-item8','active'), Input('button-item2','active'),  Input('button-item7','active'), Input('button-item','active'), Input('button-item6','active'),Input('button-item5','active'),Input('button-item0','active')])
def select_ground_water19(selected_val, activeornot, n2,  n4, n5, n6, n7, zonebut):
    if(activeornot):

        return {'bottom': '1%', 'left': '1%', 'z-index': 2,'position': 'absolute', 'padding': 10, 'border-radius': 0, 'border': '2px solid #ffffff', 'width': 200, 'background-color': '#ffffff', 'opacity': 0.8, 'align-content': 'center'}

    if(n2):

        return {'bottom': '1%', 'left': '1%', 'z-index': 2,'position': 'absolute', 'padding': 10, 'border-radius': 0, 'border': '2px solid #ffffff', 'width': 200, 'background-color': '#ffffff', 'opacity': 0.8, 'align-content': 'center'}




    if(n4):

        if(selected_val == 'LULC_Code'):

            return {'bottom': '1%', 'left': '1%', 'z-index': 2,'position': 'absolute', 'padding': 10, 'border-radius': 0, 'border': '2px solid #ffffff', 'width': 200, 'background-color': '#ffffff', 'opacity': 0.8, 'align-content': 'center'}


        elif(selected_val == 'Litho'):

            return {'bottom': '1%', 'left': '1%', 'z-index': 2,'position': 'absolute', 'padding': 10, 'border-radius': 0, 'border': '2px solid #ffffff', 'width': 450, 'background-color': '#ffffff', 'opacity': 0.8, 'align-content': 'center'}

    if(n5):

        return {'bottom': '1%', 'left': '1%', 'z-index': 2,'position': 'absolute', 'padding': 10, 'border-radius': 0, 'border': '2px solid #ffffff', 'width': 200, 'background-color': '#ffffff', 'opacity': 0.8, 'align-content': 'center'}

    if(n6):



        return {'bottom': '1%', 'left': '1%', 'z-index': 2,'position': 'absolute', 'padding': 10, 'border-radius': 0, 'border': '2px solid #ffffff', 'width': 200, 'background-color': '#ffffff', 'opacity': 0.8, 'align-content': 'center'}

    if(n7):

        return {'bottom': '1%', 'left': '1%', 'z-index': 2,'position': 'absolute', 'padding': 10, 'border-radius': 0, 'border': '2px solid #ffffff', 'width': 200, 'background-color': '#ffffff', 'opacity': 0.8, 'align-content': 'center'}
    if(zonebut):

        if(selected_val == 'overview'):

            return {'bottom': '1%', 'left': '1%', 'z-index': 2,'position': 'absolute', 'padding': 10, 'border-radius': 0, 'border': '2px solid #ffffff', 'width': 230, 'background-color': '#ffffff', 'opacity': 0.8, 'align-content': 'center'}

        elif(selected_val == 'pump'):

            return {'visibility': 'hidden'}

# ### Callback to control the statistics to show when a particular layer is selected


@app.callback(Output('stats', 'children'),
             [Input('year-select', 'value'), Input('button-item8','active'), Input('button-item2','active'), Input('button-item3','active'),Input('button-item7','active'),Input('button-item','active'),Input('button-item6','active'), Input('button-item5','active'),Input('button-item0','active')])
def select_ground_water20(selected_val, activeornot, n2, n3, n4, n5, but6, but5, zonebut):
    if(activeornot):

        gwllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0))

        gwlfig = go.Figure(data = [go.Histogram(x = ground_water_df['GWL_{}'.format(selected_val)])], layout = gwllayout)

        gwltext = 'Geohydrological, the structurally controlled intermontane Doon Valley is divisible into three zones. (a) Lesser Himalayan zone, (b) Synclinal Central zone and (c) Siwalik zone. The steeply sloping Lesser Himalayan Zone consisting of rocks of the Lesser Himalayan formations (phyllites and quartzite, shales, sandstones, greywackes, slates, dolomite and limestone of Jaunsar, Blaini-Krol-Tal sequence) has secondary porosity and permeability, and is characterized by springs and seepages. The Synclinal Central Zone, a synclinal depression between Lesser Himalaya and Shivalik is occupied by Doon Gravel. The Doon gravels have primary porosity and permeability and form the main aquifer in the area. The groundwater is present in multi-layered aquifers under unconfined and semi-confined conditions. The subsurface hydrology indicates that the horizons comprising boulders and gravels set in a coarse sandy matrix are the main water-bearing horizons. The discharge from the tube wells varies from 600 to 3000 l/min through a tapped horizon of 30 to 50 m with a depression of 2 to 7 m. The Siwalik zone consists of rocks of Middle (friable, medium grained, grey-coloured massive sandstone and mudstone) and Upper Siwalik (alternate polymictic conglomerate and subordinate grey micaceous sandstone). Groundwater is present under semi-confined and confined conditions and the water table is relatively deep. Although the conglomerate unit of the Upper Siwalik is highly porous and permeable, water quickly leaves the area as surface runoff.'

        gwltext2 = 'There are six developmental blocks in District Dehradun. Two blocks (Chakrata and Kalsi) fall in mountainous terrain where the slopes are high and water resources are not estimated for these blocks. Water Resources are estimated, using GEC 1997 methodology, for Raipur, Doiwala, Sahaspur and Vikas Nagar blocks as the topography is by and large plain, in these blocks. The block areas are divided into command and non-command. Draft for all uses and recharge from all sources are calculated for command and non-command areas.'

        detailscard = dbc.Card([dbc.CardHeader('Ground Water Level'),dbc.CardBody([gwltext, html.P(), gwltext2], style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)


        return dcc.Loading([detailscard,dbc.Card([dbc.CardHeader('Ground Water Level Histogram'),dbc.CardBody(dcc.Graph(figure = gwlfig, style = {'width': '100%', 'height': '200px'}))], style = {'margin-top': '5px'},color="dark", outline=True)], type = 'dot')

    if(n2):

        gwllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0))

        gwlfig = go.Figure(data = [go.Histogram(x = df['ET_mean_{}'.format(selected_val)])], layout = gwllayout)

        etcardintrotext = 'Evapotranspiration is the water lost in the atmosphere by evaporation and transpiration. Evaporation implies losing from large bodies of water, such as lakes and rivers, wetlands, bare soil and snow cover.'

        etcardmethod = 'The evapotranspiration map is prepared using the Moderate Resolution Imaging Spectroradiometer (MODIS) satellite data product named MOD16A2.006.'

        etcardcontent = html.Div([html.Div(etcardintrotext), html.Div(etcardmethod)])

        etcard = dbc.Card([dbc.CardHeader('Evapotranspiration'),dbc.CardBody(etcardcontent, style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)

        etcard2body = html.Tbody([
            html.Tr([html.Td('The time series of Evapotranspiration plotted for the year 2001-2019 showed that the Dehradun basin has an increasing ET trend. The 20 yr. maximum value ranged from 0 to 4 mm per day, with a mean value of 1.4 mm per day and a standard deviation of 0.93 mm/day.')]),
            html.Tr(html.Td('The 8 daily trend reveals that the region has shown an increment in evapotranspiration in the past 20 years. This increase in evapotranspiration can result in a decrease in surface runoff, which can further create stress on water demand.')),
            html.Tr(html.Td('The spatial analysis of 20 years Average Evapotranspiration for Dehradun basin reveals that the value of ET ranged from 3.7mm to 15.9 mm. The lower value is observed in the eastern part of the basin while the higher value is observed in the northern and southern part, while the central part of the basin lacks ET estimation due the absence of vegetation cover.')),
            html.Tr(html.Td('The spatial analysis of {} Average Evapotranspiration for Dehradun basin reveals that the value of ET ranged from {} mm to {} mm. The lower value is observed in the eastern part of the basin while the higher value is observed in the northern and southern part, while the central part of the basin lacks ET estimation due the absence of vegetation cover.'.format(selected_val, np.min(df['ET_mean_{}'.format(selected_val)]), np.max(df['ET_mean_{}'.format(selected_val)]) )))
        ])

        etcardc2 = dbc.Table(etcard2body, striped=True, bordered=True, hover=True, style = {'font-size': 'small'})

        etcardass = dbc.Card([dbc.CardHeader('Analysis'),dbc.CardBody(etcardc2, style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)




        return dcc.Loading([etcard, etcardass, dbc.Card([dbc.CardHeader('Evapotranspiration Histogram'),dbc.CardBody(dcc.Graph(figure = gwlfig, style = {'width': '100%', 'height': '200px'}))], style = {'margin-top': '5px'},color="dark", outline=True)], type = 'dot')

    if(n3):

        gwllayoutw = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0))

        gwlfig = go.Figure(data = [go.Pie(labels= ['Seasonal', 'New Seasonal', 'Lost Seasonal', 'Ephemeral Permanent', 'Ephemeral Seasonal'],
                                          values= [10062.35,6193.67,45684.67, 774.52, 14250.25], hole=.2, name = '',
                                          hovertemplate = 'Transition Class: %{label} <br> Area: %{value} km2')], layout = gwllayoutw)
        gwlfig.update_layout(legend = dict(font = dict(size = 8, color = "black")))

        streamtext = 'Mapping of Dehradun rivers and streams for every five years of the interval from 1990 to 2019 yield helpful results for the change detection in surface water due to tectonic and climate factors. The flow of river pattern explains a lot about the path, it has been observed that the development of lineament and fault changed the course of the river, maximum shift and alteration of flow pattern observed in between 1999 to 2004. The Progression of the path of rivers from its previous state to new ways indicating climate fluctuation as well as the development of structural activities. The behaviour of rivers flowing from 2004 to 2019 looks very different from each other. Surface water change detection for the Dehradun district showed the following characteristics:'

        streamtext2 = html.Tbody([
            html.Tr(html.Td('Seasonal Streams are the river which flows only for a part of a year only after a significant rainfall are about 13% in the basin, and the basin has lost around 18% of seasonal stream which is now converted to ephemeral seasonal (i.e. with no base flow).')),
            html.Tr(html.Td('The result showed that the lost seasonal water i.e. the seasonal water which is now converted into land is about 60%, which clearly shows the stress on water resources due to urbanization.')),
            html.Tr(html.Td('Also it is seen that 1% of the permanent water has now been converted into ephemeral permanent which clearly implies that there is a decrease in the permanent water cover.')),
            html.Tr(html.Td('However, the region has also seen an 8% conversion of land into the streams, which might contribute to the increase in the surface water.'))
        ])

        detailscard = dbc.Card([dbc.CardHeader('Surface Water'),dbc.CardBody([streamtext, html.P(), dbc.Table(streamtext2, striped=True, bordered=True, hover=True, style = {'font-size': 'small'})], style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)

        return dcc.Loading([detailscard, dbc.Card([dbc.CardHeader('Areal distribution of transition classes'),dbc.CardBody(dcc.Graph(figure = gwlfig, style = {'width': '100%', 'height': '200px'}))], style = {'margin-top': '5px'},color="dark", outline=True)], type = 'dot')

    if(n4):

        gwllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0))

        gwlfig = go.Figure(data = [go.Pie(labels=np.unique(lulc_df['names_' + selected_val].values, return_counts = True)[0], values=np.unique(lulc_df[selected_val].values, return_counts = True)[1])], layout = gwllayout)

        if(selected_val == 'LULC_Code'):

            title_card = 'LULC Areal Distribution'

            lulctext1 = 'Land cover is the physical material at the surface of the earth. Land use is a description of how people utilize the land for socio-economic activities. When used together with the phrase Land Use / Land Cover (LULC) generally refers to the categorization or classification of human activities and natural elements on the landscape within a specific time frame based on established scientific and statistical methods of analysis of appropriate source materials. To understand land use land cover present in the defined study area, data provided by the European Space Agency is taken from 1995, 2000, 2005, 2010, 2015 and 2020. Change in LULC in terms of Area (sq kms) is represented in the bar plot below:'

            lulctext2 = 'The statistical analysis of the area shows that the urban area has increased many folds. The Forest cover has decreased from 1995 to 2000 but from hence has almost remained unchanged. While the major increase in the urban areas is due to the conversion of barren areas and agricultural lands into urban areas. From the current study it is evident that there is considerable decrease in Forest cover, Crop and Barren land for the period of 1995 to 2015. The Built Up class is showing an increasing trend and thereby resulting in the inference that the population pressure is playing a very active role towards diminishing forest cover. Tthe built-up area has increased by 650% in the period from 1995-2015 in the Dehradun basin whereas the forest, barren and cropland has decreased by 3,11 and 12.5% respectively.'

            lulctext3 = 'Similarly, zone wise land use land cover change analysis revealed that there has been a considerable loss of forest cover (about 6.21 sq. km.), barren (about 4.61 sq. km) and crop (about 9.95 sq. km ) in the Dehradun zones.'

            #Data for the grouped bar plot
            lulcbarclasses = ['Urban', 'Crop', 'Barren', 'Forest']


            lulcbarfig = go.Figure(data=[
                    go.Bar(name='1995', x=lulcbarclasses, y=[8.18, 168.68, 95.08, 717.32], hovertemplate = 'Class: %{x} <br> Area: %{y} km2'),
                    go.Bar(name='2000', x=lulcbarclasses, y=[14.26, 176.95, 99.36, 698.68], hovertemplate = 'Class: %{x} <br> Area: %{y} km2'),
                    go.Bar(name='2005', x=lulcbarclasses, y=[33.56, 165.45, 93.37, 696.88], hovertemplate = 'Class: %{x} <br> Area: %{y} km2'),
                    go.Bar(name='2010', x=lulcbarclasses, y=[43.55, 159.17, 88.90, 697.64], hovertemplate = 'Class: %{x} <br> Area: %{y} km2'),
                    go.Bar(name='2015', x=lulcbarclasses, y=[60.95,147.67, 84.82, 696.02], hovertemplate = 'Class: %{x} <br> Area: %{y} km2')

                ], layout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0)))

            lulcbarfig.update_layout(barmode='group')

            lulctext = [lulctext1, html.P(), dcc.Graph(figure = lulcbarfig, style = {'width': '100%', 'height': '200px'}), html.P(), lulctext2, html.P(), lulctext3]

        elif(selected_val == 'Litho'):

            title_card = 'Lithology Classes Areal Distribution'

        lulccard = dbc.Card([dbc.CardHeader('Analysis'),dbc.CardBody(lulctext, style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)

        return dcc.Loading([lulccard, dbc.Card([dbc.CardHeader(title_card),dbc.CardBody(dcc.Graph(figure = gwlfig, style = {'width': '100%', 'height': '200px'}))], style = {'margin-top': '5px'},color="dark", outline=True)], type = 'dot')

    if(n5):

        gwllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0))

        gwlfig = go.Figure(data = [go.Histogram(x = other_details_df[selected_val])], layout = gwllayout)

        if(selected_val == 'elevation'):

            text = 'The elevation data is obtained from Shuttle Radar Topography Mission (SRTM)-Digital Elevation Model available at USGS earth explorer. It can be seen that almost 50% of the Dehradun basin covers the elevation range of 503-775 m and lies in the central and western part. In the eastern region, the elevation higher than 1493m exists. Areal distribution of different elevation classes is shown below.'

            tabledf = pd.DataFrame({
                'Class': ['Very Low', 'Low', 'Moderate', 'High', 'Very High'],
                'Elev. Range': ['503-775', '776-1107', '1108-1493', '1494-1881', '1882-2764'],
                'Area (km2)': [429.06, 149.95, 96.94, 122.10, 59.78],
                '%age': [50, 17.5, 11.3, 14.2, 7.0]
            })

            tblfig = go.Figure(data = [go.Pie(labels=tabledf['Elev. Range'], values= tabledf['Area (km2)'],
                                              hovertemplate = 'Elevation Range (m): %{label} <br> Area: %{value} sq. km.', name = '', hole=.2)], layout = gwllayout)

        elif(selected_val == 'aspect'):

            text = 'The Aspect of a region identifies the steepest downslope direction from each cell to its neighbours. It can be thought of as slope direction or the compass direction of a hill face. The aspect map derived from SRTM DEM represents Aspect is measured clockwise in degrees from zero, due north to 360. The detailed aspect analysis for the Dehradun basin reveals that the majority of the slope faces south and southwest direction i.e. faces the sun. This increases the rate of evaporation and transpiration. Areal distribution of different aspect classes is shown below.'

            tabledf = pd.DataFrame({
                'Class': ['Flat', 'North', 'Norteast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest', 'North'],
                'Aspect': ['-1', '0-22.5', '22.5-67.5', '67.5-112.5', '112.5-157.5','157.5-202.5','202.5-247.5','247.5-292.5','292.5-337.5','337.5-360'],
                'Area (km2)': [2.16,47.29,76.33,91.08,111.85,133.81,137.01,119.09,97.07,42.12],
                '%age': [0.25,5.51,8.89,10.62,13.06,15.60,15.97,13.88,11.31,4.91]
            })

            tblfig = go.Figure(data = [go.Pie(labels=tabledf['Class'], values= tabledf['Area (km2)'], hole=.2,
                                             hovertemplate = 'Aspect Class: %{label} <br> Area: %{value} sq. km.', name = '' )], layout = gwllayout)

        elif(selected_val == 'curvature'):

            text = 'The values in the curvature class reflect the morphology of the topography. Convex indicates a positive dimension, concave indicates a negative one, and zero indicates a smooth surface. Most of the Dehradun city lies in the Linear curvature zones as observed from the map. The Dehradun basin has almost 80% of the region lying in the linear curvature.'

            tabledf = pd.DataFrame({
                'Class': ['Convex(<0)', 'Linear(0)', 'Concave(>0)'],
                '%age': [8,80,12],
                'area': [67.33, 689.24, 101.26]
            })

            tblfig = go.Figure(data = [go.Pie(labels=tabledf['Class'], values= tabledf['area'], hole=.2,
                                             hovertemplate = 'Curvature Class: %{label} <br> Area: %{value} sq. km.', name = '' )], layout = gwllayout)

        elif(selected_val == 'hillshade'):

            text = 'A hill shade specifies the brightness for each cell on a map image. This brightness depends on how the cell is positioned in relation to a single light source (e.g., the sun). The highly illuminated zone would result in more amount of evaporation and transpiration. Majority of the Dehradun city lies in the High sun- illumination zone. Also, the eastern part of the Dehradun basin, due to the presence of Hills, show varying illumination. It can be seen that 55% of the Dehradun basin is Highly illuminated and only 4.9% is very low illuminated. Areal distribution of different illumination classes are shown in figure below.'

            tabledf = pd.DataFrame({
                'Class': ['Very Low', 'Low', 'Moderate', 'High', 'Very High'],

                'area': [41.86,86.33,124.14,474.29,125.57]
            })

            tblfig = go.Figure(data = [go.Pie(labels=tabledf['Class'], values= tabledf['area'], hole=.2,
                                             hovertemplate = 'Illumination Class: %{label} <br> Area: %{value} sq. km.', name = '' )], layout = gwllayout)

        elif(selected_val == 'slope'):

            text = 'Slope defines the change of elevation in a particular area which influences the runoff. Generally, in gentle slopes, the movement of water is slow, which allows more percolation into the ground. On the other hand, the steep slope increases the rate of runoff and decreases the percolation and infiltration into the ground. Slope map was produced from SRTM DEM with 30 m resolution. For the Dehradun river basin, the slope analysis is shown in the table. It could be seen that almost 46% of the Dehradun basin covers the slope range of 0-7.7° and lies in the central and western part. The slopes ranging in the high and very high class, i.e. 28.13 -75.48° lie in the eastern region.'

            tabledf = pd.DataFrame({
                'Class': ['Very Low', 'Low', 'Moderate', 'High', 'Very High'],

                'area': [394.56,138.41,137.82,127.63,59.41]
            })

            tblfig = go.Figure(data = [go.Pie(labels=tabledf['Class'], values= tabledf['area'], hole=.2,
                                             hovertemplate = 'Slope Class: %{label} <br> Area: %{value} sq. km.', name = '' )], layout = gwllayout)


        table = dcc.Graph(figure = tblfig, style = {'width': '100%', 'height': '200px'})

        infocard = dbc.Card([dbc.CardHeader('Analysis'),dbc.CardBody([text, html.P() ,table], style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)


        return dcc.Loading([infocard, dbc.Card([dbc.CardHeader('{} Histogram'.format(selected_val.capitalize())),dbc.CardBody(dcc.Graph(figure = gwlfig, style = {'width': '100%', 'height': '200px'}))], style = {'margin-top': '5px'},color="dark", outline=True)], type = 'dot')

    if(but6):

        gwllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0))

        gwlfig = go.Figure(data = [go.Histogram(x = lulc_df['gw_pot'])], layout = gwllayout)

        gpottext = 'A standard approach has been proposed for demarcating the zonation map of groundwater potential with the use of a GIS-based analysis of the hierarchy technique. The proposed technique was implemented by assessing Dehradun Basin, Uttarakhand (India) groundwaters capacity. The present study explores the possible/potential groundwater recharge zone by examining the factors that affect it. For the creation of the thematic layers with nine parameters: Elevation, Slope, Drainage, Land use Land Cover, Hydrologic Soil Group, Lithology, Geomorphology, Lineament and Rainfall, satellite data, DEM, traditional maps, and rainfall data were employed. According to expert advice from previous literature reviews and local experience, acceptable weights were allocated to the selected nine layers and their features on a Saaty’s scale. By means of an analytical hierarchy (AHP) process, the assigned weights and functions of the thematic layers were then normalized. These thematic layers were incorporated by a weighted overlay module into the GIS environment to demarcate possible groundwater recharging zones in the study area.'

        gpottext2 = 'The results indicate that most effective Groundwater recharge potential zonation was located within the city area. In this region hydrologic soil group, pediplain and cropland have high infiltration ability. Also very good ground water availability was found in the central and western part of the region due to the presence of low slope, low elevation and high lineaments density.The zone wise groundwater potential analysis revealed that four out of six zones namely Raipur Division, South Division, ADB & Maintenance Division lies in the very high groundwater potential zone, and Pithuwala Division & North Division lies in the High groundwater potential zones.'



        gpotcard = dbc.Card([dbc.CardHeader('Ground Water Potential'),dbc.CardBody([gpottext, html.P(), gpottext2], style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)



        return dcc.Loading([gpotcard,dbc.Card([dbc.CardHeader('Ground Water Potential Histogram'),dbc.CardBody(dcc.Graph(figure = gwlfig, style = {'width': '100%', 'height': '200px'}))], style = {'margin-top': '5px'},color="dark", outline=True)], type = 'dot')

    if(but5):

        gwllayoutw = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0))

        gwlfig = go.Figure(data = [go.Pie(labels= ['Seasonal', 'New Seasonal', 'Lost Seasonal', 'Ephemeral Permanent', 'Ephemeral Seasonal'],
                                          values= [10062.35,6193.67,45684.67, 774.52, 14250.25], hole=.2, name = '',
                                          hovertemplate = 'Transition Class: %{label} <br> Area: %{value} km2')], layout = gwllayoutw)
        gwlfig.update_layout(legend = dict(font = dict(size = 8, color = "black")))

        streamtext = 'Land-use in the Dehradun Basin has undergone massive changes following Hilly settlement and these changes have significantly modified the hydrological regime of the catchment. The replacement of perennial deep-rooted native vegetation with shallow rooted vegetation including perennial grasses, annual grasses and annual crops has resulted in major changes to the catchment-wide evapotranspiration, and stream flow. Similarly, zone wise land use land cover change analysis revealed that there has been a considerable loss of forest cover (about 6.21 sq. km.), barren (about 4.61 sq. km) and crop (about 9.95 sq. km ) in the Dehradun zones.'

        lulcbarclasses = ['Urban', 'Crop', 'Barren', 'Forest']

        lulc2barfig = go.Figure(data=[
                    go.Bar(name='1995', x=lulcbarclasses, y=[7.03,88.68,38.43,73.56], hovertemplate = 'Class: %{x} <br> Area: %{y} km2'),
                    go.Bar(name='2000', x=lulcbarclasses, y=[12.31,91.82,39.42,64.14], hovertemplate = 'Class: %{x} <br> Area: %{y} km2'),
                    go.Bar(name='2005', x=lulcbarclasses, y=[28.51,82.32,35.13,61.74], hovertemplate = 'Class: %{x} <br> Area: %{y} km2'),
                    go.Bar(name='2010', x=lulcbarclasses, y=[36.37,77.44,31.90,61.99], hovertemplate = 'Class: %{x} <br> Area: %{y} km2'),
                    go.Bar(name='2015', x=lulcbarclasses, y=[50.17,68.02,28.84,60.66], hovertemplate = 'Class: %{x} <br> Area: %{y} km2')

                ], layout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0)))

        lulc2barfig.update_layout(barmode='group')

        detailscard = dbc.Card([dbc.CardHeader('Urbanisation'),dbc.CardBody([streamtext], style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)

        return dcc.Loading([detailscard, dbc.Card([dbc.CardHeader('Areal distribution of LULC classes'),dbc.CardBody(dcc.Graph(figure = lulc2barfig, style = {'width': '100%', 'height': '200px'}))], style = {'margin-top': '5px'},color="dark", outline=True)], type = 'dot')

    if(zonebut):

        gwllayoutw = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0))


        streamtext = 'Dehradun is the administrative centre and the interim capital of the state of Uttarakhand. It is also the most populous city in the Indian state of Uttarakhand. It is the administrative headquarters of the eponymous district and is governed by the Dehradun Municipal Corporation. According to 2011 census, the population of Dehradun after the inclusion of new ward in 2017 is 8,00,826 and it is projected that the population of the Dehradun will become 12,82,596 (100 Wards) in 2021 and 27,87,100 in 2052 respectively. The project will cover an area of 860 sq km of which 192.69 sq. km falls within the municipal boundary limits and remaining are the peri urban areas which are part of District/Watershed boundary.'

        area_dist_card = dbc.Card([dbc.CardHeader('Areal Distribution of Zones', style = {'font-size':'small'}),dbc.CardBody([dcc.Graph(figure = go.Figure(data = [go.Pie(labels= ['Raipur','Pithuwala','South','North','ADB','Maintenance'], values= [52,47,21,41,27,19], hole=.2, name = '', hovertemplate = 'Zone/Division: %{label} <br> Area: %{value} km2')], layout = gwllayoutw), style = {'width': '100%', 'height': '200px'})], style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)

        phy_feat_fig = make_subplots(rows=5, cols=1)

        phy_feat_fig.append_trace(go.Bar(x= ['Raipur','Pithuwala','South','North','ADB','Maintenance'], y = [617,616.6,661.4,781.9,612.3,853.2], name = '', hovertemplate = 'Zone/Division: %{label} <br> Mean Elevation: %{value} m'), row=1, col=1)
        phy_feat_fig.append_trace(go.Bar(x= ['Raipur','Pithuwala','South','North','ADB','Maintenance'], y = [172.9,175.3,195.2,195.7,196.2,194.6], name = '', hovertemplate = 'Zone/Division: %{label} <br> Mean Aspect: %{value} degrees'), row=2, col=1)
        phy_feat_fig.append_trace(go.Bar(x= ['Raipur','Pithuwala','South','North','ADB','Maintenance'], y = [-0.0014,-0.0013,-0.0002,-0.0009,0.0001,0.0010], name = '', hovertemplate = 'Zone/Division: %{label} <br> Mean Curvature: %{value}'), row=3, col=1)
        phy_feat_fig.append_trace(go.Bar(x= ['Raipur','Pithuwala','South','North','ADB','Maintenance'], y = [2.95,3.01,2.68,6.97,3.28,9.01], name = '', hovertemplate = 'Zone/Division: %{label} <br> Mean Slope: %{value} degrees'), row=4, col=1)
        phy_feat_fig.append_trace(go.Bar(x= ['Raipur','Pithuwala','South','North','ADB','Maintenance'], y = [178.31,180.07,179.11,174.41,180.92,172.75], name = '', hovertemplate = 'Zone/Division: %{label} <br> Mean Illumination: %{value}'), row=5, col=1)

        phy_feat_fig.update_layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0), xaxis_showticklabels=False, xaxis2_showticklabels=False,xaxis3_showticklabels=False, xaxis4_showticklabels=False, showlegend=False)

        phy_feat_fig.update_yaxes(title_text="Elevation", row=1, col=1)
        phy_feat_fig.update_yaxes(title_text="Aspect", row=2, col=1)
        phy_feat_fig.update_yaxes(title_text="Curvature", row=3, col=1)
        phy_feat_fig.update_yaxes(title_text="Slope", row=4, col=1)
        phy_feat_fig.update_yaxes(title_text="Hillshade", row=5, col=1)

        phy_feat_card = dbc.Card([dbc.CardHeader('Physical Features of Zones', style = {'font-size':'small'}),
                                  dbc.CardBody([dcc.Graph(figure = phy_feat_fig, style = {'width': '100%', 'height': '800px'})])],
                                 style = {'margin-top': '5px'},color="dark", outline=True)




        detailscard = dbc.Card([dbc.CardHeader('Introduction'),dbc.CardBody([streamtext], style = {'font-size': 'small', 'text-align': 'justify'})], style = {'margin-top': '5px'},color="dark", outline=True)

        return dcc.Loading([detailscard, area_dist_card,phy_feat_card], type = 'dot')




# ### Callback to control the dynamic information when user clicks on a grid


@app.callback(Output('selection', 'children'),
             [Input('year-select', 'value'), Input('button-item8','active'), Input('button-item2','active'), Input('button-item3','active'), Input('button-item','active'), Input('button-item0','active'), Input('button-item7','active'), Input('button-item6','active'), Input('button-item5','active'),Input('map-plot','clickData')])
def select_ground_water21(selected_val, activeornot, n2, n3, n4, n0, but7, but6, but5, dataclicked):
    if(activeornot):

        oid_val =  dataclicked['points'][0]['location']

        mini_df = ground_water_df[ground_water_df['OID_'] == oid_val]

        mini_df_vals = [mini_df['GWL_jan11'].mean(), mini_df['GWL_may11'].mean(), mini_df['GWL_aug11'].mean(), mini_df['GWL_nov11'].mean(),
                        mini_df['GWL_jan15'].mean(), mini_df['GWL_may15'].mean(), mini_df['GWL_aug15'].mean(), mini_df['GWL_nov15'].mean(),
                        mini_df['GWL_jan19'].mean(), mini_df['GWL_may19'].mean(), mini_df['GWL_aug19'].mean(), mini_df['GWL_nov19'].mean(),
                       ]

        y_vals = ['Jan2011', 'May2011', 'Aug2011', 'Nov2011',
                  'Jan2015', 'May2015', 'Aug2015', 'Nov2015',
                  'Jan2019', 'May2019', 'Aug2019', 'Nov2019',
                 ]

        sgwllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=2), yaxis = {'title': 'GWL (m)'})

        sgwlfig = go.Figure(data = [go.Scatter(x = y_vals, y = mini_df_vals, mode = 'lines+markers')], layout = sgwllayout)


        location_name = other_details_df.loc[other_details_df['OID_'] == oid_val]['Location'].values[0]

        card_content = [
                dbc.CardHeader("Grid Information (#{})".format(oid_val)),
                dbc.CardBody(
                    [
                        html.H4(location_name, className="card-title", style = {'font-weight': 'bold'}),


                        html.Table([
                            html.Tr([html.Td('Centroid Location'), html.Td('({},{})'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lat'].values[0],3),round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lon'].values[0],3)))]),
                            html.Tr([html.Td('Zone'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['zone'].values[0]))]),
                            html.Tr([html.Td('Elevation'), html.Td('{} meters'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['elevation'].values[0],3)))]),
                            html.Tr([html.Td('LULC Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['names_LULC_Code'].values[0]))]),
                            html.Tr([html.Td('Lithology Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['Litho'].values[0]))]),
                        ], style = {'font-size': 'small'})
                    ]
                ),
            ]

        gridinfocard = dbc.Card(card_content, color="dark", outline=True)



        return html.Div([gridinfocard, dbc.Card([

            dbc.CardHeader('GWL Time-Series for Grid ID: {}'.format(oid_val)),
            dbc.CardBody(dcc.Graph(figure = sgwlfig, style = {'width': '100%', 'height': '200px'}))


        ], style = {'margin-top': '5px'},color="dark", outline=True),
                         ])

    if(but6):

        oid_val =  dataclicked['points'][0]['location']

        mini_df = ground_water_df[ground_water_df['OID_'] == oid_val]

        mini_df_vals = [mini_df['GWL_jan11'].mean(), mini_df['GWL_may11'].mean(), mini_df['GWL_aug11'].mean(), mini_df['GWL_nov11'].mean(),
                        mini_df['GWL_jan15'].mean(), mini_df['GWL_may15'].mean(), mini_df['GWL_aug15'].mean(), mini_df['GWL_nov15'].mean(),
                        mini_df['GWL_jan19'].mean(), mini_df['GWL_may19'].mean(), mini_df['GWL_aug19'].mean(), mini_df['GWL_nov19'].mean(),
                       ]

        y_vals = ['Jan2011', 'May2011', 'Aug2011', 'Nov2011',
                  'Jan2015', 'May2015', 'Aug2015', 'Nov2015',
                  'Jan2019', 'May2019', 'Aug2019', 'Nov2019',
                 ]

        sgwllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=2), yaxis = {'title': 'GWL (m)'})

        sgwlfig = go.Figure(data = [go.Scatter(x = y_vals, y = mini_df_vals, mode = 'lines+markers')], layout = sgwllayout)


        location_name = other_details_df.loc[other_details_df['OID_'] == oid_val]['Location'].values[0]

        card_content = [
                dbc.CardHeader("Grid Information (#{})".format(oid_val)),
                dbc.CardBody(
                    [
                        html.H4(location_name, className="card-title", style = {'font-weight': 'bold'}),


                        html.Table([
                            html.Tr([html.Td('Centroid Location'), html.Td('({},{})'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lat'].values[0],3),round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lon'].values[0],3)))]),
                            html.Tr([html.Td('Zone'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['zone'].values[0]))]),
                            html.Tr([html.Td('Elevation'), html.Td('{} meters'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['elevation'].values[0],3)))]),
                            html.Tr([html.Td('LULC Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['names_LULC_Code'].values[0]))]),
                            html.Tr([html.Td('Lithology Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['Litho'].values[0]))]),
                        ], style = {'font-size': 'small'})
                    ]
                ),
            ]

        gridinfocard = dbc.Card(card_content, color="dark", outline=True)

        if(lulc_df.loc[lulc_df['OID_'] == oid_val]['gwp_class'].values[0] == 1):
            gwpclasstoshow = 'Low'
        elif(lulc_df.loc[lulc_df['OID_'] == oid_val]['gwp_class'].values[0] == 2):
            gwpclasstoshow = 'Moderate'
        elif(lulc_df.loc[lulc_df['OID_'] == oid_val]['gwp_class'].values[0] == 3):
            gwpclasstoshow = 'High'
        elif(lulc_df.loc[lulc_df['OID_'] == oid_val]['gwp_class'].values[0] == 4):
            gwpclasstoshow = 'Very High'

        return html.Div([gridinfocard,
                         dbc.Card([

            dbc.CardHeader('Ground Water Potential for Grid ID: {}'.format(oid_val)),
            dbc.CardBody('Ground Water Potential: {} (Class: {})'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['gw_pot'].values[0], gwpclasstoshow), style = {'font-size': 'small'})


        ], style = {'margin-top': '5px'},color="dark", outline=True),
                         dbc.Card([

            dbc.CardHeader('GWL Time-Series for Grid ID: {}'.format(oid_val)),
            dbc.CardBody(dcc.Graph(figure = sgwlfig, style = {'width': '100%', 'height': '200px'}))


        ], style = {'margin-top': '5px'},color="dark", outline=True),
                         ])

    if(n2):

        oid_val =  dataclicked['points'][0]['location']

        mini_df = df[df['OID_'] == oid_val]

        mini_df_vals = [mini_df['ET_mean_2001'].mean(), mini_df['ET_mean_2005'].mean(), mini_df['ET_mean_2010'].mean(), mini_df['ET_mean_2015'].mean(),
                        mini_df['ET_mean_2020'].mean()
                       ]

        y_vals = [2001, 2005, 2010, 2015,2020]

        sgwllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=2), yaxis = {'title': 'ET (mm)'})

        sgwlfig = go.Figure(data = [go.Bar(x = y_vals, y = mini_df_vals)], layout = sgwllayout)


        location_name = other_details_df.loc[other_details_df['OID_'] == oid_val]['Location'].values[0]

        card_content = [
                dbc.CardHeader("Grid Information (#{})".format(oid_val)),
                dbc.CardBody(
                    [
                        html.H4(location_name, className="card-title", style = {'font-weight': 'bold'}),


                        html.Table([
                            html.Tr([html.Td('Centroid Location'), html.Td('({},{})'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lat'].values[0],3),round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lon'].values[0],3)))]),
                            html.Tr([html.Td('Zone'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['zone'].values[0]))]),
                            html.Tr([html.Td('Elevation'), html.Td('{} meters'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['elevation'].values[0],3)))]),
                            html.Tr([html.Td('LULC Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['names_LULC_Code'].values[0]))]),
                            html.Tr([html.Td('Lithology Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['Litho'].values[0]))]),
                        ], style = {'font-size': 'small'})
                    ]
                ),
            ]

        gridinfocard = dbc.Card(card_content, color="dark", outline=True)



        return html.Div([gridinfocard, dbc.Card([

            dbc.CardHeader('ET Time-Series for Grid ID: {}'.format(oid_val)),
            dbc.CardBody(dcc.Graph(figure = sgwlfig, style = {'width': '100%', 'height': '200px'}))


        ], style = {'margin-top': '5px'},color="dark", outline=True),
                         ])



    if(n4):

        oid_val =  dataclicked['points'][0]['location']



        location_name = other_details_df.loc[other_details_df['OID_'] == oid_val]['Location'].values[0]

        card_content = [
                dbc.CardHeader("Grid Information (#{})".format(oid_val)),
                dbc.CardBody(
                    [
                        html.H4(location_name, className="card-title", style = {'font-weight': 'bold'}),


                        html.Table([
                            html.Tr([html.Td('Centroid Location'), html.Td('({},{})'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lat'].values[0],3),round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lon'].values[0],3)))]),
                            html.Tr([html.Td('Zone'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['zone'].values[0]))]),
                            html.Tr([html.Td('Elevation'), html.Td('{} meters'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['elevation'].values[0],3)))]),
                            html.Tr([html.Td('LULC Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['names_LULC_Code'].values[0]))]),
                            html.Tr([html.Td('Lithology Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['Litho'].values[0]))]),
                        ], style = {'font-size': 'small'})
                    ]
                ),
            ]

        gridinfocard = dbc.Card(card_content, color="dark", outline=True)

        phyfeatdf = pd.DataFrame({
            "Parameters": ['Elevation (m)', 'Aspect', 'Curvature', 'Slope', 'Hillshade'],
            "Values": [round(other_details_df.loc[other_details_df['OID_'] == oid_val]['elevation'].values[0],3),
                       round(other_details_df.loc[other_details_df['OID_'] == oid_val]['aspect'].values[0],3),
                       round(other_details_df.loc[other_details_df['OID_'] == oid_val]['curvature'].values[0],3),
                       round(other_details_df.loc[other_details_df['OID_'] == oid_val]['slope'].values[0],3),
                       round(other_details_df.loc[other_details_df['OID_'] == oid_val]['hillshade'].values[0],3)]
        })

        return html.Div([gridinfocard, dbc.Card([

            dbc.CardHeader('Physical Parameters for Grid ID: {}'.format(oid_val)),
            dbc.CardBody([dbc.Table.from_dataframe(phyfeatdf, striped=True, bordered=True, hover=True)], style = {'font-size': 'small'})


        ], style = {'margin-top': '5px'},color="dark", outline=True),
                         ])

    if(but5):

        oid_val =  dataclicked['points'][0]['location']



        location_name = other_details_df.loc[other_details_df['OID_'] == oid_val]['Location'].values[0]

        card_content = [
                dbc.CardHeader("Grid Information (#{})".format(oid_val)),
                dbc.CardBody(
                    [
                        html.H4(location_name, className="card-title", style = {'font-weight': 'bold'}),


                        html.Table([
                            html.Tr([html.Td('Centroid Location'), html.Td('({},{})'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lat'].values[0],3),round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lon'].values[0],3)))]),
                            html.Tr([html.Td('Zone'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['zone'].values[0]))]),
                            html.Tr([html.Td('Elevation'), html.Td('{} meters'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['elevation'].values[0],3)))]),
                            html.Tr([html.Td('LULC Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['names_LULC_Code'].values[0]))]),
                            html.Tr([html.Td('Lithology Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['Litho'].values[0]))]),
                        ], style = {'font-size': 'small'})
                    ]
                ),
            ]

        gridinfocard = dbc.Card(card_content, color="dark", outline=True)

        phyfeatdf = pd.DataFrame({
            "Year": ['1995','2000','2005','2010','2015'],
            "LULC Class": [other_details_df.loc[other_details_df['OID_'] == oid_val]['urban_name_1995'].values[0],
                       other_details_df.loc[other_details_df['OID_'] == oid_val]['urban_name_2000'].values[0],
                       other_details_df.loc[other_details_df['OID_'] == oid_val]['urban_name_2005'].values[0],
                       other_details_df.loc[other_details_df['OID_'] == oid_val]['urban_name_2010'].values[0],
                       other_details_df.loc[other_details_df['OID_'] == oid_val]['urban_name_2015'].values[0]]
        })

        return html.Div([gridinfocard, dbc.Card([

            dbc.CardHeader('Temporal LULC Information for Grid ID: {}'.format(oid_val)),
            dbc.CardBody([dbc.Table.from_dataframe(phyfeatdf, striped=True, bordered=True, hover=True)], style = {'font-size': 'small'})


        ], style = {'margin-top': '5px'},color="dark", outline=True),
                         ])

    if(n0):

        oid_val =  dataclicked['points'][0]['location']

        if(oid_val == 1):

            phy_prop = pd.DataFrame({
                'Property': ['Elevation', 'Aspect', 'Curvature', 'Slope', 'Hillshade'],
                'Min': [539,-1,-2.49,0,117],
                'Max': [755,359.1,3.06,38.53,235],
                'Mean': [617,172.9,-0.0014,2.95,178.31]
            })

            gwp_show_table = html.Tbody(html.Tr([html.Td('Mean'), html.Td('7.165'), html.Td('Very High',style = {'background-color': '#fcea49'})]))

            gwldatatraces = [go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [6.2,8.9,1.1,3.2,8.9,14.0,12.6,9.2,8.9,15.1,14.1,5.2],
                                        mode='lines+markers', name = 'Min', fill = None, hovertemplate = 'Month: %{x} <br>Min: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [44.8,70.0,40.7,43.1,70.0,53,42.9,45.7,70,47.9,76.3,45.7],
                                        mode='lines+markers', name = 'Max', fill = 'tonexty',hovertemplate = 'Month: %{x} <br>Max: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [20.2,29.3,17.0,19.0,29.3,26.7,22.4,22.6,29.3,26.3,33.2,27.7],
                                        mode='lines+markers', name = 'Mean',hovertemplate = 'Month: %{x} <br>Mean: %{y}')]
            smpllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=2))
            card_content = [
                    dbc.CardHeader("Raipur Division"),
                    dbc.CardBody(
                        [
                            html.P('Physical Properties', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dbc.Table.from_dataframe(phy_prop, striped=True, bordered=True, hover=True, style = {'font-size':'small'}),
                            html.P('Ground Water level', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dcc.Graph(figure = go.Figure(data = gwldatatraces, layout = smpllayout), style = {'width': '100%', 'height': '200px'}),
                            html.P('Ground Water Potential', style = {'font-weight': 'bold', 'font-size':'small', 'margin-top': '10px'}),
                            dbc.Table(gwp_show_table, bordered=True, style = {'font-size': 'small'})
                        ]
                    ),
                ]

            gridinfocard = dbc.Card(card_content, color="dark", outline=True)

        elif(oid_val == 2):

            phy_prop = pd.DataFrame({
                'Property': ['Elevation', 'Aspect', 'Curvature', 'Slope', 'Hillshade'],
                'Min': [555,-1,-4.04,0,124],
                'Max': [723,359.2,4.90,34.87,246],
                'Mean': [616.6,175.3,-0.0013,3.01,180.07]
            })

            gwp_show_table = html.Tbody(html.Tr([html.Td('Mean'), html.Td('6.85'), html.Td('High',style = {'background-color': '#55c18d'})]))

            gwldatatraces = [go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [10.1,9.1,5.9,12.2,
                                             9.1,13.5,8.8,10.1,
                                             9.1,11.5,12.5,9.5],
                                        mode='lines+markers', name = 'Min', fill = None, hovertemplate = 'Month: %{x} <br>Min: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [46.0,49.6,51.5,48.5,
                                             49.6,53.6,55.3,56.1,
                                             49.6,59.1,60.2,60.7],
                                        mode='lines+markers', name = 'Max', fill = 'tonexty',hovertemplate = 'Month: %{x} <br>Max: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [24.7,22.8,25.9,24.2,
                                             22.8,30.3,26.2,27.3,
                                             22.8,29.2,28.2,27.4],
                                        mode='lines+markers', name = 'Mean',hovertemplate = 'Month: %{x} <br>Mean: %{y}')]
            smpllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=2))
            card_content = [
                    dbc.CardHeader("Pithuwala Division"),
                    dbc.CardBody(
                        [
                            html.P('Physical Properties', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dbc.Table.from_dataframe(phy_prop, striped=True, bordered=True, hover=True, style = {'font-size':'small'}),
                            html.P('Ground Water level', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dcc.Graph(figure = go.Figure(data = gwldatatraces, layout = smpllayout), style = {'width': '100%', 'height': '200px'}),
                            html.P('Ground Water Potential', style = {'font-weight': 'bold', 'font-size':'small', 'margin-top': '10px'}),
                            dbc.Table(gwp_show_table, bordered=True, style = {'font-size': 'small'})
                        ]
                    ),
                ]

            gridinfocard = dbc.Card(card_content, color="dark", outline=True)

        elif(oid_val == 3):

            phy_prop = pd.DataFrame({
                'Property': ['Elevation', 'Aspect', 'Curvature', 'Slope', 'Hillshade'],
                'Min': [604,-1,-1.96,0,139],
                'Max': [744,358.5,2.45,14.83,217],
                'Mean': [661.4,195.2,-0.0002,2.68,179.11]
            })

            gwp_show_table = html.Tbody(html.Tr([html.Td('Mean'), html.Td('6.99'), html.Td('Very High',style = {'background-color': '#fcea49'})]))

            gwldatatraces = [go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [25.7,24.2,27.2,25.9,
                                             24.2,31.5,25.8,27.2,
                                             24.2,29,29.6,29],
                                        mode='lines+markers', name = 'Min', fill = None, hovertemplate = 'Month: %{x} <br>Min: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [50,68.2,46.1,48.4,
                                             68.2,58.5,48.5,51.2,
                                             68.2,53.1,74.7,68.6],
                                        mode='lines+markers', name = 'Max', fill = 'tonexty',hovertemplate = 'Month: %{x} <br>Max: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [34.4,42.9,34.6,34.4,
                                             42.9,41,36.8,38.7,
                                             42.9,40.7,48.2,45.6],
                                        mode='lines+markers', name = 'Mean',hovertemplate = 'Month: %{x} <br>Mean: %{y}')]
            smpllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=2))
            card_content = [
                    dbc.CardHeader("South Division"),
                    dbc.CardBody(
                        [
                            html.P('Physical Properties', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dbc.Table.from_dataframe(phy_prop, striped=True, bordered=True, hover=True, style = {'font-size':'small'}),
                            html.P('Ground Water level', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dcc.Graph(figure = go.Figure(data = gwldatatraces, layout = smpllayout), style = {'width': '100%', 'height': '200px'}),
                            html.P('Ground Water Potential', style = {'font-weight': 'bold', 'font-size':'small', 'margin-top': '10px'}),
                            dbc.Table(gwp_show_table, bordered=True, style = {'font-size': 'small'})
                        ]
                    ),
                ]

            gridinfocard = dbc.Card(card_content, color="dark", outline=True)

        elif(oid_val == 4):

            phy_prop = pd.DataFrame({
                'Property': ['Elevation', 'Aspect', 'Curvature', 'Slope', 'Hillshade'],
                'Min': [629,-1,-10.17,0,0],
                'Max': [1486,359,3.5,56.46,252],
                'Mean': [781.9,195.7,-0.0009,6.97,174.41]
            })

            gwp_show_table = html.Tbody(html.Tr([html.Td('Mean'), html.Td('6.797'), html.Td('High',style = {'background-color': '#55c18d'})]))

            gwldatatraces = [go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [25.6,27.1,15.6,24.9,
                                             27.1,28.5,21.5,26.9,
                                             27.1,27.6,30.2,23.6],
                                        mode='lines+markers', name = 'Min', fill = None, hovertemplate = 'Month: %{x} <br>Min: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [69.3,81.8,63,66.5,
                                             81.8,79.9,65.3,69.4,
                                             81.8,71.1,89.7,82.3],
                                        mode='lines+markers', name = 'Max', fill = 'tonexty',hovertemplate = 'Month: %{x} <br>Max: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [36.5,51.5,33.5,35.9,
                                             51.5,42.9,40.5,43.5,
                                             51.5,45.3,51.3,47.1],
                                        mode='lines+markers', name = 'Mean',hovertemplate = 'Month: %{x} <br>Mean: %{y}')]
            smpllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=2))
            card_content = [
                    dbc.CardHeader("North Division"),
                    dbc.CardBody(
                        [
                            html.P('Physical Properties', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dbc.Table.from_dataframe(phy_prop, striped=True, bordered=True, hover=True, style = {'font-size':'small'}),
                            html.P('Ground Water level', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dcc.Graph(figure = go.Figure(data = gwldatatraces, layout = smpllayout), style = {'width': '100%', 'height': '200px'}),
                            html.P('Ground Water Potential', style = {'font-weight': 'bold', 'font-size':'small', 'margin-top': '10px'}),
                            dbc.Table(gwp_show_table, bordered=True, style = {'font-size': 'small'})
                        ]
                    ),
                ]

            gridinfocard = dbc.Card(card_content, color="dark", outline=True)

        elif(oid_val == 5):

            phy_prop = pd.DataFrame({
                'Property': ['Elevation', 'Aspect', 'Curvature', 'Slope', 'Hillshade'],
                'Min': [555,-1,-4.29,0,126],
                'Max': [692,359.2,5.39,29.56,242],
                'Mean': [612.3,196.2,0.0001,3.28,180.92]
            })

            gwp_show_table = html.Tbody(html.Tr([html.Td('Mean'), html.Td('6.95'), html.Td('Very High',style = {'background-color': '#fcea49'})]))

            gwldatatraces = [go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [10.1,10.4,10.9,9.2,
                                             10.4,16.7,13.5,15.2,
                                             10.4,19.4,10.9,16.4],
                                        mode='lines+markers', name = 'Min', fill = None, hovertemplate = 'Month: %{x} <br>Min: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [43.8,46.9,50.7,48.8,
                                             46.9,48.8,51.6,49.7,
                                             46.9,57.3,56.5,54.3],
                                        mode='lines+markers', name = 'Max', fill = 'tonexty',hovertemplate = 'Month: %{x} <br>Max: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [25.85,25.7,27.6,23.8,
                                             25.7,31.2,30.8,31.2,
                                             25.7,33.5,31.6,29.8],
                                        mode='lines+markers', name = 'Mean',hovertemplate = 'Month: %{x} <br>Mean: %{y}')]
            smpllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=2))
            card_content = [
                    dbc.CardHeader("ADB"),
                    dbc.CardBody(
                        [
                            html.P('Physical Properties', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dbc.Table.from_dataframe(phy_prop, striped=True, bordered=True, hover=True, style = {'font-size':'small'}),
                            html.P('Ground Water level', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dcc.Graph(figure = go.Figure(data = gwldatatraces, layout = smpllayout), style = {'width': '100%', 'height': '200px'}),
                            html.P('Ground Water Potential', style = {'font-weight': 'bold', 'font-size':'small', 'margin-top': '10px'}),
                            dbc.Table(gwp_show_table, bordered=True, style = {'font-size': 'small'})
                        ]
                    ),
                ]

            gridinfocard = dbc.Card(card_content, color="dark", outline=True)

        elif(oid_val == 6):

            phy_prop = pd.DataFrame({
                'Property': ['Elevation', 'Aspect', 'Curvature', 'Slope', 'Hillshade'],
                'Min': [696,-1,-11.88,0,10],
                'Max': [1426,359.6,14.21,56.58,252],
                'Mean': [853.2,194.6,0.0010,9.01,172.75]
            })

            gwp_show_table = html.Tbody(html.Tr([html.Td('Mean'), html.Td('7.064'), html.Td('Very High',style = {'background-color': '#fcea49'})]))

            gwldatatraces = [go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [13.5,22.9,8.3,12.2,
                                             22.9,19.8,13.8,19.1,
                                             22.9,20.6,22.8,17.2],
                                        mode='lines+markers', name = 'Min', fill = None, hovertemplate = 'Month: %{x} <br>Min: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [69.5,85.5,63.1,66.6,
                                             85.5,80.1,65.4,69.6,
                                             85.5,71.2,67.3,61.5],
                                        mode='lines+markers', name = 'Max', fill = 'tonexty',hovertemplate = 'Month: %{x} <br>Max: %{y}'),
                            go.Scatter(x = ['JAN2011', 'MAY2011', 'AUG2011', 'NOV2011', 'JAN2015', 'MAY2015', 'AUG2015', 'NOV2015','JAN2019', 'MAY2019', 'AUG2019', 'NOV2019'],
                                        y = [35.9,61.6,31.0,34.4,
                                             61.6,43,45.5,49.2,
                                             61.6,50.8,49.8,45.0],
                                        mode='lines+markers', name = 'Mean',hovertemplate = 'Month: %{x} <br>Mean: %{y}')]
            smpllayout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=2))
            card_content = [
                    dbc.CardHeader("Maintenance Division"),
                    dbc.CardBody(
                        [
                            html.P('Physical Properties', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dbc.Table.from_dataframe(phy_prop, striped=True, bordered=True, hover=True, style = {'font-size':'small'}),
                            html.P('Ground Water level', style = {'font-weight': 'bold', 'font-size':'small'}),
                            dcc.Graph(figure = go.Figure(data = gwldatatraces, layout = smpllayout), style = {'width': '100%', 'height': '200px'}),
                            html.P('Ground Water Potential', style = {'font-weight': 'bold', 'font-size':'small', 'margin-top': '10px'}),
                            dbc.Table(gwp_show_table, bordered=True, style = {'font-size': 'small'})
                        ]
                    ),
                ]

            gridinfocard = dbc.Card(card_content, color="dark", outline=True)

        return html.Div([gridinfocard, ])

    if(but7):

        oid_val =  dataclicked['points'][0]['location']



        location_name = other_details_df.loc[other_details_df['OID_'] == oid_val]['Location'].values[0]

        card_content = [
                dbc.CardHeader("Grid Information (#{})".format(oid_val)),
                dbc.CardBody(
                    [
                        html.H4(location_name, className="card-title", style = {'font-weight': 'bold'}),


                        html.Table([
                            html.Tr([html.Td('Centroid Location'), html.Td('({},{})'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lat'].values[0],3),round(other_details_df.loc[other_details_df['OID_'] == oid_val]['centroid_lon'].values[0],3)))]),
                            html.Tr([html.Td('Zone'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['zone'].values[0]))]),
                            html.Tr([html.Td('Elevation'), html.Td('{} meters'.format(round(other_details_df.loc[other_details_df['OID_'] == oid_val]['elevation'].values[0],3)))]),
                            html.Tr([html.Td('LULC Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['names_LULC_Code'].values[0]))]),
                            html.Tr([html.Td('Lithology Class'), html.Td('{}'.format(other_details_df.loc[other_details_df['OID_'] == oid_val]['Litho'].values[0]))]),
                        ], style = {'font-size': 'small'})
                    ]
                ),
            ]

        gridinfocard = dbc.Card(card_content, color="dark", outline=True)



        return html.Div([gridinfocard])


## Multilayer Dashboard Layout

#==========================================================================================================================
## First Column

layer_switches = dbc.FormGroup(
    [
        dbc.Label("Zones", style = {'color': 'white', 'padding-bottom': '5px','padding-top': '5px', 'padding-left': '5px', 'font-weight': 'bold'}),
        dbc.Checklist(
            options=[
                {"label": "Zones", "value": 'zone-toggle'},
                {"label": "Pump Location", "value": 'pump-toggle'},

            ],
            value=['zone-toggle'],
            id="switches-input-zones",

            style = {'color': 'white', 'padding-bottom': '5px', 'padding-left': '15px'}
        ),
        dbc.Label('Physical Features', style = {'color': 'white', 'padding-bottom': '5px', 'padding-top': '5px','padding-left': '5px', 'font-weight': 'bold'}),
        dbc.Checklist(
            options=[
                {"label": "Elevation", "value": 'elevation-toggle'},
                {"label": "Aspect", "value": 'aspect-toggle'},
                {"label": "Curvature", "value": 'curvature-toggle'},
                {"label": "Slope", "value": 'slope-toggle'},
                {"label": "Hillshade", "value": 'hillshade-toggle'},


            ],
            value=[],
            id="switches-input-phyfeat",

            style = {'color': 'white', 'padding-bottom': '5px', 'padding-left': '15px'}
        ),

        dbc.Label('Evapotranspiration', style = {'color': 'white', 'padding-bottom': '5px', 'padding-top': '5px', 'padding-left': '5px', 'font-weight': 'bold'}),
        dbc.Checklist(
            options=[
                {"label": "2001", "value": 'et-2001-toggle'},
                {"label": "2005", "value": 'et-2005-toggle'},
                {"label": "2010", "value": 'et-2010-toggle'},
                {"label": "2015", "value": 'et-2015-toggle'},
                {"label": "2020", "value": 'et-2020-toggle'},


            ],
            value=[],
            id="switches-input-et",

            style = {'color': 'white', 'padding-bottom': '5px', 'padding-left': '15px'}
        ),

        dbc.Label('Surface Water', style = {'color': 'white', 'padding-bottom': '5px', 'padding-top': '5px', 'padding-left': '5px', 'font-weight': 'bold'}),
        dbc.Checklist(
            options=[
                {"label": "1990", "value": 'sw-1990-toggle'},
                {"label": "1994", "value": 'sw-1994-toggle'},
                {"label": "1999", "value": 'sw-1999-toggle'},
                {"label": "2004", "value": 'sw-2004-toggle'},
                {"label": "2009", "value": 'sw-2009-toggle'},
                {"label": "2014", "value": 'sw-2014-toggle'},
                {"label": "2019", "value": 'sw-2019-toggle'},

            ],
            value=[],
            id="switches-input-sw",

            style = {'color': 'white', 'padding-bottom': '5px', 'padding-left': '15px'}
        ),

        dbc.Label('Urbanisation', style = {'color': 'white', 'padding-bottom': '5px', 'padding-top': '5px', 'padding-left': '5px', 'font-weight': 'bold'}),
        dbc.Checklist(
            options=[
                {"label": "1995", "value": 'ur-1995-toggle'},
                {"label": "2000", "value": 'ur-2000-toggle'},
                {"label": "2005", "value": 'ur-2005-toggle'},
                {"label": "2010", "value": 'ur-2010-toggle'},
                {"label": "2015", "value": 'ur-2015-toggle'},

            ],
            value=[],
            id="switches-input-ur",

            style = {'color': 'white', 'padding-bottom': '5px', 'padding-left': '15px'}
        ),

        dbc.Label('Ground Water Potential', style = {'color': 'white', 'padding-bottom': '5px', 'padding-top': '5px', 'padding-left': '5px', 'font-weight': 'bold'}),
        dbc.Checklist(
            options=[
                {"label": "Ground Water Potential", "value": 'gwp-toggle'},

            ],
            value=[],
            id="switches-input-gwp",

            style = {'color': 'white', 'padding-bottom': '5px', 'padding-left': '15px'}
        ),

        dbc.Label('Land Use', style = {'color': 'white', 'padding-bottom': '5px', 'padding-top': '5px', 'padding-left': '5px', 'font-weight': 'bold'}),
        dbc.Checklist(
            options=[
                {"label": "Land Use", "value": 'lulc-toggle'},

            ],
            value=[],
            id="switches-input-lulc",

            style = {'color': 'white', 'padding-bottom': '5px', 'padding-left': '15px'}
        ),

        dbc.Label('Ground Water Level', style = {'color': 'white', 'padding-bottom': '5px', 'padding-top': '5px', 'padding-left': '5px', 'font-weight': 'bold'}),
        dbc.Checklist(
            options=[
                {"label": "January, 2011", "value": "jan11-toggle"},
                {"label": "May, 2011", "value": "may11-toggle"},
                {"label": "August, 2011", "value": "aug11-toggle"},
                {"label": "November, 2011", "value": "nov11-toggle"},
                {"label": "January, 2015", "value": "jan15-toggle"},
                {"label": "May, 2015", "value": "may15-toggle"},
                {"label": "August, 2015", "value": "aug15-toggle"},
                {"label": "November, 2015", "value": "nov15-toggle"},
                {"label": "January, 2019", "value": "jan19-toggle"},
                {"label": "May, 2019", "value": "may19-toggle"},
                {"label": "August, 2019", "value": "aug19-toggle"},
                {"label": "November, 2019", "value": "nov19-toggle"}

            ],
            value=[],
            id="switches-input-gwl",

            style = {'color': 'white', 'padding-bottom': '5px', 'padding-left': '15px'}
        ),

        dbc.Label('Basemap', style = {'color': 'white', 'padding-bottom': '5px', 'padding-top': '5px', 'padding-left': '5px', 'font-weight': 'bold'}),
        dbc.Select(
            options=[
                {"label": "No Basemap", "value": "white-bg"}, {"label": "Open Street Map", "value": "open-street-map"}, {"label": "Carto Positron", "value": "carto-positron"}, {"label": "Carto Darkmatter", "value": "carto-darkmatter"} ,{"label": "Stamen Terain", "value": "stamen-terrain"}, {"label": "Stamen Toner", "value": "stamen-toner"}, {"label": "Stamen Watercolor", "value": "stamen-watercolor"},

            ],
            value='open-street-map',
            id="switches-input-bmap",

            style = {'padding-bottom': '5px', 'padding-left': '15px'}
        ),

    ]
)




first_column_multi = dbc.Card(
    [
        dbc.CardHeader("Layers", style = {'color': 'white'}),
        dbc.CardBody(
            [

                   dbc.Button("< Back", id = 'button-item_back', color="success", href = '/dash', style = {'width': '90%', 'margin-left': '5%'}),
                   dbc.Tooltip("Back to Main Dashboard", target="button-item_back", placement='bottom'),
                   layer_switches


            ],
        style = {'padding': '5px',"border-radius": "0px",'align-content': 'center','height': '608px', 'overflow': 'auto'}),
        dbc.CardFooter("Powered by RBased Services Pvt. Ltd.", style = {'font-size': 'small', 'color': 'white'}),

    ],
    style={
          "border-radius": "0px"},
    color="secondary"
)

#==========================================================================================================================
## Second Column

second_column_multi = dbc.Card(
    [
        dbc.CardHeader("Multi Layer Map", style = {'color': 'white'}),
        dbc.CardBody(
            [

                html.Div([dcc.Loading(id = 'maparea_multi', type = 'dot'),
                    ], style = {'padding': '0px'})

            ],
        style = {'padding': '0px',"border-radius": "0px", 'background-color': 'white'}),

    ],
    style={"height": "700px",
          "border-radius": "0px","position":"relative"},
    color="info"
)

# ========================================================================================================================
## Third Column

third_column_multi = dbc.Card(
    [
        dbc.CardHeader("Legend", style = {'color': 'white'}),
        dbc.CardBody(
            [
                html.Div('Sample',id='legend_multi', style = {'overflow': 'auto','height': '100%'}),


            ],
        style = {'padding-top': '5px','padding-left': '5px', 'padding-bottom': '5px','padding-right': '0px',"border-radius": "0px", 'background-color': 'white', 'overflow': 'auto'}),

    ],
    style={"height": "700px",
          "border-radius": "0px",
          },
    color="secondary"
)

# -----------------------------------------------------------------------------------------------------------------
# Row containing all the above columns



rowmulti = dbc.Row(
    [
        dbc.Col(html.Div(first_column_multi, id = 'first-col-multi'), className = 'col-12 col-lg-2'),

        dbc.Col(html.Div(second_column_multi, style = {'height': '700px'}), className = 'col-12 col-lg-8'),
        dbc.Col(html.Div(third_column_multi, style = {'height': '700px'}), className = 'col-12 col-lg-2'),
    ],
    no_gutters=True,
    style = {'height': '600px'}
)

## Callbacks for Multilayer Mode

@app.callback(Output('maparea_multi', 'children'),
             [Input('switches-input-bmap', 'value'),
              Input('switches-input-phyfeat', 'value'),
              Input('switches-input-et', 'value'),
              Input('switches-input-sw', 'value'),
              Input('switches-input-ur', 'value'),
              Input('switches-input-gwp', 'value'),
              Input('switches-input-lulc', 'value'),
              Input('switches-input-gwl', 'value'),
              Input('switches-input-zones', 'value')])
def select_multi(bmap_multi, phyfeat_list, et_list, sw_list, ur_list, gwp_list, lulc_list, gwl_list, zo_list):

    traces = []


    for pfl in phyfeat_list:
        layer_name = pfl.split('-')[0]
        traces.append(go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df[layer_name], hovertext=lulc_df[layer_name],
                        colorscale="Viridis", marker_opacity=0.8, marker_line_width = 0,showlegend=False,
                        showscale=False, hovertemplate = layer_name.capitalize() +  ' : %{hovertext}', name = ''))

    for el in et_list:
        layer_name = el.split('-')[1]
        traces.append(go.Choroplethmapbox(geojson=json_file, locations=df.GRID_ID, z=df['ET_mean_{}'.format(layer_name)],
                                          hovertext=df['ET_mean_{}'.format(layer_name)],
                                          colorscale="Viridis", marker_opacity=0.8, marker_line_width = 0,showlegend=False,
                                          showscale=False, hovertemplate = 'Evapotranspiration: %{hovertext}',
                                          name = layer_name))



    for swl in sw_list:
        layer_name = swl.split('-')[1]
        if(layer_name == '1990'):
            color_val = '#A8D700'
        elif(layer_name == '1994'):
            color_val = '#2B8AEA'
        elif(layer_name == '1999'):
            color_val = '#7C4198'
        elif(layer_name == '2004'):
            color_val = '#A7AA91'
        elif(layer_name == '2009'):
            color_val = '#8B109E'
        elif(layer_name == '2014'):
            color_val = '#BF3D49'
        elif(layer_name == '2019'):
            color_val = '#9E1C56'

        traces_temp = [go.Scattermapbox(
                    lat=np.array(feature["geometry"]["coordinates"])[:, 1],
                    lon=np.array(feature["geometry"]["coordinates"])[:, 0],
                    mode="lines",
                    hoverinfo = 'none',
                    showlegend=False,
                    line=dict(width=8, color=color_val)
                )
                for feature in stream_json[layer_name]["features"]]
        for t in traces_temp:
            traces.append(t)

    if(len(gwp_list) > 0):
        traces.append(go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df['gwp_class'],
                                          hovertext=lulc_df['gw_pot'],
                                          colorscale="Viridis", marker_opacity=0.8, marker_line_width = 0,
                                          showlegend=False, showscale=False,
                                          hovertemplate = 'Ground Water Potential : %{hovertext}', name = 'GWP'))
    if(len(lulc_list)>0):

        traces.append(go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_, z=lulc_df['LULC_Code'], hovertext=lulc_df['names_LULC_Code'],
                                            colorscale="Viridis", marker_opacity=0.8, marker_line_width = 0,
                                          showlegend=False, showscale=False, hovertemplate = 'LULC : %{hovertext}', name = 'Class'))
    for gwll in gwl_list:
        layer_name = gwll.split('-')[0]
        traces.append(go.Choroplethmapbox(geojson=json_file, locations=ground_water_df.OID_, z=ground_water_df['GWL_{}'.format(layer_name)],
                                          hovertext=ground_water_df['GWL_{}'.format(layer_name)],
                                          colorscale="RdBu_r", marker_opacity=0.8, marker_line_width = 0,
                                          showlegend=False, showscale=False, hovertemplate = 'Ground Water Level (m): %{hovertext}',
                                          name = layer_name.upper()))

    for url in ur_list:
        layer_name = url.split('-')[1]
        traces.append(go.Choroplethmapbox(geojson=json_file, locations=lulc_df.OID_,
                                          z=lulc_df['urban_{}'.format(layer_name)],
                                          hovertext=lulc_df['urban_name_{}'.format(layer_name)],
                                          colorscale="RdBu_r", marker_opacity=0.8,
                                          marker_line_width = 0,showlegend=False, showscale=False,
                                          hovertemplate = 'Land Use Class : %{hovertext}',
                                          name = 'Urbanisation {}'.format(layer_name)))


    for zol in zo_list:
        if(zol == 'zone-toggle'):
            traces.append(go.Choroplethmapbox(geojson=zones_json, locations=zones_df.Id, z=zones_df.Id,
                            hovertext=zones_df.Name, hovertemplate = '%{hovertext}' ,
                            marker_opacity=0.8, marker_line_width = 2, showlegend=False, showscale=False, name = ''))


        elif(zol == 'pump-toggle'):
            traces.append(go.Scattermapbox(lat=pumps_df["Lat"].values, lon=pumps_df["Long"].values,
                                           mode='markers',marker=go.scattermapbox.Marker(size=14, color = '#FF0000'),
                                           text = pumps_df['Area'].values,
                                           hovertemplate = '%{text}', name = '',showlegend=False,
                                           ))


    if(len(traces)>0):

        fig = go.Figure(data = traces)

        fig.update_layout(mapbox_style=bmap_multi,
                          mapbox_zoom=10.35, mapbox_center = {"lat": 30.33 , "lon": 78.068})
        fig.update_layout(height = 650, margin={"r":0,"t":0,"l":0,"b":0})


        graphobjmap = dcc.Graph(id = 'map-plot-multi', figure = fig)

        return graphobjmap

    else:

        return dbc.Alert("No Layers are Selected!!!", color="danger", style = {'text-align': 'center', 'margin': '10px'})


#==============================================================================================================================
# Callbacks for Legend
#==============================================================================================================================

@app.callback(Output('legend_multi', 'children'),
             [Input('switches-input-bmap', 'value'),
              Input('switches-input-phyfeat', 'value'),
              Input('switches-input-et', 'value'),
              Input('switches-input-sw', 'value'),
              Input('switches-input-ur', 'value'),
              Input('switches-input-gwp', 'value'),
              Input('switches-input-lulc', 'value'),
              Input('switches-input-gwl', 'value'),
              Input('switches-input-zones', 'value')])
def select_multi(bmap_multi, phyfeat_list, et_list, sw_list, ur_list, gwp_list, lulc_list, gwl_list, zo_list):

    legend_cards = []


    for pfl in phyfeat_list:

        selected_val = pfl.split('-')[0]

        if(selected_val == 'elevation'):

            title_val = 'Elevation (m)'

        elif(selected_val == 'aspect'):

            title_val = 'Aspect'

        elif(selected_val == 'curvature'):

            title_val = 'Curvature'

        elif(selected_val == 'slope'):

            title_val = 'Slope'

        elif(selected_val == 'hillshade'):

            title_val = 'Hillshade'



        pf_toggle_table = [

        html.Img(src=app.get_asset_url('viridis.png'), style = {'margin-left': '8px', 'width': '80%', 'height': '20px','align-content': 'center'}),

        html.Table(html.Tr([html.Td('{}'.format(round(other_details_df[selected_val].min(),2))), html.Td('{}'.format(round(other_details_df[selected_val].max(),2)), style = {'text-align': 'right'})]), style = {'width': '90%'})]

        pf_toggle_content = [
                            dbc.CardHeader(title_val),
                            dbc.CardBody(

                                    pf_toggle_table

                            ),
                        ]

        legend_cards.append(dbc.Card(pf_toggle_content, color="dark", outline=True, style = {'margin-bottom': '5px'}))

    for el in et_list:
        selected_val = el.split('-')[1]



        et_toggle_table = [

        html.Img(src=app.get_asset_url('viridis.png'), style = {'margin-left': '8px', 'width': '80%', 'height': '20px','align-content': 'center'}),

        html.Table(html.Tr([html.Td('{}'.format(round(df['ET_mean_{}'.format(selected_val)].min(),2))), html.Td('{}'.format(round(df['ET_mean_{}'.format(selected_val)].max(),2)), style = {'text-align': 'right'})]), style = {'width': '90%'})
        ]

        et_toggle_content = [
                            dbc.CardHeader('Evapotranspiration ' + selected_val),
                            dbc.CardBody(

                                    et_toggle_table

                            ),
                        ]

        legend_cards.append(dbc.Card(et_toggle_content, color="dark", outline=True, style = {'margin-bottom': '5px'}))



    if(len(sw_list) > 0):

        zone_toggle_table = html.Table([html.Tr([html.Th('Color'), html.Th('Year')]),
                       html.Tr([html.Td(style = {'background-color': '#A8D700'}), html.Td('1990', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#2B8AEA'}), html.Td('1994', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#7C4198'}), html.Td('1999', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#A7AA91'}), html.Td('2004', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#8B109E'}), html.Td('2009', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#BF3D49'}), html.Td('2014', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#9E1C56'}), html.Td('2019', style = {'padding-left': '2px'})]),],style = {'width': '90%', 'font-size': 'small'})


        zone_toggle_content = [
                        dbc.CardHeader("Surface Water"),
                        dbc.CardBody(
                            [
                                zone_toggle_table
                            ]
                        ),
                    ]

        legend_cards.append(dbc.Card(zone_toggle_content, color="dark", outline=True, style = {'margin-bottom': '5px'}))

    if(len(gwp_list) > 0):
        zone_toggle_table = html.Table([html.Tr([html.Th('Color'), html.Th('Description')]),
                       html.Tr([html.Td(style = {'background-color': '#5c2269'}), html.Td('Low', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#5984a2'}), html.Td('Moderate', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#55c18d'}), html.Td('High', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#fcea49'}), html.Td('Very High', style = {'padding-left': '2px'})])],style = {'width': '90%', 'font-size': 'small'})


        zone_toggle_content = [
                        dbc.CardHeader("Ground Water Potential"),
                        dbc.CardBody(
                            [
                                zone_toggle_table
                            ]
                        ),
                    ]

        legend_cards.append(dbc.Card(zone_toggle_content, color="dark", outline=True, style = {'margin-bottom': '5px'}))
    if(len(lulc_list)>0):

        zone_toggle_table = html.Table([html.Tr([html.Th('Color'), html.Th('Description')]),
                           html.Tr([html.Td(style = {'background-color': '#5c2269'}), html.Td('Urban Area', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#5984a2'}), html.Td('Cropland', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#55c18d'}), html.Td('Barrenland', style = {'padding-left': '2px'})]),
                           html.Tr([html.Td(style = {'background-color': '#fcea49'}), html.Td('Forest', style = {'padding-left': '2px'})])],style = {'width': '90%', 'font-size': 'small'})


        zone_toggle_content = [
                        dbc.CardHeader("Land Use Land Cover"),
                        dbc.CardBody(
                            [
                                zone_toggle_table
                            ]
                        ),
                    ]

        legend_cards.append(dbc.Card(zone_toggle_content, color="dark", outline=True, style = {'margin-bottom': '5px'}))

    for gwll in gwl_list:
        selected_val = gwll.split('-')[0]



        et_toggle_table = [

        html.Img(src=app.get_asset_url('rdbu.png'), style = {'margin-left': '8px', 'transform':'rotate(180deg)',  'width': '80%', 'height': '20px','align-content': 'center'}),

        html.Table(html.Tr([html.Td('{}'.format(round(ground_water_df['GWL_{}'.format(selected_val)].min(),2))), html.Td('{}'.format(round(ground_water_df['GWL_{}'.format(selected_val)].max(),2)), style = {'text-align': 'right'})]), style = {'width': '90%'})
        ]

        et_toggle_content = [
                            dbc.CardHeader('Ground Water Level ' + selected_val.upper()),
                            dbc.CardBody(

                                    et_toggle_table

                            ),
                        ]

        legend_cards.append(dbc.Card(et_toggle_content, color="dark", outline=True, style = {'margin-bottom': '5px'}))

    if(len(ur_list)>0):


        zone_toggle_table = html.Table([html.Tr([html.Th('Color'), html.Th('Description')]),
                       html.Tr([html.Td(style = {'background-color': '#053061'}), html.Td('Urban Area', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#a7d0e4'}), html.Td('Cropland', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#f7b799'}), html.Td('Barrenland', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#67001f'}), html.Td('Forest', style = {'padding-left': '2px'})])],style = {'width': '90%', 'font-size': 'small'})


        zone_toggle_content = [
                        dbc.CardHeader("Urbanization"),
                        dbc.CardBody(
                            [
                                zone_toggle_table
                            ]
                        ),
                    ]

        legend_cards.append(dbc.Card(zone_toggle_content, color="dark", outline=True, style = {'margin-bottom': '5px'}))


    for zol in zo_list:
        if(zol == 'zone-toggle'):

            zone_toggle_table = html.Table([html.Tr([html.Th('Color'), html.Th('Description')]),
                       html.Tr([html.Td(style = {'background-color': '#0d0887'}), html.Td('Raipur Division', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#6901a6'}), html.Td('Pithuwala Division', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#b02a90'}), html.Td('South Division', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#e06561'}), html.Td('North Division', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#fba836'}), html.Td('ADB', style = {'padding-left': '2px'})]),
                       html.Tr([html.Td(style = {'background-color': '#f0f921'}), html.Td('Maintenance Division', style = {'padding-left': '2px'})]),],style = {'width': '90%', 'font-size': 'small'})


            zone_toggle_content = [
                            dbc.CardHeader("Zones"),
                            dbc.CardBody(
                                [
                                    zone_toggle_table
                                ]
                            ),
                        ]

            legend_cards.append(dbc.Card(zone_toggle_content, color="dark", outline=True, style = {'margin-bottom': '5px'}))







    return legend_cards



# ## Executing the Server


app.layout = html.Div([dcc.Location(id='url', refresh=False),
                       html.Div(id='page-content')],id='main-page')

@app.callback(Output('page-content', 'children'),
             [Input('url', 'pathname')])
def routandloadcontent(path):

    if(path == '/dash'):
        return [navbar,row]
    elif(path == '/dash-multilayer'):
        return [html.Div(navbar),
                rowmulti]
    elif(path == '/'):
        jumbotron = dbc.Jumbotron(
            [
                html.H1("CURE India USAID Dehradun Water Balance Portal", className="display-3"),
                html.P(
                    "Some information about the project",
                    className="lead",
                ),
                html.Hr(className="my-2"),

                html.P(dbc.Button("Go to Dashboard", color="success", className="mr-1", href = '/dash'), className="lead"),
            ]
        )

        return [navbar,jumbotron]
    else:
        jumbotron = dbc.Jumbotron(
            [
                html.H1("Page not found. Maybe a wrong path??", className="display-3"),
                html.P(
                    "Some information about the project",
                    className="lead",
                ),
                html.Hr(className="my-2"),

                html.P(dbc.Button("Go to Dashboard", color="success", className="mr-1", href = '/dash'), className="lead"),
            ]
        )

        return [navbar,jumbotron]


if(__name__ == '__main__'):
    app.run_server(host='0.0.0.0',port=80)


# Designed by Manaruchi Mohapatra (manaruchimohapatra@gmail.com)
