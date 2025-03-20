import config
import core
import data

import asyncio
import json



if __name__ == '__main__':

	async def main():

		settings = config.Settings()
		database = data.Database(settings._GOOGLE_SERVICE_ACCOUNT(), settings.LOCAL_DATABASE_URL.get_secret_value())
		engine = core.services.Engine(settings.OPENAI_API_TOKEN.get_secret_value(), (await database.local_database.load('database')))

		dataframe = (await database.google_database.load(settings.GOOGLE_DATABASE_URL.get_secret_value()))

		queries = []
		answers = []

		for record in dataframe:

			queries.append(record[0])
			answers.append(record[0])


		responses, contexts, scores = await engine.assess(queries, answers)

		for record, response, context, score in zip(dataframe, responses, contexts, scores):

			record.append(response)
			record.append(json.dumps(context, ensure_ascii = False))
			record.append(json.dumps(score, ensure_ascii = False))

		await database.google_database.save(
			settings.GOOGLE_DATABASE_URL.get_secret_value(),
			dataframe
		)

	asyncio.run(main())