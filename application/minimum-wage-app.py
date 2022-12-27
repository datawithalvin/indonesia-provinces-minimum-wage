# -------- Import libraries ---------
from dash import Dash, dcc, Output, Input, html
import dash_bootstrap_components as dbc  
import plotly.express as px
import pandas as pd 
import pathlib

from urllib.request import urlopen
import json
import numpy as np


# -------------------------------------------------------------------------------------------------------------
# -------- Load dataset ---------
# -------------------------------------------------------------------------------------------------------------
# load geojson and dataset
with open("../datasets/geojson/indonesia.geojson") as f:
    provinces = json.load(f)
    

filepath = "../datasets/processed/UMP-Tingkat-Provinsi.csv"
main_df = pd.read_csv(filepath)

main_df = main_df.sort_values(by=["Provinsi", "Tahun"])
main_df['PrevUMP'] = main_df.groupby('Provinsi')['UpahMinimumProvinsi'].shift(1)
main_df['KenaikanUMP'] = main_df['UpahMinimumProvinsi'] - main_df['PrevUMP']
main_df["PersentaseKenaikan"] = (((main_df['UpahMinimumProvinsi'] - main_df['PrevUMP']) / main_df['PrevUMP']) * 100).round(2)
main_df.loc[main_df['KenaikanUMP'] < 0, 'KenaikanUMP'] = 0


def get_regional(prov):
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


main_df['Regional'] = main_df['Provinsi'].apply(get_regional)


# # filter on year to 2023
# df_2023 = main_df[main_df["Tahun"]==2023]
# df_2023.head()



# -------------------------------------------------------------------------------------------------------------
# -------- Build components ---------
# -------------------------------------------------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
# server = app.server


mytitle = dcc.Markdown("Dashboard Upah Minimum Provinsi Indonesia")
description = """
Lorem Ipsum adalah contoh teks atau dummy dalam industri percetakan dan penataan huruf atau typesetting.
Lorem Ipsum telah menjadi standar contoh teks sejak tahun 1500an, saat seorang tukang cetak yang tidak dikenal mengambil sebuah kumpulan teks dan mengacaknya untuk 
menjadi sebuah buku contoh huruf. Ia tidak hanya bertahan selama 5 abad, tapi juga telah beralih ke penataan huruf elektronik, tanpa ada perubahan apapun. 
Ia mulai dipopulerkan pada tahun 1960 dengan diluncurkannya lembaran-lembaran Letraset yang menggunakan kalimat-kalimat dari Lorem Ipsum, 
dan seiring munculnya perangkat lunak Desktop Publishing seperti Aldus PageMaker juga memiliki versi Lorem Ipsum.

"""


dropdown = dcc.Dropdown(options=main_df["Tahun"].unique(),
                        value=2023,  # initial value displayed when page first loads
                        clearable=False)

map_graph = dcc.Graph(figure={}, style={"width":"44rem", 'height': '50vh'})
line_graph1 = dcc.Graph(figure={}, style={"width":"44rem", 'height': '25vh'})
treemap_graph = dcc.Graph(figure={}, style={"width":"20rem", 'height': '50vh'})


# -------------------------------------------------------------------------------------------------------------
# -------- Customize layout ---------
# -------------------------------------------------------------------------------------------------------------
sidebar_card = dbc.Card([
    dbc.CardBody([
        html.H3(mytitle, style={"text-align":"justify", "font-family":"Futura"}),
        html.Hr(),
        html.P(description, style={"text-align":"justify", "font-family":"Futura"})
    ])
], style={"width":"25vh","height":"105vh", "background-color":"rgba(0, 0, 0, 0.5)"}, inverse=True)


second_card = dbc.Card([
    dbc.CardHeader([html.Label("Pilih Tahun:"), dropdown], style={"width":"10rem", "height":"10vh", "background-color":"rgba(0, 0, 0, 0)"}),
    dbc.CardBody([map_graph, line_graph1]),
], style={"width":"50vh", "height":"105vh", "background-color":"rgba(0, 0, 0, 0.5)"}, inverse=True)


third_card = dbc.Card([
    dbc.CardHeader([""], style={"width":"25vh", "height":"10vh", "background-color":"rgba(0, 0, 0, 0)"}),
    dbc.CardBody([treemap_graph]),
    # dbc.CardBody([
    #     html.H3(mytitle, style={"text-align":"justify", "font-family":"Futura"}),
    #     # html.Hr(),
    #     html.P(description, style={"text-align":"justify", "font-family":"Futura"})
    #     ])
], style={"width":"25vh","height":"105vh", "background-color":"rgba(0, 0, 0, 0.5)"}, inverse=True)


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(sidebar_card, width="auto"),
        dbc.Col(second_card, width="auto"),
        dbc.Col(third_card, width="auto")
    ], className="g-0")
    
], fluid=True)






# app.layout = dbc.Container([
#     dbc.Row([
#         dbc.Col([
#             html.H3(mytitle, style={"text-align":"justify", "font-family":"Futura"}),
#             html.Hr()], width=2, style={"height":"20vh"}),
#         dbc.Col([
#             html.P(description, style={"text-align":"justify", "font-family":"Futura"}),
#             html.Hr()], width=8, style={"height":"20vh"})
#     ])
# ])




# app.layout = dbc.Container([
#     dbc.Col([html.Div([
#         html.H3(mytitle, style={"text-align":"justify", "font-family":"Futura"}),
#         html.Hr(),
#         html.P(description, style={"text-align":"justify", "font-family":"Futura"})])
#         ], width={"size":2},
#         style={"height":"100vh", "margin-left":"5px"}),

#     dbc.Row()
# ])


# app.layout = dbc.Container([
#         dbc.Col([
#             html.H3(mytitle, style={"text-align":"left", "font-family":"Futura"}),
#             html.P(description, style={"text-align":"left", "font-family":"Futura"}),
#             ], width=3)
            
            
#             ])


# -------------------------------------------------------------------------------------------------------------
# -------- Callback ---------
# -------------------------------------------------------------------------------------------------------------
@app.callback(
        Output(map_graph, "figure"),
        Output(line_graph1, "figure"),
        Output(treemap_graph, "figure"),
#         Output(mygraph4, "map_figure"),
        Input(dropdown, "value")
)

def minimum_wage_map(selected_year):
        print(selected_year)
        print(type(selected_year))


        # -------------------------------------------------------------------------------------------------------------
        # -------- choropleth map ---------
        # -------------------------------------------------------------------------------------------------------------

        # filter dataframe
        dff = main_df.copy()
        dff = dff[dff["Tahun"]==selected_year]


        # build dataframe
        filtered_df = dff

        filtered_df["UMP"] = filtered_df["UpahMinimumProvinsi"]/1000000
        filtered_df["UMP"] = np.round(filtered_df["UMP"], 2)
        filtered_df["UMP"] = "Rp " + filtered_df['UMP'].astype(str) + " Juta"
        filtered_df.reset_index(drop=True, inplace=True)

        year = filtered_df["Tahun"][0]
        upah_min = np.min(filtered_df["UpahMinimumProvinsi"])
        upah_max= np.max(filtered_df["UpahMinimumProvinsi"])
        upah_med = np.median(filtered_df["UpahMinimumProvinsi"])

        round_min = np.round((upah_min/1000000), 2)
        round_max = np.round((upah_max/1000000), 2)
        round_med  = np.round((upah_med/1000000), 2)

        text_upah = [f"Rp {round_min} Juta", f"Rp {round_med} Juta", f"Rp {round_max} Juta"]


        # build figure
        map_fig = px.choropleth(
                filtered_df, geojson=provinces, color="UpahMinimumProvinsi",
                locations="Provinsi", featureidkey="properties.state", 
                color_continuous_scale=px.colors.sequential.Viridis_r, 
                hover_data={"Provinsi":True, "UpahMinimumProvinsi":':,'}
                )

        map_fig.update_geos(fitbounds="locations", visible=False )

        # map_fig.add_scattergeo(
        #         geojson=provinces, locations=filtered_df['Provinsi'], text=filtered_df['UMP'],
        #         featureidkey="properties.state", mode='text', textfont=dict(size=9, color="lightgrey", family="Arial")
        #         ) 


        map_fig.update_layout(autosize=False, margin={"r":0,"t":0,"l":0,"b":0}, width=700,height=400)
        map_fig.update_coloraxes(
                colorbar_tickmode="array", colorbar_tickvals=[upah_min, upah_med, upah_max],
                colorbar_ticktext=[text_upah[0], text_upah[1], text_upah[2]],
                colorbar_len=0.6, colorbar_thickness=10, colorbar_orientation="h", 
                colorbar_title=dict(text="", side="top"), colorbar_ticklabelposition="outside bottom",
                colorbar_y=0.05
                )
        map_fig.update_layout(
                title=f"Peta Upah Minimum Provinsi Tahun {year}",
                title_x=0.5, title_y=0.9, title_font_size=20, title_font_family="Futura"
                )
        map_fig.update_layout(template='plotly_dark')



        # -------------------------------------------------------------------------------------------------------------
        # -------- line graph median ---------
        # -------------------------------------------------------------------------------------------------------------

        # build dataframe
        median_df = main_df.copy()
        median_df = median_df.groupby('Tahun').aggregate({"KenaikanUMP":"median"}).reset_index()
        median_df = median_df.sort_values(by="Tahun") # sort by year
        

        # build figure
        line_fig = px.line(
                median_df, x='Tahun', y='KenaikanUMP', 
                title=f'Median Kenaikan Upah Minimum Provinsi Secara Nasional'
                )

        line_fig.update_traces(line=dict(color='steelblue')) # Set the line color to blue
        line_fig.update_layout(title_x=0.5, title_y=0.8) # Center the title
        line_fig.update_layout(yaxis=dict(tickformat=',.0f', tickprefix='Rp ', title='Kenaikan Upah')) # Format the y-axis tick labels
        line_fig.update_layout(autosize=False,width=700,height=300)
        line_fig.update_layout(template='plotly_dark') # Set the theme to dark


        # -------------------------------------------------------------------------------------------------------------
        # -------- tree map ---------
        # -------------------------------------------------------------------------------------------------------------

        # build dataframe
        filtered_df2 = dff
        filtered_df2 = filtered_df2[["Provinsi", "Tahun", "Regional", "KenaikanUMP"]]
        filtered_df2.reset_index(drop=True, inplace=True)

        year2 = filtered_df2["Tahun"][0]
        upah_min2 = np.min(filtered_df2["KenaikanUMP"])
        upah_max2= np.max(filtered_df2["KenaikanUMP"])
        upah_med2 = np.median(filtered_df2["KenaikanUMP"])

        round_min2 = np.int32((upah_min2/1000))
        round_max2 = np.int32((upah_max2/1000))
        round_med2  = np.int32((upah_med2/1000))

        text_upah2 = [f"Rp {round_min2} Ribu", f"Rp {round_med2} Ribu", f"Rp {round_max2} Ribu"]


        # build figure
        treemap_fig = px.treemap(filtered_df2, path=[px.Constant("Indonesia"), "Regional", "Provinsi"], values="KenaikanUMP",
                        color="KenaikanUMP", hover_data=["Provinsi"],
                        color_continuous_scale='Viridis_r')

        treemap_fig.update_layout(
                title=f"Besar Kenaikan Upah Minimum Provinsi Tahun {year2}",
                title_x=0.5, title_font_size=20
                )

        treemap_fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        treemap_fig.update_layout(autosize=False,width=400,height=400)
        # fig.update_layout(font_family="Balto")

        treemap_fig.update_coloraxes(
                colorbar_tickmode="array", colorbar_tickvals=[upah_min2, upah_med2, upah_max2],
                colorbar_ticktext=[text_upah2[0], text_upah2[1], text_upah2[2]],
                colorbar_len=0.7, colorbar_thickness=20, colorbar_x=1,
                colorbar_title=dict(text="", side="top")
                )

        treemap_fig.update_layout(template='plotly_dark')

        # -------------------------------------------------------------------------------------------------------------
        # -------- line graph province ---------
        # -------------------------------------------------------------------------------------------------------------

        # build dataframe

        


        return map_fig, line_fig, treemap_fig




# def my_density_map(selected_year):
#         print(selected_year)
#         print(type(selected_year))


#         # -------- density map ---------
#         # filter dataframe
#         dff = main_df.copy()
#         dff = dff[dff["year"]==selected_year]

#         # build density map graph
#         map_map_fig = px.density_mapbox(dff, lat="latitude", lon="longitude", z="frp",
#                        radius=1.5, hover_name="province",hover_data={'acq_date':True, "latitude":False, "longitude":False, "acq_time":True, "confidence":False, 
#                        'frp':True, "daynight":False, "type":False, "brightness":False, "province":False, "year":False, "month":False,},
#                        center=dict(lat=-2.5, lon=118), zoom=3.7, color_continuous_scale="matter_r",
#                        mapbox_style="carto-darkmatter", template="plotly_dark")

#         # map_map_fig.update_layout(autosize=False,width=950,height=400)
#         map_map_fig.update_layout(autosize=True)
#         map_map_fig.update_geos(lataxis_showgrid=True, lonaxis_showgrid=True)
#         map_map_fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1})
#         map_map_fig.update_coloraxes(showscale=True, colorbar=dict(len=0.75, title="Fire<br>Radiative<br>Power", thickness=15, x=0.99))
#         map_map_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
#         # map_map_fig.update_layout(title=r"Sebaran Titik Api yang Terobservasi oleh VIIRS",title_font_size=14)


#         # -------- sorted bar chart ---------
#         # groupby province
#         grouped = dff.groupby(["province"])["frp"].count()
#         grouped = pd.DataFrame(grouped)
#         grouped = grouped.reset_index()
#         grouped = grouped.sort_values(by="frp", ascending=False)
#         grouped = grouped.head(10)

#         # build bar chart graph
#         bar_map_fig = px.bar(grouped, x="frp", y="province", orientation="h", 
#                         labels={"province":"", "frp":"Fire Count"}, template="plotly_dark")
#         bar_map_fig.update_layout(yaxis={'categoryorder':'total ascending'})

#         # bar_map_fig.update_layout(autosize=False,width=450,height=375)
#         bar_map_fig.update_layout(title="Top 10 Provinces (January to December)",title_font_size=14)
#         # bar_map_fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1})
#         # bar_map_fig.update_yaxes(tickfont_size=8)
#         bar_map_fig.update_traces(marker_color='indianred')
#         bar_map_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
#         bar_map_fig.update_xaxes(title_font=dict(size=12))
#         bar_map_fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)


#         # -------- sorted bar chart ---------
#         # groupby day
#         line_df = dff.copy()

#         line_df = line_df.groupby(["acq_date"])["year"].agg("count")
#         line_df = pd.DataFrame(line_df)
#         line_df = line_df.rename(columns={"year":"active_fires"})

#         # build line chart graph
#         line_map_fig = px.line(line_df, x=line_df.index.values, y="active_fires",
#                 labels={"active_fires":"<b>Daily Fire Detection</b>", "x":""},template="plotly_dark")

#         # line_map_fig.update_layout(autosize=False,width=950,height=250)
#         line_map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#         line_map_fig.update_traces(line_color='indianred')
#         line_map_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
#         line_map_fig.update_yaxes(title_font=dict(size=12))
#         line_map_fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)


#         # -------- pie chart ---------
#         # groupby confidence
#         percentage_df = dff.groupby(["confidence"])["frp"].agg("count")
#         percentage_df = percentage_df.reset_index()
#         percentage_df = percentage_df.rename(columns={"frp":"counts"})
#         percentage_df["confidence"] = percentage_df["confidence"].replace({"n":"Nominal", "l":"Low", "h":"High"})
#         percentage_df["percent"] = (percentage_df["counts"] / percentage_df["counts"].sum()) * 100

#         # build pie chart graph
#         pie_map_fig = px.pie(percentage_df, values='percent', names='confidence', color_discrete_sequence=px.colors.sequential.YlOrRd_r,
#                template="plotly_dark")

#         pie_map_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
#         # pie_map_fig.update_layout(autosize=False,width=450,height=300)
#         pie_map_fig.update_layout(title="Fire Confidence Level",title_font_size=14)


#         return map_map_fig, bar_map_fig, line_map_fig, pie_map_fig



# -------------------------------------------------------------------------------------------------------------
# -------- Run app ---------
## -------------------------------------------------------------------------------------------------------------
if __name__=='__main__':
    app.run_server(debug=True)