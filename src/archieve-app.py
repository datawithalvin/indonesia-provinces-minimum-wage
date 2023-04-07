# ************************************************************************************************************************************************************************************
# -------- Import libraries ---------
# ************************************************************************************************************************************************************************************

from dash import Dash, dcc, Output, Input, html
import dash_bootstrap_components as dbc  
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd 
import pathlib

from urllib.request import urlopen
import json
import numpy as np



# ************************************************************************************************************************************************************************************
# -------- Load dataset, data preparation ---------
# ************************************************************************************************************************************************************************************

## load geojson file
with open("data/geojson/indonesia.geojson") as f:
    provinces = json.load(f)
    
## load dataset
filepath = "data/processed/UMP-Tingkat-Provinsi.csv"
main_df = pd.read_csv(filepath)

## do some data preparation and add some column that needed for the viz
main_df = main_df.sort_values(by=["Provinsi", "Tahun"])
main_df['PrevUMP'] = main_df.groupby('Provinsi')['UpahMinimumProvinsi'].shift(1)
main_df['KenaikanUMP'] = main_df['UpahMinimumProvinsi'] - main_df['PrevUMP']
main_df["PersentaseKenaikan"] = (((main_df['UpahMinimumProvinsi'] - main_df['PrevUMP']) / main_df['PrevUMP']) * 100).round(2)
main_df.loc[main_df['KenaikanUMP'] < 0, 'KenaikanUMP'] = 0


def get_regional(prov):
        """
        this function will return a regional or island origin of the province in a dataset. 
        """
        regional = []

        sumatera = ['Sumatera Utara', 'Sumatera Barat', 'Riau', 'Jambi', 'Sumatera Selatan','Bengkulu', 'Lampung', 'Aceh', 'Bangka-Belitung', 'Kepulauan Riau']
        jawa = ['Jakarta Raya', 'Jawa Barat', 'Jawa Tengah', 'Yogyakarta', 'Jawa Timur', 'Banten',]
        sulawesi = ['Sulawesi Barat', 'Gorontalo', 'Sulawesi Tenggara', 'Sulawesi Selatan', 'Sulawesi Tengah', 'Sulawesi Utara']
        kalimantan = ['Kalimantan Utara', 'Kalimantan Timur', 'Kalimantan Selatan', 'Kalimantan Tengah', 'Kalimantan Barat']
        papua = ['Papua', 'Papua Barat']
        maluku = ['Maluku Utara', 'Maluku']
        nusatenggara = ['Nusa Tenggara Timur', 'Nusa Tenggara Barat', "Bali"]

        if prov in sumatera:
                regional.append("Pulau Sumatera")
        elif prov in jawa:
                regional.append("Pulau Jawa")
        elif prov in sulawesi:
                regional.append("Pulau Sulawesi")
        elif prov in kalimantan:
                regional.append("Pulau Kalimantan")
        elif prov in papua:
                regional.append("Pulau Papua")
        elif prov in maluku:
                regional.append("Kepulauan Maluku")
        elif prov in nusatenggara:
                regional.append("Kepulauan Nusa Tenggara")       
        else:
                regional.append("Regional Provinsi Tidak Terdaftar")

        return regional[0]

## add a new column by call the function
main_df['Regional'] = main_df['Provinsi'].apply(get_regional)

## list of minimum wage years from 2015
## desc sort
list_tahun = main_df[main_df["Tahun"]>=2015]
list_tahun = list_tahun.sort_values(by="Tahun", ascending=False)
list_tahun = list_tahun["Tahun"].unique()

# ************************************************************************************************************************************************************************************
# -------- Build web components ---------
# ************************************************************************************************************************************************************************************

## set the themes to dark
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

## dashboard title and description
mytitle = dcc.Markdown("Dashboard Upah Minimum Provinsi Indonesia")
description = dcc.Markdown("""
Upah Minimum Provinsi (UMP) adalah gaji bulanan minimum yang wajib dibayarkan oleh pemberi kerja ke tenaga kerja.
UMP ditetapkan oleh pemerintah provinsi setempat dengan mempertibangkan tingkat biaya hidup, produktivitas, 
dan kondisi ekonomi dari suatu provinsi dan berlaku hanya untuk pekerja yang bekerja di wilayah administrasi provinsi tersebut.
Dashboard ini berisi informasi tentang UMP semua provinsi yang ada di Indonesia dan dapat digunakan sebagai referensi 
untuk memastikan bahwa kamu mendapatkan gaji yang layak. Silahkan kunjungi 
[tautan berikut ini](https://bplawyers.co.id/2021/04/09/upah-masih-di-bawah-standar-minimum-berikut-ini-langkah-hukum-yang-bisa-ditempuh/)
jika kamu menerima gaji yang lebih rendah dari UMP yang telah ditetapkan untuk mencari tahu apa langkah yang harus dilakukan.
""")


## graphs and other components
dropdown = dcc.Dropdown(options=list_tahun,
                        value=2023,  # initial value displayed when page first loads
                        clearable=False, 
                        style={"width":"40%", "height":"5%", "text-align":"left", 
                                "font-family":"Futura", "font-size":"12px"})

map_graph = dcc.Graph(figure={}, className='row')
line_graph = dcc.Graph(figure={}, className='row')
treemap_graph = dcc.Graph(figure={})



# ************************************************************************************************************************************************************************************
# -------- Build cards and layout ---------
# ************************************************************************************************************************************************************************************

## card for title and description, will be placed at the first column as a sidebar
## the title will be at the first row with 25% height, and the description will be at the second row with 75% height
## the width of the column will have size of 2
sidebar_card = dbc.Card([
        dbc.CardBody([
                html.H3(mytitle, style={"width":"100%", "height":"40%",  "text-align":"justify", "font-family":"Futura", "font-size":"24px", "font-weight":"bold"}),
                html.Hr(),
                html.P(description,
                        style={"width":"100%", "height":"60%",  "text-align":"justify", "font-family":"Futura", "font-size":"14px"}),
                dbc.Button(
                        "Source Code", href="https://github.com/datawithalvin/indonesia-provinces-minimum-wage",
                         color="primary", size="sm", external_link=True
                         )
        ])
], style={"background-color":"rgba(17, 17, 17, 1)", "border":"10px rgba(37, 37, 38, 175)", "margin-right": "0px"}, className="g-0",
        inverse=True,)

## card for choropleth map and line chart yearly median of national minimum wage, will be placed at the second column as main focus
## above the map, there will be a dropdown will a label that have each 10% height, the map will have 60% height, and 30% height for the line chart
## the width of the column will have size of 6

main_card = dbc.Card([
        dbc.CardBody([
                dbc.CardHeader([
                        html.Label("Pilih Tahun: ", style={"width":"30%", "height":"3%", "text-align":"left",
                                        "font-family":"Futura", "font-size":"14px", "background-color":"rgba(17, 17, 17, 1)"}),
                        dropdown
                ], style={"background-color":"rgba(17, 17, 17, 1)", "border":"0px rgba(17, 17, 17, 1)"}),
                map_graph,
                line_graph
        ])
], style={"background-color":"rgba(17, 17, 17, 1)", "border":"0px rgba(17, 17, 17, 1)"})



## card for treemap and another line chart that will dispplay minimum wage of selected province, will be placed at the third column as a support viz
## the treemap will be at the first row with 60% height and then second row will be the line chart with 30% height that have dropdown and a label with 10% height each
## the width of the column will have size of 4

rightside_card = dbc.Card([
        dbc.CardBody(treemap_graph, style={"width":"100%", "height":"90%", "font-family":"Futura"})
], style={"background-color":"rgba(17, 17, 17, 1)", "border":"0px rgba(17, 17, 17, 1)"})


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(sidebar_card, style={"height": "100vh"}, xs=10, sm=10, md=2, lg=2, xl=2),
        dbc.Col(main_card, style={"height": "100%"}, xs=10, sm=10, md=7, lg=7, xl=7),
        dbc.Col(rightside_card, style={"height": "100%"}, xs=10, sm=10, md=3, lg=3, xl=3)
    ], className=["h-100", "g-0"])
    
], fluid=True, style={"background-color":"rgba(17, 17, 17, 1)"})



# ************************************************************************************************************************************************************************************
# -------- Build Callback ---------
# ************************************************************************************************************************************************************************************

@app.callback(
        Output(map_graph, "figure"),
        Output(line_graph, "figure"),
        Output(treemap_graph, "figure"),
        Input(dropdown, "value"),
        Input(map_graph, "hoverData")
)

def minimum_wage_map(selected_year, hover_data):
        print(selected_year)
        print(type(selected_year))


        # print(json.dumps(hover_data, indent=2))

        # slctd_province = hover_data["points"][0]["text"]


        # ************************************************************************************************************************************************************************************
        # -------- choropleth map ---------
        # ************************************************************************************************************************************************************************************


        ## build dataframe
        ## filter dataframe by selected year
        dff = main_df.copy()
        dff = dff[dff["Tahun"]==selected_year]

        dff["UMP"] = dff["UpahMinimumProvinsi"]/1000000
        dff["UMP"] = np.round(dff["UMP"], 2)
        dff["UMP"] = "Rp " + dff['UMP'].astype(str) + " Juta"
        dff.reset_index(drop=True, inplace=True)

        year = dff["Tahun"][0]
        upah_min = np.min(dff["UpahMinimumProvinsi"])
        upah_max= np.max(dff["UpahMinimumProvinsi"])
        upah_med = np.median(dff["UpahMinimumProvinsi"])

        round_min = np.round((upah_min/1000000), 2)
        round_max = np.round((upah_max/1000000), 2)
        round_med  = np.round((upah_med/1000000), 2)

        text_upah = [f"Rp {round_min} Juta", f"Rp {round_med} Juta", f"Rp {round_max} Juta"]


        ## build figure
        map_fig = px.choropleth(
                dff, geojson=provinces, color="UpahMinimumProvinsi",
                locations="Provinsi", featureidkey="properties.state", 
                color_continuous_scale=px.colors.sequential.Viridis_r,
                hover_data={"Provinsi":True, "UpahMinimumProvinsi":':,'}
                )

        map_fig.update_geos(fitbounds="locations", visible=False )

        map_fig.update_layout(autosize=False, margin={"r":0,"t":0,"l":0,"b":0, "pad":0}, width=900,height=380)
        map_fig.update_coloraxes(
                colorbar_tickmode="array", colorbar_tickvals=[upah_min, upah_med, upah_max],
                colorbar_ticktext=[text_upah[0], text_upah[1], text_upah[2]],
                colorbar_len=0.4, colorbar_thickness=10, colorbar_orientation="h", 
                colorbar_title=dict(text="", side="top"), colorbar_ticklabelposition="outside bottom", colorbar_tickfont_size=12,
                colorbar_y=0
                )
        map_fig.update_layout(
                title=f"<b>Peta Upah Minimum Provinsi Tahun {year}</b>",
                title_x=0.5, title_y=0.95, title_font_size=18
                )
        map_fig.update_layout(template='plotly_dark')
        map_fig.update_layout(font=dict(family='Futura'))




        # ************************************************************************************************************************************************************************************
        # -------- line charts ---------
        # ************************************************************************************************************************************************************************************

        ## build dataframe for first line chart
        ## create a function that will get a data from hovered location on the map
        ## use the hovered location name as a filter for the dataframe
        ## the figure will display a line chart that have timeries data for selected province
        dff1 = main_df.copy()

        def get_province_name():
                if hover_data is not None:
                        province_name = hover_data["points"][0]["location"]
                        return province_name
                else:
                        province_name = "Jakarta Raya"
                        return province_name

        province_name = get_province_name()
        dff1 = dff1[dff1["Provinsi"]==province_name]
        dff1["Provinsi"] = dff1["Provinsi"].replace({"Jakarta Raya":"DKI Jakarta"})
        dff1 = dff1.sort_values(by="Tahun")
        dff1.reset_index(drop=True, inplace=True)

        ## add new columns
        ## replace all negative values
        dff1["KenaikanUpah"] = dff1["UpahMinimumProvinsi"] - dff1["UpahMinimumProvinsi"].shift(1)
        dff1["KenaikanPersen"] = (((dff1["UpahMinimumProvinsi"] - dff1["UpahMinimumProvinsi"].shift(1)) / dff1["UpahMinimumProvinsi"].shift(1)) * 100).round(2)

        dff1.loc[dff1['KenaikanUpah'] < 0, 'KenaikanUpah'] = 0
        dff1.loc[dff1['KenaikanPersen'] < 0, 'KenaikanPersen'] = 0

        prov_name = dff1["Provinsi"][0]


        ## build dataframe for first second chart
        median_df = main_df.copy()
        median_df = median_df.groupby('Tahun').aggregate({"KenaikanUMP":"mean"}).reset_index()
        median_df = median_df.sort_values(by="Tahun") # sort by year



        ## build figure
        line_fig = make_subplots(
                rows=1, cols=2, 
                subplot_titles=(f'<b>Jumlah Kenaikan UMP Tahunan Provinsi {prov_name}</b>', 
                                "<b>Rerata Jumlah Kenaikan UMP Nasional Tahun 2001 - 2023</b>")
        )

        line_fig.add_trace(
                go.Scatter(x=dff1["Tahun"], y=dff1["KenaikanUpah"], name="Kenaikan Upah"),
                row=1, col=1, 
                
        )

        line_fig.add_trace(
                go.Scatter(x=median_df["Tahun"], y=median_df["KenaikanUMP"], name="Kenaikan Upah"),
                row=1, col=2
        )

        line_fig.update_layout(template='plotly_dark')
        line_fig.update_layout(autosize=False,width=1100,height=300, showlegend=False)
        line_fig.update_layout(font=dict(family='Futura'))
        line_fig.update_annotations(font_size=16, y=1.15)
        line_fig.update_traces(line=dict(color='steelblue'))
        line_fig.update_layout(yaxis=dict(tickformat=',.0f', tickprefix='Rp ', title='', showgrid=False), 
                                yaxis2=dict(tickformat=',.0f', tickprefix='Rp ', title='', showgrid=False))
        line_fig.update_layout(yaxis2=dict(range=[median_df["KenaikanUMP"].min(), median_df["KenaikanUMP"].max()]))
        line_fig.update_layout(xaxis=dict(title='Tahun', showgrid=False), xaxis2=dict(title='Tahun', showgrid=False))
        line_fig.update_layout(hovermode="x unified")


        # ************************************************************************************************************************************************************************************
        # -------- treemap ---------
        # ************************************************************************************************************************************************************************************

        # build dataframe
        # filter dataframe by selected year
        dff2 = main_df.copy()
        dff2 = dff2[dff2["Tahun"]==2023]
        dff2 = dff2[["Provinsi", "Tahun", "Regional", "KenaikanUMP"]]
        dff2["Provinsi"] = dff2["Provinsi"].replace({"Jakarta Raya":"DKI Jakarta"})
        dff2.reset_index(drop=True, inplace=True)

        upah_min2 = np.min(dff2["KenaikanUMP"])
        upah_max2= np.max(dff2["KenaikanUMP"])
        upah_med2 = np.median(dff2["KenaikanUMP"])

        round_min2 = np.int32((upah_min2/1000))
        round_max2 = np.int32((upah_max2/1000))
        round_med2  = np.int32((upah_med2/1000))

        text_upah2 = [f"Rp {round_min2} Ribu", f"Rp {round_med2} Ribu", f"Rp {round_max2} Ribu"]
        year2 = dff2["Tahun"][0]


        ## build figure
        treemap_fig = px.treemap(
                dff2, path=[px.Constant("Indonesia"), "Regional", "Provinsi"], values="KenaikanUMP",
                color="KenaikanUMP",color_continuous_scale='Viridis_r', hover_name="Provinsi",
                hover_data=["KenaikanUMP"]
                )

        ## update figure layout
        treemap_fig.update_layout(
                title="<b>Jumlah Kenaikan UMP Tahun 2023<b>",
                title_x=0.45, title_font_size=16, title_y=0.97, 
                )
        treemap_fig.update_layout(margin = dict(t=50, l=0, r=25, b=15))
        treemap_fig.update_layout(autosize=False,width=350,height=500)
        treemap_fig.update_layout(template='plotly_dark')
        treemap_fig.update_coloraxes(
                colorbar_tickmode="array", colorbar_tickvals=[upah_min2, upah_med2, upah_max2],
                colorbar_ticktext=[text_upah2[0], text_upah2[1], text_upah2[2]], colorbar_tickfont_size=12,
                colorbar_len=0.8, colorbar_thickness=10, colorbar_orientation="h", colorbar_title=dict(text="", side="top"), 
                colorbar_ticklabelposition="outside bottom", colorbar_y=-0.12, colorbar_x=0.5,
                )
        treemap_fig.update_layout(font=dict(family='Futura'))

        return map_fig, line_fig, treemap_fig



# ************************************************************************************************************************************************************************************
# -------- Run app ---------
# ************************************************************************************************************************************************************************************
if __name__=='__main__':
    app.run_server(debug=True)