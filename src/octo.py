import requests
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime as dt
import plotly.graph_objects as go

class Energy_Analyser:
	def __init__(self):
		load_dotenv()
		self.API_KEY = os.getenv('API_KEY')
		self.ACCOUNT = os.getenv('ACCOUNT')
		self.MPAN = os.getenv('MPAN')
		self.SERIAL = os.getenv('SERIAL')

		self.BASE_URL = 'https://api.octopus.energy'

	def api_call(self,url,date_from,date_to,page_size=1000):
		auth = requests.auth.HTTPBasicAuth(self.API_KEY+':','')	# pass empty password as it is not required with API_KEY

		response = requests.get(
			url,
			headers={'Content-Type': 'application/json'},
			auth=auth,
			params={
				'page_size':page_size,
				'date_from':date_from,
				'date_to':date_to
			}
			)

		contents = response.json()
		print(response.headers)

		return contents

	def get_consumption(self,date_from=dt.now().replace(year=dt.now().year - 1),date_to=dt.now()):
		print(f'Getting usage data for between {date_from.date()} and {date_to.date()}...')
		url = f"{self.BASE_URL}/v1/electricity-meter-points/{self.MPAN}/meters/{self.SERIAL}/consumption/?page=1"
		
		contents = self.api_call(
			url,
			date_from=date_from,
			date_to=date_to
			)

		print(f"Returning {contents['count']} records...")
		results = contents['results']

		data = pd.DataFrame(results)

		while contents['next'] is not None:
			print(url.split('?')[-1])
			url = contents['next']

			contents = self.api_call(url)
			
			data = data.append(contents['results'],ignore_index=True)
			print(data.size//3)

		data['interval_start'] = pd.to_datetime(data['interval_start'])
		data['interval_end'] = pd.to_datetime(data['interval_end'])
		
		return data

	def daily_average(self,data):
		'''method to calculate the average usage for a day'''
		data['time'] = data['interval_start'].dt.strftime('%H:%M')
		data.drop(['interval_start','interval_end'],inplace=True,axis=1)
		df_grp = data.groupby(['time']).mean()
		return df_grp.reset_index()

	def visualise(self,data):
		fig = go.Figure(
			data=[go.Bar(x=data['time'],y=data['consumption'])]
		)
		fig.show()

if __name__ == '__main__':
	EA = Energy_Analyser()
	data = EA.get_consumption(
		date_from=dt.now().replace(year=dt.now().year - 1),
		date_to=dt.now()
		)

	# EA.visualise(data)

	print(data.interval_start.min(),data.interval_end.max())

	data['time'] = data['interval_start'].dt.time

	data.drop(['interval_start','interval_end'],inplace=True,axis=1)

	df_grp = data.groupby(['time']).sum()
	print(df_grp)

	df_grp.hist()

