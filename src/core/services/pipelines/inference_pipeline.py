import asyncio
import llama_index
import llama_index.llms.openai
import llama_index.agent.openai



class InferencePipeline():

	def __init__(self, model, data: dict, config: dict = {}):

		self.model = model
		self.data = data

		self.config = {
			'similarity_top': config.get('similarity_top', 5)
		}

		self.documents = None
		self.index = None
		self.retriever = None
		self.engine = None

		asyncio.run(self.setup())

	async def setup(self):

		await self.setup_documents()
		await self.setup_index()
		await self.setup_retriever()
		await self.setup_engine()

	async def setup_documents(self):

		self.documents = [
			llama_index.core.Document(
				text = chunk.get('text',''),
				metadata = chunk.get('metadata',{})
			)
			for file in self.data
			for chunk in file['chunks']
		]

	async def setup_index(self):

		self.index = llama_index.core.VectorStoreIndex.from_documents(self.documents)

	async def setup_retriever(self):

		self.retriever = self.index.as_retriever()

	async def setup_engine(self):

		metadata_postprocessor = llama_index.core.postprocessor.MetadataReplacementPostProcessor(
			target_metadata_key = 'window'
		)

		self.engine = llama_index.core.query_engine.RetrieverQueryEngine(
			retriever = self.retriever,
			node_postprocessors = [
				metadata_postprocessor
			]
		)

		'''
		self.engine = self.index.as_query_engine(
			similarity_top_k = self.config.get('similarity_top'),
			node_postprocessors = [
				metadata_postprocessor
			]
		)
		'''

	async def process(self, query: str):

		"""

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



		"""

		retrieved_nodes = (await self.retriever.aretrieve(query))
		retrieved_contexts = [node.node.text for node in retrieved_nodes]
		context = ' '.join(retrieved_contexts)

		prompt = f'''
		Using the provided context, generate a comprehensive and informative answer to the query:
		Query: {query}
		Context: {context}

		Guidelines for your response:
		1. Your answer must focus exclusively on the given context and must not introduce unrelated information.
		2. Provide a detailed explanation that thoroughly addresses all aspects of the context relevant to the query.
		3. Use a structured format, ensuring the response is clear and concise.
		4. Enhance the response by finding meaningful connections within the context where applicable.
		5. If the context lacks information about the query, reply explicitly with: "There is no information on this topic."
		'''

		response = (await self.model.acomplete(prompt)).text

		return response, retrieved_contexts
		
	async def retrieve_context(self, query: str):

		return await self.engine.aquery(query)
