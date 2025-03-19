import config

import asyncio

if __name__ == '__main__':

	async def main():

		settings = config.Settings()
		print(settings.GOOGLE_SERVICE.get_secret_value())

	asyncio.run(main())