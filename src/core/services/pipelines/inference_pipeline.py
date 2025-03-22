import asyncio
import llama_index
import llama_index.llms.openai
import llama_index.agent.openai

class InferencePipeline():

	def __init__(self, model, data: dict, config: dict = {}):

		self.model = model
		self.data = data

		self.config = {
			'similarity_top': config.get('similarity_top', 1),
			'similarity_cutoff': config.get('similarity_cutoff', 0.75),
			'retrieve_hybrid_alpha': config.get('retrieve_hybrid_alpha', 0.25),
			'rerank_choice_batch_size': config.get('rerank_choice_batch_size', 5),
			'rerank_similarity_top': config.get('rerank_similarity_top', 1)
		}

		self.documents = None
		self.index = None
		self.retriever = None
		self.reranker = None
		self.engine = None
		self.pipeline = None

		asyncio.run(self.setup())

	async def setup(self):

		self.documents = [
			llama_index.core.Document(
				text = chunk.get('text', ''),
				metadata = {
					**chunk.get('metadata', {}), 
					'header': file['file_path']
				}
			)
			for file in self.data
			for chunk in file['chunks']
		]

		self.index = llama_index.core.VectorStoreIndex.from_documents(self.documents)

		self.retriever = self.index.as_retriever(
			similarity_top_k = self.config.get('similarity_top'),
			similarity_cutoff = self.config.get('similarity_cutoff'),
			alpha = self.config.get('retrieve_hybrid_alpha')
		)

		self.reranker = llama_index.core.postprocessor.llm_rerank.LLMRerank(
			choice_batch_size = self.config.get('rerank_choice_batch_size'),
			top_n = self.config.get('rerank_similarity_top'),
			llm = self.model
		)

		self.summarizer = llama_index.core.response_synthesizers.TreeSummarize(
			llm = self.model
		)

		metadata_postprocessor = llama_index.core.postprocessor.MetadataReplacementPostProcessor(target_metadata_key = 'window')
		similarity_postprocessor = llama_index.core.postprocessor.SimilarityPostprocessor(similarity_cutoff = self.config.get('similarity_cutoff'))
		self.engine = llama_index.core.query_engine.RetrieverQueryEngine(
			retriever = self.retriever,
			node_postprocessors = [
				similarity_postprocessor,
				metadata_postprocessor
			]
		)

		instruction_prompt = (
			'Using the provided context, generate a comprehensive and informative answer to the query:\n'
			'Query: {query}\n'
			'Context: {context}\n'
			'\n'
			'Guidelines for your response:\n'
			'1. If the context lacks information about the query, reply explicitly with: "There is no information on this topic."\n'
			'2. Your answer must focus exclusively on the given context and must not introduce unrelated information.\n'
			'3. Provide a detailed explanation that thoroughly addresses all aspects of the context relevant to the query.\n'
			'4. Use a structured format, ensuring the response is clear and concise.\n'
		)
		instruction_prompt_template = llama_index.core.PromptTemplate(instruction_prompt)

		self.pipeline = llama_index.core.query_pipeline.QueryPipeline(
			modules = {
				'retriever': self.retriever,
				'reranker': self.reranker,
				'summarizer': self.summarizer,
				'instruction': instruction_prompt_template,
				'model': self.model
			},
			verbose = True
		)

		self.pipeline.add_link('instruction', 'model')
		self.pipeline.add_link('model', 'retriever')
		self.pipeline.add_link('retriever', 'reranker', dest_key = 'nodes')
		self.pipeline.add_link('model', 'reranker', dest_key = 'query_str')
		self.pipeline.add_link('reranker', 'summarizer', dest_key = 'nodes')
		self.pipeline.add_link('model', 'summarizer', dest_key = 'query_str')

	async def process(self, query: str):

		retrieved_nodes = (await self.engine.aretrieve(query))
		retrieved_headers = [node.node.metadata.get('header', 'Untitled') for node in retrieved_nodes]
		retrieved_contexts = [node.node.text for node in retrieved_nodes]
		context = '\n'.join(retrieved_contexts)

		response = self.pipeline.run(
			context = context,
			query = query
		).response

		return response, retrieved_contexts, retrieved_headers
		
	async def retrieve_context(self, query: str):

		return await self.engine.aquery(query)