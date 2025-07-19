import numpy as np
import pandas as pd
import folium
import json
import re
import geopandas as gpd
import plotly.express as px

geo_path = 'HangJeongDong_ver20250401.geojson'
data_path = './제21대_대통령선거_개표결과.xlsx'

df = pd.read_excel(data_path)
df.fillna(method = 'ffill', axis=0, inplace=True)
df.columns = df.loc[4, :]
df = df.loc[5:, :]
for col in df.columns:
    try:
        df[col] = df[col].astype(str).str.replace(',', '') 
        df[col] = pd.to_numeric(df[col], errors='raise') 
    except:
        continue

df = df.reset_index()
df['읍면동명'] = df['읍면동명'].str.replace(r'제(?=\d)', '', regex=True)
df['구시군명'] = df['구시군명'].str.replace(r'시갑', '시', regex=True)
df['구시군명'] = df['구시군명'].str.replace(r'시을', '시', regex=True)
df['구시군명'] = df['구시군명'].str.replace('세종특별자치시', '세종시')
df.loc[3559, '읍면동명'] = '가야제1동'
df.loc[3105, '읍면동명'] = '상일제1동'
df.loc[3115, '읍면동명'] = '상일제2동'

df['투표구'] = df['시도명'] + ' ' + df['구시군명'] + ' ' + df['읍면동명'] + ' ' + df['투표구명']
df['읍면동'] = df['시도명'] + ' ' + df['구시군명'] + ' ' + df['읍면동명']

df.loc[5340, '읍면동'] = '대구광역시 달서구 두류1,2동'

df.drop(columns = 'index', inplace=True)

df.columns = ['시도명', '구시군명', '읍면동명', '투표구명', '선거인수', '투표수', '더불어민주당 이재명',
       '국민의힘 김문수', '개혁신당 이준석', '민주노동당 권영국', '무소속 송진호', '계', '무효 투표수',
       '기권수', '투표구', '읍면동']


df2['rates_jm'] = df2['더불어민주당 이재명']/df2['투표수']
df2['rates_ms'] = df2['국민의힘 김문수']/df2['투표수']
df2['rates_js'] = df2['개혁신당 이준석']/df2['투표수']
df2['rates_uk'] = df2['민주노동당 권영국']/df2['투표수']

with open('HangJeongDong_ver20250401.geojson', encoding='utf-8') as f:
    geo_data = json.load(f)

for i in range(len(geo_data['features'])):
    if geo_data['features'][i]['properties']['adm_nm'] not in list(df2['읍면동']):
        print(geo_data['features'][i]['properties']['adm_nm'], ':', len(df2[df2['읍면동'] == geo_data['features'][i]['properties']['adm_nm']]))

geo_lists = []

for i in range(len(geo_data['features'])):
    geo_lists.append(geo_data['features'][i]['properties']['adm_nm'])


for i in range(len(geo_data['features'])):
    name = geo_data['features'][i]['properties']['adm_nm']

    if len(df2[df2['읍면동'].str.contains(name)]) != 1:
        print(f"{name}: {len(df2[df2['읍면동'].str.contains(name)])}")


m = folium.Map(location = [36.5, 127.8], zoom_start = 7)
folium.Choropleth(
    geo_data=geo_data,
    data=df2,
    columns=['읍면동', 'rates_jm'],
    key_on='feature.properties.adm_nm', 
    fill_color='Blues',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='이재명 득표율'
).add_to(m)
m

j = folium.Map(location = [36.5, 127.8], zoom_start = 7)

folium.Choropleth(
    geo_data=geo_data,
    data=df2,
    columns=['읍면동', 'rates_js'],
    key_on='feature.properties.adm_nm',  # GeoJSON 내 시군구 이름 key 확인 필요
    fill_color='Oranges',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='이준석 득표율'
).add_to(j)

j

ms = folium.Map(location = [36.5, 127.8], zoom_start = 7)

folium.Choropleth(
    geo_data=geo_data,
    data=df2,
    columns=['읍면동', 'rates_ms'],
    key_on='feature.properties.adm_nm', 
    fill_color='Reds',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='김문수 득표율'
).add_to(ms)

ms

uk = folium.Map(location = [36.5, 127.8], zoom_start = 7)

folium.Choropleth(
    geo_data=geo_data,
    data=df2,
    columns=['읍면동', 'rates_ms'],
    key_on='feature.properties.adm_nm', 
    fill_color='YlOrBr',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='권영국 득표율'
).add_to(uk)

uk

import geopandas as gpd
import plotly.express as px



gdf = gpd.read_file(geo_path)

merged = gdf.merge(df2, left_on = 'adm_nm', right_on = '읍면동')


fig = px.choropleth_mapbox(
    merged,
    geojson=merged.geometry.__geo_interface__, 
    locations=merged.index,
    color='rates_jm', 
    hover_name='읍면동',
    hover_data={
        'rates_jm': ':.2f',
        'rates_ms': ':.2f',
        'rates_js': ':.2f',
        'rates_uk': ':.2f'
    },
    center={"lat": 36.5, "lon": 127.8},
    mapbox_style="open-street-map",
    zoom=5.5,
    opacity=0.6
)

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()


import plotly.graph_objects as go


geojson = merged.geometry.__geo_interface__
location_ids = merged.index

candidates = {
    '이재명': ('rates_jm', ['white', '#1f77b4']),
    '김문수': ('rates_ms', ['white', '#d62728']),
    '이준석': ('rates_js', ['white', '#ff7f0e']),
    '권영국': ('rates_uk', ['white', '#ffdd00'])
}

geojson = merged.geometry.__geo_interface__
locations = merged.index

traces = []
buttons = []

for i, (name, (colname, colorscale)) in enumerate(candidates.items()):
    visible = (i == 0)
    zmax_value = merged[colname].max()  
    traces.append(
        go.Choroplethmapbox(
            geojson=geojson,
            locations=merged.index,
            z=merged[colname],
            colorscale=colorscale,
            zmin=0, 
            zmax=zmax_value,
            colorbar_title=f'{name} 득표율',
            marker_opacity=0.7,
            marker_line_width=0,
            hovertext=[
                f"{merged.loc[idx, '읍면동']}<br>{name}: {merged.loc[idx, colname]:.2%}"
                for idx in merged.index
            ],
            hoverinfo='text',
            visible=visible
        )
    )

    buttons.append(dict(
        label=name,
        method='update',
        args=[{'visible': [j == i for j in range(len(candidates))]},
              {'title': f'{name} 득표율'}]
    ))



layout = go.Layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,
    mapbox_center={"lat": 36.5, "lon": 127.8},
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    updatemenus=[dict(
        buttons=buttons,
        direction="left",
        pad={"r": 10, "t": 10},
        showactive=True,
        type="buttons",
        x=0.5,
        xanchor="center",
        y=1.05,
        yanchor="top"
    )]
)

fig = go.Figure(data=traces, layout=layout)
fig.show()




fig.update_layout(
    mapbox=dict(
        center={"lat": 36.5, "lon": 127.8},
        zoom=6.4,
        style="carto-positron"
    ),
    margin={"r":0,"t":0,"l":0,"b":0}
)
fig.write_html("korea_vote_map.html")




for name, (colname, colorscale) in candidates.items():
    fig = go.Figure()

    fig.add_trace(
        go.Choroplethmapbox(
            geojson=geojson,
            locations=merged.index,
            z=merged[colname],
            colorscale=colorscale,
            zmin=0,
            zmax=merged[colname].max(),  # 개별 후보의 최대 득표율
            colorbar_title=f"{name} 득표율",
            marker_opacity=0.7,
            marker_line_width=0,
            hovertext=[
                f"{merged.loc[idx, '읍면동']}<br>{name}: {merged.loc[idx, colname]:.2%}"
                for idx in merged.index
            ],
            hoverinfo="text"
        )
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=6,
        mapbox_center={"lat": 36.5, "lon": 127.8},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title=f"{name} 득표율"
    )

    fig.write_html(f"{name}_map.html", full_html=True)



