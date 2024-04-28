import plotly.graph_objs as go
from shiny import App, Inputs, Outputs, Session, render, ui
import numpy as np
import pandas as pd
import geopandas as gpd
from shinywidgets import output_widget, render_widget
import matplotlib.pyplot as plt
import plotly.express as px





# Load data

# india_state = gpd.read_file("india-polygon.shp")
# rainfall = pd.read_csv("rainfall.csv")[["SUBDIVISION", "YEAR", "ANNUAL"]]
# rainfall_data = pd.merge(india_state, rainfall, left_on = "st_nm", right_on = "SUBDIVISION", how = "left")
# agriculture_data = pd.read_csv("ICRISAT-District Level Data.csv")
# agriculture_data = agriculture_data.groupby(['State Name', 'Year']).sum().reset_index()
# agriculture_data.drop(columns=['Dist Code', 'Dist Name', 'State Code'], inplace=True)
# agriculture_data_year = [pd.merge(india_state, agriculture_data[agriculture_data['Year'] == year], right_on='State Name', left_on='st_nm', how='left') for year in range(1978, 2018)]
# states = india_state["st_nm"].unique()

# #district wise data
# indian_district = gpd.read_file("output.shp")
# agri_district = pd.read_csv("ICRISAT-District Level Data.csv")
# district_agri_map = pd.merge(indian_district, agri_district, left_on = 'distname', right_on='Dist Name', how = 'left')





india_state = gpd.read_file("india-polygon.shp")
india_state['st_nm'] = india_state['st_nm'].str.lower()
rainfall = pd.read_csv("final_rainfall.csv")
rainfall['State'] = rainfall['State'].str.lower()
# print(rainfall.head())
rainfall_data = pd.merge(india_state, rainfall, left_on = "st_nm", right_on = "State", how = "inner")
agriculture_data = pd.read_csv("ICRISAT-District Level Data.csv")
agriculture_data['State Name'] = agriculture_data['State Name'].str.lower()
agriculture_data = agriculture_data.groupby(['State Name', 'Year']).sum().reset_index()
agriculture_data.drop(columns=['Dist Code', 'Dist Name', 'State Code'], inplace=True)
agriculture_data_year = [pd.merge(india_state, agriculture_data[agriculture_data['Year'] == year], right_on='State Name', left_on='st_nm', how='left') for year in range(1978, 2018)]
states = india_state["st_nm"].unique()





# State Comparison
app_ui = ui.page_fluid(
    ui.card(
        ui.row(
            ui.column(6, ui.input_select("column_select", label="Select Column", choices=list(agriculture_data.columns[5:]))),
            ui.column(6, ui.input_slider("year_slider", label="Select Year", min=1978, max=2017, step=1, value=2000, animate=False))
        ),
        ui.row(
            ui.column(
                6,
                output_widget("agri_produce_bar"),   
            ),
            ui.column(
                6,
                output_widget("agri_produce_doughnut"),  
                # style="border: 1px solid black; ",  
            ),
        ),
        ui.row(
            ui.column(
                6,
                output_widget("agri_produce_map"),  
                # style="border: 1px solid black; ",  
            ),
            ui.column(
                6,
                output_widget("rainfall_map"),  
            )
        )
    ),

    
    # # State Comparison
    # ui.card(
    #     ui.row(
    #         ui.column(6, ui.input_select("column_select_compare", label="Select Column", choices=list(agriculture_data.columns[5:]))),
    #         ui.column(6, ui.input_slider("year_slider_compare", label="Select Year", min=1978, max=2017, step=1, value=2000, animate=False))
    #     ),
    #     ui.row(
    #         # left state
    #         ui.column(6, 
    #             ui.card(
    #                 ui.input_select("select_left_state", label = "Select State", choices = list(states)), 
    #                 ui.output_plot("left_state_produce_map")
    #             )
    #         ),
    #         #Right state

    #         ui.column(6, 
    #             ui.card(
    #                 ui.row(
    #                     ui.input_select("select_right_state", label = "Select State", choices = list(states)), 
    #                 ),
    #                 ui.row(
    #                     ui.output_plot("right_state_produce_map")
    #                 )
    #             )
    #         )
    #     ),
    # ),


    ui.card(
        ui.row(
            ui.column(6, ui.input_select("column_select_compare", label="Select Crop", choices=list(agriculture_data.columns[5:])), multiple = False),
            ui.column(6, ui.input_selectize("state_select_compare", label="Select States", choices=list(states), multiple = True, remove_button =True, selected=["rajasthan", "gujarat"])),
        ),
        ui.row(
            ui.column(6, output_widget("time_series")),
            ui.column(6, output_widget("buuble_plot"))
        )
    ),


)

def no_data_available_plot():
    # Create an empty scatter plot with no data
    trace = go.Scatter(x=[], y=[], mode='markers', marker=dict(color='rgba(0,0,0,0)'), name='No data available')

    # Add text annotation for "No data available"
    layout = go.Layout(title='No Data Available', showlegend=False, width=600, height=400, 
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       annotations=[dict(x=0.5, y=0.5, text='No data available', showarrow=False, 
                                         font=dict(size=20, color='black'))])

    # Create the figure object
    fig = go.Figure(data=[trace], layout=layout)

    return fig



def update_agri_map(year, column):
    merged_data = agriculture_data_year[year - 1978]
    merged_data[column] = merged_data[column].replace(np.nan, -5)

    fig = go.Figure(go.Choroplethmapbox(
            geojson=merged_data.geometry.__geo_interface__,
            locations=merged_data.index,
            z=merged_data[column],
            colorscale='OrRd',
            zmin=merged_data[column].min(),
            zmax=merged_data[column].max(),
            colorbar=dict(title=column),
            hoverinfo='text',
            text=merged_data.apply(lambda row: f"{row['st_nm']}: {row[column]}", axis=1)
            )
        )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=3,
        mapbox_center={"lat": 20.5937, "lon": 78.9629},
        title = "Area of produce"
    )

    return fig

def update_agri_bar(year, column):
    # print("Hello from update agri produce bar")
    agriculture_data_y = agriculture_data.sort_values(by=column, ascending=True)
    agriculture_data_y = agriculture_data_y[agriculture_data_y['Year'] == year]
    fig = go.Figure(go.Bar(
        x=agriculture_data_y[column],
        y=agriculture_data_y['State Name'],
        orientation='h'
    ))

    fig.update_layout(
        title=f'{column} for year {year}',
        xaxis_title=column,
        yaxis_title='State Name',
        template='plotly_white'
    )

    return fig
def update_rainfall_map(year):
    rainfall_data_temp = rainfall_data[rainfall_data["YEAR"] == year]
    fig = go.Figure(go.Choroplethmapbox(
            geojson=rainfall_data_temp.geometry.__geo_interface__,
            locations=rainfall_data_temp.index,
            z=rainfall_data_temp["ANNUAL"],
            colorscale='OrRd',
            zmin=rainfall_data_temp["ANNUAL"].min(),
            zmax=rainfall_data_temp["ANNUAL"].max(),
            colorbar=dict(title="ANNUAL Rainfall"),
            hoverinfo='text',
            text=rainfall_data_temp.apply(lambda row: f"{row['st_nm']}: {row['ANNUAL']}", axis=1)
        )
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=3,
        mapbox_center={"lat": 20.5937, "lon": 78.9629},
        title = "Annual Rainfall in MMS"
    )
    return fig

def update_agri_doughnut(year, column):
    agriculture_data_y = agriculture_data.sort_values(by=column, ascending=True)
    agriculture_data_y = agriculture_data_y[agriculture_data_y['Year'] == year]
    total_value = agriculture_data_y[column].sum()
    threshold = total_value * 0.01
    agriculture_data_y = agriculture_data_y[agriculture_data_y[column] >= threshold]
    other_value = total_value - agriculture_data_y[column].sum()
    labels = agriculture_data_y['State Name'].tolist() + ['Others']
    values = agriculture_data_y[column].tolist() + [other_value]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.7, textinfo='percent+label')])
    fig.update_layout(showlegend=False, title = "Contribution of States")
    return fig


# def update_state_map(state, year, column):
#     # Filter the district data for the specified state and year
#     data = district_agri_map[(district_agri_map['statename'] == state) & (district_agri_map['Year'] == year)]

#     # Check if there is no data available for the specified state and year
#     if len(data) == 0:
#         return no_data_available_plot()

#     # Create a new figure and axis
#     fig, ax = plt.subplots()

#     # Plot the district data
#     data.plot(column=column, cmap='OrRd', linewidth=0.8, edgecolor='0.8', ax=ax)

#     # Customize the appearance of the plot
#     ax.set_title(f"Area of produce for {state}")
#     ax.set_aspect('equal')  # Ensure equal aspect ratio
#     ax.axis('off')  # Turn off axis labels

#     # Show the plot
#     # plt.show()
#     return fig


def update_timeseries(states, column):
    # print("hello from left update time series ")
    fig = go.Figure()  # Create an empty figure
    # print(states)
    for state in states:
        ts = agriculture_data[agriculture_data["State Name"] == state][[column, 'Year']]
        if len(ts) == 0:
            # print("Empty ", states)
            continue  # Skip if no data available for the state

        trace = go.Scatter(x=ts['Year'], y=ts[column], mode='lines+markers', name=f'Time Series ({state})')
        fig.add_trace(trace)  # Add trace for the state to the figure

    # Update the layout for the plot
    fig.update_layout(
        title='Time Series Line Plot',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Value'),
        hovermode='closest'
    )

    return fig


# def update_bubble_plot(states, column):
#     categories = []
#     y = rainfall[rainfall["State"].isin(states)]
#     z = agriculture_data[agriculture_data["State Name"].isin(states)]
#     data = pd.merge(z, y, left_on = ["Year", "State Name"], right_on = ["YEAR", "State"], how = "inner")
#     print(data.head(10))
#     fig = px.scatter(data, x="Year", y=column, size="ANNUAL", color="State Name")
#     fig.update_layout(
#         showlegend=True
#     )
#     return fig

def update_bubble_plot(states, column):
    categories = []
    y = rainfall[rainfall["State"].isin(states)]
    z = agriculture_data[agriculture_data["State Name"].isin(states)]
    data = pd.merge(z, y, left_on=["Year", "State Name"], right_on=["YEAR", "State"], how="inner")
    
    fig = px.scatter(data, x="Year", y=column, size="ANNUAL", color="State Name")
    
    fig.update_traces(
        showlegend=True,  # Show legend for the bubble size scale
        selector=dict(type='scatter', mode='markers')
    )
    
    fig.update_layout(
        showlegend=True,
        legend_title="State",
        margin=dict(l=0, r=0, t=0, b=0),  # Adjust the plot margins
    )
    
    return fig



def server(input, output, session):
    @output
    @render_widget
    def agri_produce_map():
        return update_agri_map(input.year_slider(), input.column_select())

    @output
    @render_widget
    def agri_produce_bar():
        return update_agri_bar(input.year_slider(), input.column_select())

    @output
    @render_widget
    def agri_produce_doughnut():
        return update_agri_doughnut(input.year_slider(), input.column_select())

    @output
    @render_widget
    def rainfall_map():
        return update_rainfall_map(input.year_slider())

    # @output
    # @render_widget
    # def left_state_produce_map():
    #     s = input.select_left_state()
    #     y = input.year_slider_compare()
    #     column = input.column_select_compare()
    #     return update_state_map(s, y, column)
    
    # @output
    # @render_widget
    # def right_state_produce_map():
    #     s = input.select_right_state()
    #     y = input.year_slider_compare()
    #     column = input.column_select_compare()
    #     return update_state_map(s, y, column)
   
    # @output
    # @render.ui
    # def left_time_series():
    #     print("hello from left time series")
    #     s = input.select_left_state()
    #     column = input.column_select_compare()
    #     print(s, column)
    #     return update_timeseries(s, column)
    
    @output
    @render_widget
    def time_series():
        s = input.state_select_compare()
        column = input.column_select_compare()
        # print(type(s), type(column))
        return update_timeseries(s, column)
    
    @output
    @render_widget
    def buuble_plot():
        s = input.state_select_compare()
        column = input.column_select_compare()
        # print(type(s), type(column))
        return update_bubble_plot(s, column)

app = App(app_ui, server)
app.run()
