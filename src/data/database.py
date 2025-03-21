import data.connectors



class Database:

	def __init__(self, google_service_account: dict, local_storage_path: str):

		self.google_service_account = google_service_account
		self.local_database_path = local_database_path

		self.google_connector = data.connectors.GoogleConnector(self.google_service_account)
		self.local_connector = data.connectors.LocalConnector(self.local_storage_path)