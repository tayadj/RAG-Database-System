import config
import core
import data

import asyncio
import json



if __name__ == '__main__':

	async def main():

		settings = config.Settings()
		database = data.Database(settings._GOOGLE_SERVICE_ACCOUNT(), settings.LOCAL_DATABASE_URL.get_secret_value())
		engine = core.services.Engine(settings.OPENAI_API_TOKEN.get_secret_value(), (await database.local_connector.load('database')))

		dataframe = (await database.google_connector.load(settings.GOOGLE_DATABASE_URL.get_secret_value()))
		queries, answers = zip(*[(record[0], record[1]) for record in dataframe])

		tasks = [engine.assess([query],[answer]) for query, answer in zip(queries, answers)]
		results = await asyncio.gather(*tasks)

		for record, result in zip(dataframe, results):

			responses, headers, scores = result
			record.append(responses[0])
			record.append(json.dumps(headers[0], ensure_ascii=False))
			record.append(json.dumps(scores[0], ensure_ascii=False))

		await database.google_connector.save(
			settings.GOOGLE_DATABASE_URL.get_secret_value(),
			dataframe
		)

	asyncio.run(main())