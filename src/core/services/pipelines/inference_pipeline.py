import asyncio
import llama_index
import llama_index.llms.openai
import llama_index.agent.openai



class InferencePipeline():

	# implement anchor for no-context i.e. when there's no information about the question in our index

	def __init__(self, model, index, config = {}):

		self.model = model
		self.index = index
		self.engine = None

	async def process(self, query: str):

		if self.engine is None:

			self.engine = await self.retrieve_query_engine(self.index)

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

		return response, [context] # case if context is str

	async def retrieve_context(self, query):

		return await self.engine.aquery(query)

	async def retrieve_query_engine(self, index: llama_index.core.VectorStoreIndex, similarity_top: int = 5):

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
