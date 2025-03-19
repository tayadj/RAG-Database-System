import asyncio
import llama_index
import llama_index.llms.openai

class Engine():

	class RAGPipeline():

		# RAG Strategy 
		pass

	def __init__(self, openai_api_token: str):

		self.openai_api_token = openai_api_token
		self.model = llama_index.llms.openai.OpenAI (
			model = 'gpt-3.5-turbo',
			api_key = openai_api_token
		)

	def request(self, query: str):

		pass