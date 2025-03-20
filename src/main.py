import config
import core
import data

import asyncio
import ragas
import json



if __name__ == '__main__':

	async def main():

		settings = config.Settings()
		database = data.Database(settings._GOOGLE_SERVICE_ACCOUNT(), settings.LOCAL_DATABASE_URL.get_secret_value())
		engine = core.services.Engine(settings.OPENAI_API_TOKEN.get_secret_value(), (await database.local_database.load('database')))

		# assessment = core.services.Assessment()
		# move to assessment

		evaluator_llm = ragas.llms.LlamaIndexLLMWrapper(engine.model)

		dataframe = (await database.google_database.load(settings.GOOGLE_DATABASE_URL.get_secret_value()))[:2]

		for record in dataframe:

			response, context = await engine.request(record[0])

			sample = ragas.dataset_schema.SingleTurnSample(
				user_input = record[0],
				response = response,
				reference = record[1],
				retrieved_contexts = context
			)

			factual_correctness_scorer = ragas.metrics._factual_correctness.FactualCorrectness(
				llm = evaluator_llm
			)
			noise_sensitivity_scorer = ragas.metrics.NoiseSensitivity(
				llm = evaluator_llm
			)

			scores = {
				'factual_correctness' : (await factual_correctness_scorer.single_turn_ascore(sample)),
				'noise_sensitivity': (await noise_sensitivity_scorer.single_turn_ascore(sample))
			}

			record.append(response)
			record.append(json.dumps(context, ensure_ascii = False))
			record.append(json.dumps(scores, ensure_ascii = False))

		
		await database.google_database.save(
			settings.GOOGLE_DATABASE_URL.get_secret_value(),
			dataframe
		)

	asyncio.run(main())