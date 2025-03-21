import asyncio
import llama_index
import llama_index.llms.openai
import llama_index.agent.openai
import os

import core.services.pipelines



class Engine():

	def __init__(self, openai_api_token: str, data: dict):

		os.environ["OPENAI_API_KEY"] = openai_api_token		

		self.data = data		
		self.model = llama_index.llms.openai.OpenAI(model = 'gpt-3.5-turbo')

		self.inference_pipeline = core.services.pipelines.InferencePipeline(self.model, self.data)
		self.assessment_pipeline = core.services.pipelines.AssessmentPipeline(self.model, self.inference_pipeline)

	async def request(self, query: str):

		response, _ = await self.inference_pipeline.process(query)
		
		return response

	async def assess(self, queries, answers):

		responses, contexts, scores = await self.assessment_pipeline.process(queries, answers)

		return responses, contexts, scores