import asyncio
import llama_index
import llama_index.llms.openai
import llama_index.agent.openai


'''
	def setup_index(self):

		'''



class InferencePipeline():

	def __init__(self, model, data, config = {}):

		self.model = model
		self.data = data
		self.config = config

		self.documents = None
		self.index = None
		self.engine = None

		asyncio.run(self.setup())

	async def setup(self):

		await self.retrieve_documents()
		await self.retrieve_index()
		await self.retrieve_query_engine()

	async def process(self, query: str):

		context = (await self.retrieve_context(query)).response
		
		prompt = f'''
		Generate a detailed response for the query asked based only on the context fetched:
		Query: {query}
		Context: {context}

		Instructions:
		1. Show only your generated response based on context.
		2. Your response should be detailed and should cover every aspect of the context.
		3. Be crisp and concise.
		4. Try to find correlated information based on context and enhance your response using it.
		5. In case you haven't found any information from context, your response must be "There is no information on this topic."
		'''

		response = (await self.model.acomplete(prompt)).text

		return response, [context] 
		
	async def retrieve_context(self, query):

		return await self.engine.aquery(query)
		
	async def retrieve_documents(self):

		self.documents = [
			llama_index.core.Document(
				text = chunk.get('text',''),
				metadata = chunk.get('metadata',{})
			)
			for file in self.data
			for chunk in file['chunks']
		]

	async def retrieve_index(self):

		self.index = llama_index.core.VectorStoreIndex.from_documents(self.documents)

	async def retrieve_query_engine(self):

		postprocessor = llama_index.core.postprocessor.MetadataReplacementPostProcessor(
			target_metadata_key = 'window'
		)

		self.engine = self.index.as_query_engine(
			similarity_top_k = self.config.get('similarity_top', 5),
			node_postprocessors = [
				postprocessor
			]
		)
