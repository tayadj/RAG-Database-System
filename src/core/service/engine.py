import asyncio
import llama_index
import llama_index.llms.openai
import llama_index.agent.openai
import os

class Engine():

	# implement multi-thread, connection pool

	class RAGPipeline():

		# RAG Strategy 

		# Feel free to use statistical methods in order to enhance the metrics
		# No hallucinations

		pass

	def __init__(self, openai_api_token: str, RAG_data: dict):

		self.data = RAG_data
		self.index = None
		
		os.environ["OPENAI_API_KEY"] = openai_api_token
		self.model = llama_index.llms.openai.OpenAI (
			model = 'gpt-3.5-turbo'
		)

		self.setup_storage()

	# move datalake strategy to /data ?

	# rearrange data ingestion strategy to be universal

	def setup_storage(self):

		documents = [
			llama_index.core.Document(
				text = chunk.get('text',''),
				metadata = chunk.get('metadata',{})
			)
			for file in self.data
			for chunk in file['chunks']
		] 
		# use GPTVectorStoreIndex
		self.index = llama_index.core.VectorStoreIndex.from_documents(documents)

	async def request(self, query: str):

		# outtage database - ignore

		#resp = await self.model.acomplete("Paul Graham is ")
		#print(resp)

		query_engine = self.index.as_query_engine()
		response = query_engine.query(query)

		return response.response