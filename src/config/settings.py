import base64
import json
import os
import pydantic
import pydantic_settings



class Settings(pydantic_settings.BaseSettings):
	
	model_config = pydantic_settings.SettingsConfigDict(
		env_file = os.path.dirname(__file__) + '/.env',
		env_file_encoding = 'utf-8',
		extra = 'ignore'
	)

	OPENAI_API_TOKEN: pydantic.SecretStr
	GOOGLE_SERVICE_ACCOUNT: pydantic.SecretStr
	GOOGLE_SERVICE_DATABASE_URL: pydantic.SecretStr

	def _GOOGLE_SERVICE_ACCOUNT(self):

		google_service_account = base64.b64decode(self.GOOGLE_SERVICE_ACCOUNT.get_secret_value())
		
		return json.loads(google_service_account)
		