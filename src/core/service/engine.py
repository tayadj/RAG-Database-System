import asyncio
import llama_index
import llama_index.llms.openai

class Engine():

	# implement multi-thread

	class RAGPipeline():

		

		# RAG Strategy 
		pass

	def __init__(self, openai_api_token: str, RAG_data: dict):

		self.data = RAG_data
		self.index = None

		
		self.openai_api_token = openai_api_token
		self.model = llama_index.llms.openai.OpenAI (
			model = 'gpt-3.5-turbo',
			api_key = openai_api_token
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

		self.index = llama_index.core.GPTVectorStoreIndex.from_documents(documents)

	def request(self, query: str):

		pass