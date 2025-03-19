import config
import core
import data

import asyncio



if __name__ == '__main__':

	async def main():

		settings = config.Settings()
		database = data.Database(settings._GOOGLE_SERVICE_ACCOUNT(), settings.LOCAL_DATABASE_URL.get_secret_value())
		engine = core.service.Engine(settings.OPENAI_API_TOKEN.get_secret_value(), (await database.local_database.load('database')))

		dataframe = (await database.google_database.load(settings.GOOGLE_DATABASE_URL.get_secret_value()))[:3]

		for record in dataframe:

			record.append(await engine.request(record[0]))




		print(dataframe)
		
		await database.google_database.save(
			settings.GOOGLE_DATABASE_URL.get_secret_value(),
			dataframe
		)

		#RAG_data = await database.local_database.load('database')

		#engine = core.service.Engine(settings.OPENAI_API_TOKEN.get_secret_value(), RAG_data)

		#await engine.request('How can I better manage my stock to avoid running out of popular items?')

	asyncio.run(main())