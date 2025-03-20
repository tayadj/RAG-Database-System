import ragas
import json


class Assessment:

	def __init__(self, queries: dict, answers: dict, model):

		self.queries = queries
		self.answers = answers
		self.model = model
		
		# exceptions
		# queries and answers must be the same dimension

	def assess_factual_correctness(self):

		pass

	def assess_noise_sensitivity(self):

		pass
		