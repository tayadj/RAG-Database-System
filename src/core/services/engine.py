import asyncio
import llama_index
import llama_index.llms.openai
import llama_index.agent.openai
import os

import core.services.pipelines

class Engine():

	# implement multi-thread, connection pool

	def __init__(self, openai_api_token: str, RAG_data: dict):


		self.data = RAG_data
		self.index = None
		
		os.environ["OPENAI_API_KEY"] = openai_api_token
		self.model = llama_index.llms.openai.OpenAI (
			model = 'gpt-3.5-turbo'
		)

		self.setup_index()

		self.inference_pipeline = core.services.pipelines.InferencePipeline(self.model, self.index)
		self.assessment_pipeline = core.services.pipelines.AssessmentPipeline(self.model, self.inference_pipeline)

	# rearrange data ingestion strategy to be universal

	def setup_index(self):

		documents = [
			llama_index.core.Document(
				text = chunk.get('text',''),
				metadata = chunk.get('metadata',{})
			)
			for file in self.data
			for chunk in file['chunks']
		]
		self.index = llama_index.core.VectorStoreIndex.from_documents(documents)

	async def request(self, query: str):

		response, context = await self.inference_pipeline.process(query)
		
		return response, context

	async def assess(self, queries, answers):

		responses, contexts, scores = await self.assessment_pipeline.process(queries, answers)

		return responses, contexts, scores