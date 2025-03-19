import config
import core
import data

import asyncio



if __name__ == '__main__':

	async def main():

		settings = config.Settings()
		engine = core.service.Engine(settings.OPENAI_API_TOKEN.get_secret_value())
		database = data.Database(settings._GOOGLE_SERVICE_ACCOUNT(), '/storage')
		
		#print(await database.google_database.load(settings.GOOGLE_SERVICE_DATABASE_URL.get_secret_value()))
		#print(await database.local_database.load('database'))

	asyncio.run(main())