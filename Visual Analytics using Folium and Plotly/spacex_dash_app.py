# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown component
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',  # Default value when the dropdown loads
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    
    html.Br(),

    # Pie chart component
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),

    # Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),
    
    html.Br(),

    # Scatter plot component
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for the pie chart based on selected launch site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, 
                     values='class', 
                     names='Launch Site', 
                     title='Total Success Launches by Site')
        return fig
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.pie(site_df, 
                     names='class', 
                     title=f'Total Success Launches for site {entered_site}',
                     labels={'class': 'Launch Outcome'},
                     hole=0.3)
        return fig

# Callback for the scatter plot based on selected site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all sites'
        )
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {entered_site}'
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()