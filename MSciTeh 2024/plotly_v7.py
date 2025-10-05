import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import psutil

app = dash.Dash(__name__)

# Function to read and parse the data from test.txt
def load_data(file_path='testplumb2.txt'):
    dates = []
    values = []
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line based on the expected format
            date_str, value_str = line.split(' - Pulses_per_10s: ')
            # Convert date string to datetime object
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            # Convert the value to integer
            value = int(value_str.strip())
            dates.append(date)
            values.append(value)
    
    # Create a DataFrame
    df = pd.DataFrame({'Date': dates, 'Value': values})
    return df

# Function to aggregate the data by summing up every n points
def aggregate_data(df, n):
    aggregated_dates = df['Date'][::n].reset_index(drop=True)
    aggregated_values = df['Value'].rolling(window=n).sum()[n-1::n].reset_index(drop=True)
    
    aggregated_df = pd.DataFrame({'Date': aggregated_dates, 'Value': aggregated_values})
    return aggregated_df

# Function to check if save_serial.py is running
def is_script_running(script_name='save_serial.py'):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        cmdline = proc.info['cmdline']
        if cmdline and script_name in cmdline:
            return True
    return False

# Layout of the Dash app
app.layout = html.Div([
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=(datetime.now() - timedelta(days=1)).date(),
        end_date=datetime.now().date(),
        display_format='YYYY-MM-DD',
        style={'marginRight': '10px'}
    ),
    dcc.Input(
        id='start-time',
        type='text',
        value='00:00',
        placeholder='HH:MM',
        style={'marginRight': '10px'}
    ),
    dcc.Input(
        id='end-time',
        type='text',
        value='23:59',
        placeholder='HH:MM',
        style={'marginRight': '10px'}
    ),
    dcc.Input(
        id='n-points',
        type='number',
        value=1,
        min=1,
        step=1,
        placeholder='Enter number of points to sum',
        style={'marginRight': '10px'}
    ),
    html.Button('Update Plot', id='update-plot-button'),
    html.Br(),
    html.Br(),
    html.Button('Start save_serial.py', id='start-script-button', n_clicks=0),
    html.Button('Stop save_serial.py', id='stop-script-button', n_clicks=0),
    html.Div(id='script-status', style={'marginTop': '20px', 'fontWeight': 'bold'}),
    dcc.Graph(id='time-series-plot')
])

# Callback to update the plot based on the number of points to sum and the selected time interval
@app.callback(
    Output('time-series-plot', 'figure'),
    Input('update-plot-button', 'n_clicks'),
    State('n-points', 'value'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('start-time', 'value'),
    State('end-time', 'value')
)
def update_graph(n_clicks, n_points, start_date, end_date, start_time, end_time):
    if n_clicks is None:
        return go.Figure()

    if n_points is None or n_points < 1:
        n_points = 1

    # Load the data again to include any new entries
    df = load_data()

    # Combine the date and time inputs into datetime objects
    start_datetime = datetime.strptime(f'{start_date} {start_time}', '%Y-%m-%d %H:%M')
    end_datetime = datetime.strptime(f'{end_date} {end_time}', '%Y-%m-%d %H:%M')

    # Filter the DataFrame for the selected time interval
    df_filtered = df[(df['Date'] >= start_datetime) & (df['Date'] <= end_datetime)]

    # Aggregate the data by summing up every n_points
    aggregated_df = aggregate_data(df_filtered, n_points)
    
    # Create a line plot
    fig = go.Figure(data=[go.Scatter(x=aggregated_df['Date'], y=aggregated_df['Value'], mode='lines+markers')])

    fig.update_layout(
        title=f'Sum of Every {n_points} Pulses_per_10s Over Time',
        title_x=0.5,
        xaxis_title='Date and Time',
        yaxis_title='Sum of Pulses_per_10s',
        xaxis=dict(tickformat='%Y-%m-%d %H:%M:%S')
    )

    return fig

# Combined callback to manage script status (start/stop) and display the status
@app.callback(
    Output('script-status', 'children'),
    [Input('start-script-button', 'n_clicks'),
     Input('stop-script-button', 'n_clicks')]
)
def manage_script_status(start_n_clicks, stop_n_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return 'save_serial.py is not running'

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'start-script-button':
        if not is_script_running():
            subprocess.Popen(['python', 'save_serial.py'])
            return 'save_serial.py is running'
        else:
            return 'save_serial.py is already running'

    elif button_id == 'stop-script-button':
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info['cmdline']
            if cmdline and 'save_serial.py' in cmdline:
                proc.terminate()
                return 'save_serial.py has been stopped'
        return 'save_serial.py is not running'

    return 'save_serial.py is not running'


if __name__ == '__main__':
    app.run(debug=True)
