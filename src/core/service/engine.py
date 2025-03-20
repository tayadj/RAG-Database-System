import asyncio
import llama_index
import llama_index.llms.openai
import llama_index.agent.openai
import os

class Engine():

	# implement multi-thread, connection pool

	class RAGPipeline:

		@staticmethod
		async def response(query: str, context, model):
			
			prompt = f'''
			Generate a detailed response for the query asked based only on the context fetched:
            Query: {query}
            Context: {context}

            Instructions:
            1. Show only your generated response based on context.
            2. Your response should be detailed and should cover every aspect of the context.
            3. Be crisp and concise.
            4. Try to find correlated information based on context and enhance your response using it.
            '''

			response = await model.acomplete(prompt)

			return response

		@staticmethod
		async def retrieve_context(engine, query):

			return engine.query(query)

		@staticmethod
		async def retrieve_query_engine(index: llama_index.core.VectorStoreIndex, similarity_top: int = 5):

			postprocessor = llama_index.core.postprocessor.MetadataReplacementPostProcessor(
				target_metadata_key = 'window'
			)

			engine = index.as_query_engine(
				similarity_top_k = similarity_top,
				node_postprocessors = [
					postprocessor
				]
			)

			return engine

	def __init__(self, openai_api_token: str, RAG_data: dict):

		self.data = RAG_data
		self.index = None
		
		os.environ["OPENAI_API_KEY"] = openai_api_token
		self.model = llama_index.llms.openai.OpenAI (
			model = 'gpt-3.5-turbo'
		)

		self.setup_index()

	# move datalake strategy to /data ?

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
		# use GPTVectorStoreIndex
		self.index = llama_index.core.VectorStoreIndex.from_documents(documents)

	async def request(self, query: str):

		query_engine = await self.RAGPipeline.retrieve_query_engine(self.index)
		context = await self.RAGPipeline.retrieve_context(query_engine, query)
		response = await self.RAGPipeline.response(query, context, self.model)
		
		return response