import aiohttp
import google.oauth2.service_account
import google.auth.transport.requests
import json
import os



# Rebase databases as access points 

class Database:

	class GoogleDatabase:

		def __init__(self, google_service_account: dict):

			self.google_service_account = google_service_account
			self.access_token = None
			self.request = None
			self.credentials = google.oauth2.service_account.Credentials.from_service_account_info(
				self.google_service_account,
				scopes = ['https://www.googleapis.com/auth/spreadsheets']
			)

		async def authentificate(self):

			self.request = google.auth.transport.requests.Request()
			self.credentials.refresh(self.request)
			self.access_token = self.credentials.token

		async def load(self, url: str):

			if not self.access_token:

				await self.authentificate()

			async with aiohttp.ClientSession() as session:

				async with session.get(
					url, 
					headers = {
						'Authorization' : f'Bearer {self.access_token}'
					}
				) as response:

					if response.status == 200:

						data = await response.json()
						data = data.get('values', [])

					else:

						print(f"Failed to load data: {response.status} - {await response.text()}")
						data = []
		
			return data

		async def save(self, url: str, data: list):

			if not self.access_token:

				await self.authentificate()
				
			async with aiohttp.ClientSession() as session:

				async with session.put(
					url,
					headers = {
						'Authorization' : f'Bearer {self.access_token}',
						'Content-Type': 'application/json'
					},
					json = {
						'range': url.split('/')[-1],
						'values': data,
						'majorDimension': 'ROWS'
					},
					params = {
						'valueInputOption' : 'RAW'
					}
				) as response:

					if response.status == 200:

						result = await response.json()

					else:

						print(f"Failed to save data: {response.status} - {await response.text()}")
						result = {}

	class LocalDatabase:

		def __init__(self, path: str):

			self.path = path

		async def load(self, id: str):

			with open(f'{os.path.dirname(__file__)}/{self.path}/{id}.json', 'r', encoding = 'utf-8') as file:
			
				data = json.load(file)

			return data

	def __init__(self, google_service_account: dict, local_database_path: str):

		self.google_service_account = google_service_account
		self.local_database_path = local_database_path
		self.google_database = self.GoogleDatabase(self.google_service_account)
		self.local_database = self.LocalDatabase(self.local_database_path)