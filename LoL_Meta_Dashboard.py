#!/usr/bin/env python
# coding: utf-8

# In[21]:


import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server

pick_grouped = pd.read_csv("pick_grouped.csv", index_col="patch")
ban_grouped = pd.read_csv("ban_grouped.csv", index_col="patch")
pick_stats = pd.read_csv("pick_stats.csv", index_col="patch")
win_stats = pd.read_csv("win_stats.csv", index_col="patch")
presence_stats = pd.read_csv("presence_stats.csv", index_col="patch")
win_pct_sorted = pd.read_csv("win_pct_sorted.csv", index_col="patch")
presence_pct_sorted = pd.read_csv("presence_pct_sorted.csv", index_col="patch")
ban_pct_sorted = pd.read_csv("ban_pct_sorted.csv", index_col="patch")
top_5_presence = pd.read_csv("top_5_presence.csv", index_col="patch")
champion_w_release = pd.read_csv("champion_w_release.csv", index_col="index")

champ_names = pick_grouped.T.index.sort_values().to_list()

app.layout = html.Div([
    html.Div(html.H3(
        "LoL Professional Meta Analysis",
        style={"text-align": "center"}
    )
            ),
    html.Div(dcc.Dropdown(id="select_champ",
                          options=champ_names,
                          value=champ_names[0]
                         )),
    html.Div(dcc.Graph(id="main_graph", figure={}, style={"height": 800})),
    html.Div(dcc.Input(id="select_pct",
                       placeholder='Enter a %',
                       type='number',
                       value=50
                      )),
    html.Div(dcc.Dropdown(id="select_kpi",
                          options=["Presence", "Win Rate", "Ban Rate"],
                          value="Presence"
                         )),
    html.Div(dcc.Graph(id="presence_nominal", figure={}, style={"height": 400})),
    html.Div(dcc.Graph(id="presence_lifespan", figure={}, style={"height": 400}))
])


@app.callback(Output(component_id="main_graph", component_property="figure"),
              Input(component_id="select_champ", component_property="value")
             )
def generate_main_graph(champ):
    p = pick_grouped[champ].values
    b = ban_grouped[champ].values

    pick_stats["P"] = p
    pick_stats["B"] = b
    pick_stats["P"].fillna(0, inplace=True)
    pick_stats["B"].fillna(0, inplace=True)
    pick_stats["N"] = pick_stats.patch_games-pick_stats.B-pick_stats.P

    fig1 = make_subplots(rows=3,
                        cols=1,
                        shared_xaxes=True,
                        x_title='Current Patch')
    fig1.add_trace((go.Scatter(x=win_stats["Date"],
                              y=win_stats["top_5"],
                              name="Top 5 WR",
                              hovertext=win_pct_sorted.index.to_list(),
                              hoverinfo="text+x+y",
                              marker={"color": "Red"})),
                   row=1, col=1)
    fig1.add_trace((go.Scatter(x=win_stats["Date"],
                              y=win_stats["top_20"],
                              name="Top 20 WR",
                              hovertext=win_pct_sorted.index,
                              hoverinfo="text+y",
                              marker={"color": "RoyalBlue"})),
                   row=1, col=1)
    fig1.add_trace((go.Scatter(x=win_pct_sorted["Date"],
                              y=win_pct_sorted[champ],
                              name=champ + " WR",
                              hovertext=win_pct_sorted.index,
                              hoverinfo="text+y",
                              marker={"color": "ForestGreen"})),
                   row=1, col=1)
    fig1.add_trace((go.Scatter(x=ban_pct_sorted["Date"],
                              y=ban_pct_sorted[champ],
                              name=champ + " BR",
                              hovertext=ban_pct_sorted.index,
                              hoverinfo="text+y",
                              marker={"color": "DarkOrange"})),
                   row=2, col=1)
    fig1.add_trace((go.Scatter(x=presence_pct_sorted["Date"],
                              y=presence_stats.iloc[:, 1],
                              name="Top 5 Presence",
                              hovertext=presence_pct_sorted.index,
                              hoverinfo="text+y",
                              marker={"color": "Red"})),
                   row=2, col=1)
    fig1.add_trace((go.Scatter(x=presence_pct_sorted["Date"],
                              y=presence_stats.iloc[:, 3],
                              name="Top 20 Presence",
                              hovertext=presence_pct_sorted.index,
                              hoverinfo="text+y",
                              marker={"color": "RoyalBlue"})),
                   row=2, col=1)
    fig1.add_trace((go.Scatter(x=presence_pct_sorted["Date"],
                              y=presence_pct_sorted[champ],
                              name=champ + " Presence",
                              hovertext=presence_pct_sorted.index,
                              hoverinfo="text+y",
                              marker={"color": "ForestGreen"})),
                   row=2, col=1)
    fig1.add_trace(go.Bar(x=pick_stats["Date"], 
                         y=pick_stats.loc[:, "B"],
                         name="Bans",
                         hovertext=pick_stats.index,
                         hoverinfo="text+y",
                         marker={"color": "DarkOrange"}),
                  row=3, col=1)
    fig1.add_trace(go.Bar(x=pick_stats["Date"], 
                         y=pick_stats.loc[:, "P"],
                         name="Picks",
                         hovertext=pick_stats.index,
                         hoverinfo="text+y",
                         marker={"color": "Lime"}),
                  row=3, col=1)
    fig1.add_trace(go.Bar(x=pick_stats["Date"], 
                         y=pick_stats.loc[:, "N"],
                         name="No Presence",
                         hovertext=pick_stats.index,
                         hoverinfo="text+y",
                         marker={"color": "Black"}),
                  row=3, col=1)
    fig1.update_layout(title=champ + " Pro Stats", title_x=0.5, title_xanchor="center", 
                      barmode="stack",
                      yaxis={"title": "Win Rate %"},
                      yaxis2={"title": "BP Presence %"},
                      yaxis3={"title": "# of Games"})

    fig1.update_layout(hovermode="x unified")
    fig1.update_traces(xaxis='x1')
    return fig1

@app.callback(Output(component_id="presence_nominal", component_property="figure"),
              Output(component_id="presence_lifespan", component_property="figure"),
              Input(component_id="select_champ", component_property="value"),
              Input(component_id="select_pct", component_property="value"),
              Input(component_id="select_kpi", component_property="value"),
              
             )
def generate_presence_graphs(champ, pct, kpi):
    if kpi == "Win Rate":
        cur_df = win_pct_sorted
    elif kpi == "Presence":
        cur_df = presence_pct_sorted
    elif kpi == "Ban Rate":
        cur_df = ban_pct_sorted
    if champ==None:
        champ="Aatrox"
    df = pd.DataFrame()
    for charac in cur_df.columns[:-1]:
        cur_total = 0
        for patch in presence_stats.index:
            if (cur_df.loc[patch, charac] >= pct):
                cur_total += 1
        df.loc[charac, "Total"] = cur_total
        df.loc[charac, "Pct"] = np.round(cur_total/champion_w_release[champion_w_release["Champion"]==charac].iloc[0, 3], 3)
    df["Color"] = ""
    for i in df.index:
        if i==champ:
            df.loc[i, "Color"] = "Red"
        else:
            df.loc[i, "Color"] = "DodgerBlue"
    colors = df.to_dict()["Color"]
    
    df.sort_values(by="Total", ascending=True, inplace=True)
    fig2 = px.bar(df,
               y="Total",
               title=f"Total Patches Where Each Champion Exceeds {pct}% {kpi}",
               color=df.index,
               color_discrete_map=colors,
               labels={"Total": "Frequency"})
    fig2.update_layout(showlegend=False, xaxis={'visible': False, 'showticklabels': False},
                       title_x=0.5, title_xanchor="center")
    
    df.sort_values(by="Pct", ascending=True, inplace=True)
    fig3 = px.bar(df, 
               y="Pct",
               title=f"Ratio of Lifespan Where Each Champion Exceeds {pct}% {kpi}",
               color=df.index,
               color_discrete_map=colors,
               labels={"Pct": "Ratio of Lifespan"})
    fig3.update_layout(showlegend=False, xaxis={'visible': False, 'showticklabels': False},
                       title_x=0.5, title_xanchor="center")
    return fig2, fig3

if __name__ == "__main__":
    app.run_server(debug=False)

