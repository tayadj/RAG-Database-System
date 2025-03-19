import config
import core

import asyncio





if __name__ == '__main__':

	async def main():

		settings = config.Settings()
		engine = core.service.Engine(settings)

	asyncio.run(main())