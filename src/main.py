import config
import core
import data

import asyncio
import ragas



if __name__ == '__main__':

	async def main():

		settings = config.Settings()
		database = data.Database(settings._GOOGLE_SERVICE_ACCOUNT(), settings.LOCAL_DATABASE_URL.get_secret_value())
		engine = core.service.Engine(settings.OPENAI_API_TOKEN.get_secret_value(), (await database.local_database.load('database')))

		evaluator_llm = ragas.llms.LlamaIndexLLMWrapper(engine.model)

		dataframe = (await database.google_database.load(settings.GOOGLE_DATABASE_URL.get_secret_value()))[:2]

		for record in dataframe:

			response = await engine.request(record[0])

			record.append(response)

		print(dataframe)

		# move to evaluator

		sample = ragas.dataset_schema.SingleTurnSample(
			user_input = dataframe[0][0],
			response = dataframe[0][1],
			reference = '''"To better manage your stock and avoid running out of popular items, consider the following strategies based on the inventory management principles presented in the available material:

1. **Track Inventory Regularly**:
   - Implement a system to keep accurate records of inventory levels, which can help identify when items are running low and need to be reordered.

2. **Use ABC Analysis**:
   - Classify products into categories (A, B, and C) based on their sales volume and significance to your business. Focus more on managing items in category A, which contribute the most to revenue.

3. **Set Minimum Inventory Levels**:
   - Establish reorder points to ensure you have sufficient stock on hand before it runs out. Keeping a buffer stock of a few extra units can help mitigate shortages during peak demand.

4. **Utilize Inventory Management Systems**:
   - Invest in computer or mobile-based inventory applications that offer real-time tracking and alerts for low stock levels.

5. **Plan for Demand Forecasting**:
   - Estimate stock requirements based on previous sales data and potential seasonal fluctuations. Consider creating an annual production plan to align inventory levels with expected sales.

6. **Rotate Stock Effectively**:
   - Implement stock rotation methods (FIFO - First In First Out) to ensure older stock is sold first, particularly for perishable items.

7. **Regularly Count Inventory**:
   - Perform inventory counts frequently to reconcile physical stock against records, helping to identify discrepancies or trends in sales.

8. **Communicate with Suppliers**:
   - Maintain good relationships with suppliers to improve the reliability of deliveries and negotiate favorable terms for restocking.

By applying these strategies, you can enhance your inventory management practices and significantly reduce the risk of running out of popular items."''', # ground_truth
			retrieved_contexts = [] # chunks contexts
		)

		factual_correctness_scorer = ragas.metrics._factual_correctness.FactualCorrectness(
			llm = evaluator_llm
		)
		noise_sensitivity_scorer = ragas.metrics.NoiseSensitivity(
			llm = evaluator_llm
		)

		print(await factual_correctness_scorer.single_turn_ascore(sample))
		print(await noise_sensitivity_scorer.single_turn_ascore(sample))

		await database.google_database.save(
			settings.GOOGLE_DATABASE_URL.get_secret_value(),
			dataframe
		)

	asyncio.run(main())