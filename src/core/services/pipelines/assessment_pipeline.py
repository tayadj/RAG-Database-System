import ragas
import json



class AssessmentPipeline():

	def __init__(self, model, inference_pipeline):

		self.model = model
		self.evaluator = ragas.llms.LlamaIndexLLMWrapper(self.model)

		self.inference_pipeline = inference_pipeline

		self.factual_correctness_scorer = ragas.metrics._factual_correctness.FactualCorrectness(llm = self.evaluator)
		self.noise_sensitivity_scorer = ragas.metrics.NoiseSensitivity(llm = self.evaluator)

	async def process(self, queries, answers):

		responses = []
		headers = []
		scores = []

		for query, answer in zip(queries, answers):

			response, context, header = await self.inference_pipeline.process(query)

			responses.append(response)
			headers.append(header)

			sample = ragas.dataset_schema.SingleTurnSample(
				user_input = query,
				response = response,
				reference = answer,
				retrieved_contexts = context
			)

			score = {
				'factual_correctness' : (await self.factual_correctness_scorer.single_turn_ascore(sample)),
				'noise_sensitivity': (await self.noise_sensitivity_scorer.single_turn_ascore(sample))
			}

			print(f"Sample: {sample}, header: {header}, query: {query}, score: {score}")

			scores.append(score)

		return responses, headers, scores
		