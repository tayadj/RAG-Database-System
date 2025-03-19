import config
import core
import data

import asyncio



if __name__ == '__main__':

	async def main():

		settings = config.Settings()

		database = data.Database(settings._GOOGLE_SERVICE_ACCOUNT(), '/storage')
		RAG_data = await database.local_database.load('database')

		engine = core.service.Engine(settings.OPENAI_API_TOKEN.get_secret_value(), RAG_data)

	asyncio.run(main())