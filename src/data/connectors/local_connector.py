import json
import os



class LocalConnector:

	def __init__(self, path: str):

		self.path = path

	async def load(self, id: str):

		with open(f'{os.path.dirname(__file__)}/../{self.path}/{id}.json', 'r', encoding = 'utf-8') as file:
			
			data = json.load(file)

		return data