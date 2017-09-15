import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout
import plotly


def plot_data(data_dictionary, header_list):

    # Extract Data
    for key, value in data_dictionary.items():
        data_dictionary[key] = data_dictionary[value]

    # Create traces
    trace0 = go.Scatter(
        x=Time_stamp,
        y=VBUS_volts,
        mode='lines+markers',
        name='VBUS_volts (V)'
    )
    trace1 = go.Scatter(
        x=Time_stamp,
        y=VBUS_curr,
        mode='lines+markers',
        name='VBUS Current (A)'
    )
    trace2 = go.Scatter(
        x=Time_stamp,
        y=VCONN_volts,
        mode='lines',
        name='VCONN Voltage (V)'
    )
    trace3 = go.Scatter(
        x=Time_stamp,
        y=VCONN_volts,
        mode='lines',
        name='VCONN Voltage (V)'
    )
    trace4 = go.Scatter(
        x=Time_stamp,
        y=VCONN_curr,
        mode='lines',
        name='VCONN Current (A)'
    )
    trace5 = go.Scatter(
        x=Time_stamp,
        y=CC1_volts,
        mode='lines',
        name='CC1 Voltage (V)'
    )
    trace6 = go.Scatter(
        x=Time_stamp,
        y=CC1_curr,
        mode='lines',
        name='CC1 Current (A)'
    )
    trace7 = go.Scatter(
        x=Time_stamp,
        y=CC2_volts,
        mode='lines',
        name='CC2 Voltage (V)'
    )
    trace8 = go.Scatter(
        x=Time_stamp,
        y=CC2_curr,
        mode='lines',
        name='CC2 Current (A)'
    )
    data = [trace0, trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8]

    plotly.offline.plot({
        "data": data,
        "layout": Layout(title="PD PY Data Capture")})
