import aiohttp
import googleapiclient
import google.oauth2.service_account
import google.auth.transport.requests



class Database:

	def __init__(self, google_service_account: dict, ):

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

		print(self.request, self.credentials, self.access_token)

	async def load(self, url: str):

		if not self.access_token:

			await self.authentificate()

		async with aiohttp.ClientSession() as session:

			async with session.get(url, headers = {'Authorization' : f'Bearer {self.access_token}'}) as response:

				if response.status == 200:

					data = await response.json()
					data = data.get('values', [])

				else:

					print(f"Failed to load data: {response.status} - {await response.text()}")
					data = []
		
		return data