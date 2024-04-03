import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# Sample Data
# Replace this with your actual dataset
df = pd.read_csv('StudentPerformance.csv')

# Initialize the Dash app
app = dash.Dash(__name__)
app.layout = html.Div(className="parent_container", children=[
    html.Div(className="row", children=[
        html.Div(className="cell", children=[
            html.Label("Parental Education", style={'font-size': '12px'}),
            dcc.Checklist(
                id='education-checklist',
                options=[{'label': level, 'value': level} for level in df['parental level of education'].unique()],
                value=["bachelor's degree", "some college"],  # Default selected values
                inline=True,
                style={'width': '50%'},
                labelStyle={'font-size': '12px'}
                
            ),  # Display checklist items horizontally
            
            html.Label("Filter by Race", style={'font-size': '12px'}),
            dcc.Dropdown(
                id='race-dropdown',
                options=[{'label': race, 'value': race} for race in df['race/ethnicity'].unique()],
                multi=True,
                value=['group B', 'group C', 'group D']
            )
        ], style={'display': 'flex', 'flex-direction': 'row','width':'100%'}),
        
        html.Div(className="cell", children=[
            html.Div(className="graphs_container", children=[
                dcc.Graph(id='graph1', style={'width': '50%', 'height': '310px','border': '0.5px solid black'}),
                dcc.Graph(id='graph2', style={'width': '50%', 'height': '310px','border': '0.5px solid black'})
            ], style={'display': 'flex', 'flex-direction': 'row'})
        ]),
    ]),
    html.Div(className="row", children=[
        html.Div(className="cell", children=[
            html.Div([
                html.Label("Select Subject", style={'font-size': '12px'}),
                dcc.Dropdown(
                    id='subject-dropdown',
                    options=[
                        {'label': 'Math Score', 'value': 'math score'},
                        {'label': 'Reading Score', 'value': 'reading score'},
                        {'label': 'Writing Score', 'value': 'writing score'},
                    ],
                    value='math score',
                    style={'width': '50%'}
                ),
                html.Label("Test Preparation Course", style={'font-size': '12px'}),
                dcc.Checklist(
                    id='test-prep-checklist',
                    options=[
                        {'label': 'Completed', 'value': 'completed'},
                        {'label': 'None', 'value': 'none'}
                    ],
                    value=['completed', 'none'],
                    labelStyle={'font-size': '12px'}
                ),
            ], style={'display': 'flex', 'flex-direction': 'row'}),
        ]),
        html.Div(className="cell", children=[
            dcc.Graph(id='graph3', style={'width': '50%', 'height': '390px','border': '0.5px solid black'}),
            dcc.Graph(id='graph4', style={'width': '50%', 'height': '390px','border': '0.5px solid black'})
        ], style={'display': 'flex', 'flex-direction': 'row'})
    ]),
])

# Callbacks to update the graphs based on user input

import numpy as np

# Callback to update graph1 based on checklist selection
@app.callback(
    Output('graph1', 'figure'),
    [Input('education-checklist', 'value'),
     Input('subject-dropdown', 'value')]
)
def update_bar_chart(selected_education, selected_subject):
    if not selected_education:
        return {}

    # Filter data based on selected education levels, races, and reduced lunch
    filtered_data = df[df['parental level of education'].isin(selected_education)]

    # Separate data for reduced lunch and non-reduced lunch
    reduced_lunch_data = filtered_data[filtered_data['lunch'] == 'free/reduced']
    non_reduced_lunch_data = filtered_data[filtered_data['lunch'] == 'standard']

    # Calculate average scores for each parental education level
    avg_scores_reduced_lunch = reduced_lunch_data.groupby('parental level of education')[selected_subject].mean()
    avg_scores_non_reduced_lunch = non_reduced_lunch_data.groupby('parental level of education')[selected_subject].mean()

    # Create bar chart
    fig = go.Figure()

    # Add trace for reduced lunch
    fig.add_trace(go.Bar(
        x=avg_scores_reduced_lunch.index,
        y=avg_scores_reduced_lunch.values,
        name='Reduced Lunch',
        marker_color='green'  # Set color to green
    ))

    # Add trace for non-reduced lunch
    fig.add_trace(go.Bar(
        x=avg_scores_non_reduced_lunch.index,
        y=avg_scores_non_reduced_lunch.values,
        name='Non-Reduced Lunch',
        marker_color='red'  # Set color to red
    ))

    # Update layout
    fig.update_layout(
        barmode='group',
        title='Average Exam Scores by Parental Education Level',
        xaxis_title='Parental Education Level',
        yaxis_title=selected_subject
    )
    fig.update_traces(marker_line_color='black', marker_line_width=1, opacity=0.8)

    return fig



@app.callback(
    Output('graph2', 'figure'),
    Input('race-dropdown', 'value'),
    Input('subject-dropdown', 'value'),
    Input('test-prep-checklist', 'value')
)
def update_bar_chart(selected_races, selected_subject, selected_prep):
    if not selected_races:
        return {}

    # Filter data based on selected races
    filtered_data = df[df['race/ethnicity'].isin(selected_races)]
    

    # Calculate average scores by race and subject
    avg_scores = filtered_data.groupby(['race/ethnicity']).mean().reset_index()

    # Melt the DataFrame to have separate rows for each subject
    avg_scores = pd.melt(avg_scores, id_vars=['race/ethnicity'], value_vars=['reading score', 'writing score', 'math score'],
                         var_name='Subject', value_name='Average Score')
    
    # Create bar chart
    fig = px.bar(avg_scores, x='race/ethnicity', y='Average Score', color='Subject',
                 barmode='group', title='Average Exam Scores by Race and Subject',
                 color_discrete_map={'reading score': 'blue', 'writing score': 'red', 'math score': 'green'})

    # Add black bordering to the bars
    fig.update_traces(marker_line_color='black', marker_line_width=1, opacity=0.8)
    
    return fig


@app.callback(
    Output('graph3', 'figure'),
    Input('subject-dropdown', 'value'),
    Input('test-prep-checklist', 'value')
)
def update_histogram(selected_subject, selected_prep):
    if not selected_subject:
        return {}

    # Filter data based on selected subject and prep course completion
    filtered_data = df[df[selected_subject].notna()]
    if 'completed' in selected_prep and 'none' in selected_prep:
        pass  # Keep all data
    elif 'completed' in selected_prep:
        filtered_data = filtered_data[filtered_data['test preparation course'] == 'completed']
    elif 'none' in selected_prep:
        filtered_data = filtered_data[filtered_data['test preparation course'] == 'none']
    else:
        return {}  # No data selected

    # Create histogram
    fig = px.histogram(filtered_data, x=selected_subject, color='gender', title='Histogram of Exam Scores')
    fig.update_traces(marker_line_color='black', marker_line_width=1, opacity=0.8)

    
    return fig

# Callback to update graph4 (Boxplot) based on dropdown and checklist selection
@app.callback(
    Output('graph4', 'figure'),
    Input('subject-dropdown', 'value'),
    Input('test-prep-checklist', 'value')
)
def update_boxplot(selected_subject, selected_prep):
    if not selected_subject:
        return {}

    # Filter data based on selected subject and prep course completion
    filtered_data = df[df[selected_subject].notna()]
    if 'completed' in selected_prep and 'none' in selected_prep:
        pass  # Keep all data
    elif 'completed' in selected_prep:
        filtered_data = filtered_data[filtered_data['test preparation course'] == 'completed']
    elif 'none' in selected_prep:
        filtered_data = filtered_data[filtered_data['test preparation course'] == 'none']
    else:
        return {}  # No data selected

    # Create boxplot
    fig = px.box(filtered_data, x='test preparation course', y=selected_subject, color='gender', points="all", title='Boxplot of Exam Scores by Prep Course Completion')
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
