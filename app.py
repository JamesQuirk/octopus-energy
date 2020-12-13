import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from src.octo import Energy_Analyser

app = dash.Dash(__name__)
EA = Energy_Analyser()

data = EA.get_consumption()

daily = EA.daily_average(data.copy())

max_date = data['interval_start'].max().date()
min_date = data['interval_start'].min().date()

app.layout = html.Div(children=[
	html.Div(html.H1(children='Energy Usage')),
	html.Div(
		dcc.Markdown(f'Data being displayed for the date range: **{min_date}** to **{max_date}**')
	),
	dcc.Graph(
		id='full-period',
		figure=px.bar(
			data[['interval_start','consumption']],
			x='interval_start',
			y='consumption',
			title='Energy usage by date and time',
			labels={'consumption':'Consumption (kWh)'})
	),
	dcc.Graph(
		id='daily-avg',
		figure=px.bar(
			daily,
			x='time',
			y='consumption',
			title='Average daily energy usage',
			labels={'consumption':'Consumption (kWh)'})
	)
	]
)


if __name__ == '__main__':
	app.run_server(debug=True)