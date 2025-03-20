import ragas
import json



class AssessmentPipeline():

	def __init__(self, queries: dict, answers: dict, model):

		self.queries = queries
		self.answers = answers
		self.model = model
		
		# exceptions
		# queries and answers must be the same dimension

	def process(self):

		pass
		