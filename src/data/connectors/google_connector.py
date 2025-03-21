import aiohttp
import google.oauth2.service_account
import google.auth.transport.requests



class GoogleConnector:

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

		return result