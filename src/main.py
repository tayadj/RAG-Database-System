import config
import core
import data

import asyncio
import ragas



if __name__ == '__main__':

	async def main():

		settings = config.Settings()
		database = data.Database(settings._GOOGLE_SERVICE_ACCOUNT(), settings.LOCAL_DATABASE_URL.get_secret_value())
		engine = core.service.Engine(settings.OPENAI_API_TOKEN.get_secret_value(), (await database.local_database.load('database')))

		evaluator_llm = ragas.llms.LlamaIndexLLMWrapper(engine.model)

		dataframe = (await database.google_database.load(settings.GOOGLE_DATABASE_URL.get_secret_value()))[:2]

		for record in dataframe:

			response = await engine.request(record[0])

			record.append(response)

		print(dataframe)

		# move to evaluator

		sample = ragas.dataset_schema.SingleTurnSample(
			user_input = dataframe[0][0],
			response = dataframe[0][1],
			reference = '',
			etrieved_contexts = [] # chunks contexts
		)

		factual_correctness_scorer = ragas.metrics._factual_correctness.FactualCorrectness(
			llm = evaluator_llm
		)
		noise_sensitivity_scorer = ragas.metrics.NoiseSensitivity(
			llm = evaluator_llm
		)

		print(await factual_correctness_scorer.single_turn_ascore(sample))
		print(await noise_sensitivity_scorer.single_turn_ascore(sample))

		await database.google_database.save(
			settings.GOOGLE_DATABASE_URL.get_secret_value(),
			dataframe
		)

	asyncio.run(main())