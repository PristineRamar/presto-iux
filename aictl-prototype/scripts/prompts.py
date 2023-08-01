QUERY_SEED_SALES = "Show me sales and movement for Upper Respiratory for Q2."

PROMPT_SALES = """
Example
-------

User: Show me sales and movement for Upper Respiratory for Q2.
Observation: I need to call the Movement API for Upper Respiratory Quarter 2 sales and movement, and then display to user.
Thought: I need the location, but user did not specify it.
Action: Call Follow-Up Question API with {"type" = "location"}.
AI: For which location would you like to know?
User: The location is Zone 1000
Thought: User responded Zone 1000
Action: Call Movement API with {"product-name" = "Upper Respiratory", "quarter" = 2, "metrics" = ["sales", "movement"], "location-name" = "Zone 1000"}
Thought: I should use numerical format to display sales and movement
Action: Call Display API with {"type"="numeric", "data" = movement API response}

Based on the example given above, generate a conversation between user and ai. `the movement api requires product group, location and time period (weeks, months, year, quarter). Get these information from the user. Add thoughts and observations as well.
"""

QUERIES_SALES = """
What were the sales numbers in Zone 500 in Q3 of last year?
Can you give me the sales figures for Beauty products?
I need to see the movement of Electronics in Zone 250.
How much revenue was generated from Home Decor in Zone 750?
What was the sales performance in Zone 300 in Q4 of last year?
Can you provide me with the sales data in Zone 800 for the last six months?
What were the quarterly sales figures in Zone 400?
I want to see the sales numbers for Outdoor Gear in Zone 900.
Please give me the sales performance of Pet Supplies for Q2 and Q3 of last year.
What was the revenue generated in Zone 600?
"""

PROMPT_BUDGET_FORECAST = """"
Example
-------

User: What are the budget goals for Dairy for the current quarter? Are we projected to meet them or fall short?
Observation: I need to call the Budget API for Dairy current quarter, then call the Forecast API for the same, decide whether we fall short or not, and display results to user.
Thought: I need the location, but user did not specify it.
Action: Call Follow-Up Question API with {"type" = "location"}.
AI: Give me a location to proceed further.
User: Zone 1000
Thought: User responded Zone 1000
Action: Call Budget API with {"product-name" = "Dairy", "quarter" = "current", "location-name" = "Zone 1000"}
Action: Call Forecast API with {"product-name" = "Dairy", "quarter" = "current", "location-name" = "Zone 1000"}
Thought: Forecast exceeds budget for sales and movement, but not volume. I should display the numbers in a table, and also state my findings.
Action: Call Display API with {"type" = ["table", "text"], data = [Budget API Response + Forecast API response, "We are projected to meet the sales and movement goals, but fall short on margin."]}"

Based on the example given above, generate a conversation between user and ai.
The budget and forecast api's require product group, location and time period (weeks, months, year, quarter).
Get these information from the user. Add thoughts and observations as well.
"""

QUERIES_BUDGET_FORECAST = """What are the sales targets for Snacks in Zone 35 for the next quarter?
Can you tell me the budget goals for Frozen Foods for the entire year?
What is the projected revenue for Beverages in Zone 20 for the next six months?
How are we performing in terms of meeting the budget targets for Bakery products in the current quarter?
What are the financial goals for Meat and Poultry for the upcoming year?
Can you provide me with the budget projections for Produce in Zone 450 for the next quarter?
What is the expected revenue for Seafood in the current quarter across all locations?
What are the sales targets for Canned Goods for the next six months in Zone 710?
How are we tracking against the budget goals for Deli products for the first half of the year?
Can you give me an update on the revenue projections for Dairy in Zone 880 for the next three months?"""

PROMPT_KVI = """"
Examples
--------

User: Give me a list of of Primary KVIs under OTC Internal for Zone 42.
Observation: I need to call KVI API for OTC Internal Zone 42 Primary KVIs and display list to user.
Action: Call KVI API with {"product-name" = "OTC Internal", "location-name" = "Zone 42", type = "Primary"}
Action: Call Display API with {"type" = "list", data = KVI Response}"

User: Can you give me a list of Secondary KVIs for Pet Care in Zone 710?
Observation: I need to call KVI API for Zone 710 Secondary KVIs and display list to user.
Action: Call KVI API with {"product-name" = "Pet Care", "location-name" = "Zone 710", type = "Secondary"}
Action: Call Display API with {"type" = "list", data = KVI Response}"

User: Can you provide me with a list of the Top KVIs for Personal Care in Zone 35?
Observation: I need to call KVI API for Zone 35 Primary KVIs and display list to user
Action: Call KVI API with {"product-name" = "Personal Care", "location-name" = "Zone 35", type = "Primary"}
Action: Call Display API with {"type" = "list", data = KVI Response}"

Based on the examples given above, generate a conversation between user and ai.
The KVI API requires product name, location and type. Do not ask questions about information you already have.
Top KVI's = primary KVI's.
Add observations and actions as well.
"""

QUERIES_KVI = """What are the Secondary KVIs for Health and Wellness in Zone 15?
Can you provide me with a list of the Top KVIs for Personal Care in Zone 35?
Give me the Primary KVIs for Baby Products in Zone 20.
What are the Top KVIs for Household Supplies in Zone 85?
Can you give me a list of Secondary KVIs for Pet Care in Zone 710?
What are the Primary KVIs for Beauty and Cosmetics in Zone 450?
Provide me with the Top KVIs for Toys and Games in Zone 880.
What are the Secondary KVIs for Office Supplies in Zone 690?
Give me the Primary KVIs for Snacks and Confectionery in Zone 42.
Can you provide me with a list of Top KVIs for Home Appliances in Zone 260?"""

PROMPT_COST_CHANGE = """
Example
-------

User: Show me all items which had a cost change in the last three weeks.
Observation: I need to call Cost API for the last four weeks, filter for items that underwent a change, and then display the list to user.
Thought: I need the product group, but user did not specify it.
Action: Call Follow-Up Question API with {"type" = "product"}.
AI: Which product group are you interested in?
User: I'm interested in Grocery
Thought: User responded Grocery.
Action: Call Cost API with {"product-name" = "Grocery", week = "last 4", change = "Y"}
Action: Call Display API with {"type" = "list", data = Cost API Response}

Based on the example given above, generate a conversation between user and ai.
The Cost API requires product name, location and type. Do not ask questions about information you already have.
Add thoughts, observations, and actions as well."""

QUERIES_COST_CHANGE = """What are the products that have had a price change in the last two weeks for Snacks in Zone 15?
Can you give me a list of all items with a cost change in the last month for Beauty and Cosmetics in Zone 35?
Show me the products with a price change in the last week for Beverages in Zone 20.
What are the items with a cost change in the last three weeks for Toys and Games in Zone 450?
Can you provide me with a list of all products with a price change in the last four weeks for Frozen Foods in Zone 35?
Show me all items with a cost change in the last two weeks for Home Appliances in Zone 880.
What are the products that have had a price change in the last week for Meat and Poultry in Zone 450?
Provide me with a list of all items with a cost change in the last month for Personal Care in Zone 15.
Show me the products with a price change in the last three weeks for Office Supplies in Zone 690.
What are the items with a cost change in the last five days for Canned Goods in Zone 260?"""


PROMPT_SALES_COMPARISON = """
Examples
--------

User: Show me a year-over-year comparison of Zone 1000 Eye/Ear Care sales.
Observation: I need to get sales for Eye/Ear Care Zone 1000 for this year and last year using Movement API, and display both to user.
Action: Call Movement API with {"product-name" = "Eye/Ear Care", "location-name" = "Zone 1000", year = "last 1", "location-aggregate-level" = "week"}
Action: Call Movement API with {"product-name" = "Eye/Ear Care", "location-name" = "Zone 1000", year = "current", "location-aggregate-level" = "week"}
Action: Call Display API with {"type" = "line graph", "data" = [Movement API Response 1, Movement API Response 2]}

User: Provide me with a comparison of Snacks and Confectionery sales over the last two years.
Observation: I need to get sales for Snacks and Confectionery for the last two years using Movement API, and display both to user.
Observation: Location is missing
Thought: Ask user a follow up questions to get the location
AI: Which location are you interested in?
User: Zone 150
Thought: I need to get sales for Snacks and Confectionery at Zone 150 for the last two years using Movement API, and display both to user.
Action: Call Movement API with {"product-name" = "Snacks and Confectionery", "location-name" = "Zone 150", year = "last 2", "location-aggregate-level" = "week"}
Action: Call Movement API with {"product-name" = "Snacks and Confectionery", "location-name" = "Zone 150", year = "current", "location-aggregate-level" = "week"}
Action: Call Display API with {"type" = "line graph", "data" = [Movement API Response 1, Movement API Response 2]}
AI: Sure, here is a comparison of Snacks and Confectionery sales for Zone 150 over the last two years. [Displays line graph]


Based on the examples given above, generate a conversation between user and ai.
The Movement API requires product name, location, and year. Do not ask questions about information you already have.
Add observations and actions as well."""

QUERIES_SALES_COMPARISON = """Give me a comparison of Eye/Ear Care sales for Zone 1000 this year versus last year.
Can you show me the YoY change in sales of Beauty and Cosmetics?
Provide me with a comparison of Snacks and Confectionery sales for Zone 150 over the last two years.
Show me the percentage change in sales in Zone 250 over the last 12 months.
Give me a comparison of sales for Personal Care products in Zone 750 for the current quarter and the same quarter last year.
What is the change in sales of Household Supplies in Zone 350?
Can you show me a comparison of Meat and Poultry sales for Zone 550 this month versus last month?
Provide me with the YoY change in sales for Dairy products.
Show me the percentage change in sales of Baby Care products in Zone 450 over the last six months.
Give me a comparison of sales for Zone 650 this quarter versus the same quarter two years ago.
Show me a comparison of Zone 1000 Eye/Ear Care sales from this year and the previous year.
Provide me with a year-to-year comparison of sales for Snacks and Confectionery"""


PROMPT_OFFERS = """
Example:
-------

User: Which items are planned to be on BOGO in the coming week? Of these, which are on page 1 of the ad?
Observation: Need to use Promo API to find all items on BOGO during the coming week, filter for those on page 1 of the ad, and display list to user.
Thought: I need the product group, but user did not specify it.
Action: Call Follow-Up Question API with {"type" = "product"}.
AI: Which product would you like to know about?
User: Vitamins
Thought: User responded Vitamins.
Thought: I need the location, but user did not specify it.
Action: Call Follow-Up Question API with {"type" = "location"}.
Thought: User responded Zone 33.
Action: Call Promo API with {"product-name" = "Vitamins", "location-name" = "Zone 33", "week" = "next 1", "type" = "BOGO", "page-no" = 1}
Action Call Display API with {"type" = "list", "data" = Promo API Response}

Based on the examples given above, generate a conversation between user and ai.
The Promo API requires product name, week, page number, and type.
Ask user for missing information. Do not ask questions about information you already have.
Add observations, thoughts, and actions as well."""

QUERIES_OFFERS = """Can you give me a list of upcoming items with a BOGO offer? Which of these items are on page 1 of the ad in Zone 1000?
Which products are planned to have a Buy One Get One Half Off offer in the next week?
Give me a list of items that will be on sale in the coming week. Which of these items are on the front page of the ad?
What are the upcoming products with a BOGO Free offer? Which of these products are available in Zone 500?
Which items will be part of a Buy 2 Get 1 Free offer in the next few days?
Can you provide me with a list of products planned to be on sale next week? Which of these items are in the Home category?
What products will be part of a 20% off promotion in the coming days? Are any of these products available in Zone 250?
Which products are planned to have a BOGO 50% off offer in the next week? Are any of these products available in Zone 750?
What are the upcoming products with a Buy 3 Get 1 Free offer? Which of these products are in the Electronics category?
Can you give me a list of items that will be on sale in the coming week? Which of these items are on the back page of the ad?
Which products will be part of a Buy One Get One Free offer in the next few days? Are any of these products available in Zone 200?
Give me a list of upcoming items with a BOGO 25% off offer. Which of these items are in the Toys category?
What products will be part of a 30% off promotion in the coming days? Are any of these products available in Zone 450?
Which items are planned to be on sale next week? Are any of these items on the endcaps?
Can you provide me with a list of products planned to be part of a Buy 2 Get 2 Free offer in the next few days? Which of these products are available in Zone 800?
What are the upcoming products with a Buy One Get One 25% off offer? Which of these products are in the Health and Beauty category?
Give me a list of items that will be part of a 10 for $10 promotion in the coming week. Which of these items are on the side panels of the ad?"""

QUERIES_PRICE_CHANGE = """Show me the KVIs with scheduled price changes for Zone 200 in the next 3 weeks.
Which KVIs for Beauty products have a price change scheduled in the next 2 weeks?
What are the KVIs for Zone 500 which have a scheduled price change in the coming month?
Show me the list of KVIs in Snacks category with scheduled price changes in the next 4 weeks.
What KVIs in Pet Supplies are scheduled for a price change in the next 2 weeks?
Give me the details of the KVIs in Dairy products that are scheduled for price change in the next 3 weeks.
Which KVIs for Beverages have scheduled price changes in the next 4 weeks?
Show me the KVIs in Meat category with scheduled price changes in the next month.
What are the KVIs for Baby Care products which have a price change scheduled in the coming 2 weeks?
Give me the details of the KVIs in Home Essentials that have scheduled price changes in the next 4 weeks."""

PROMPT_PRICE_CHANGE = """
Example:
-------
User: Which KVIs are have a scheduled price change in the next 4 weeks?
Thought: I need to call the KVI API, then take the list of KVIs and call the Price API for the next 4 weeks, then filter for those items which have a price change during that time, then display the results to the user.
Thought: I need the product group, but user did not specify it.
Action: Call Follow-Up Question API with {"type" = "product"}.
AI: I need a product group.
User: Center Store
Thought: User responded Center Store.
Thought: I need the location, but user did not specify it.
Action: Call Follow-Up Question API with {"type" = "location"}.
Thought: User responded Midwest.
Action: Call KVI API with {"product-name" = "Center Store", "location-name" = "Midwest"}
Action: Call Price API with {"item-list" = KVI API Response, "location-name" = "Midwest", week = "next 4", change = "Y"}
Action: Call Display API with {type = "list", data = Price API Response}

Based on the example given above, generate a conversation between user and ai.
The KVI API requires product name, and location. 
The Price API requires the response of KVI API, location, and week.
Ask user for missing information. Do not ask questions about information you already have.
Add thoughts and actions as well."""

PROMPT_PROMO = """
Examples:
--------

User: Show me the two most effective promotions.
Thought: I need to call Promo Analysis API for the given item, filter for the top two most effective promotions, and display results to the user.
Action: Call Promo Analysis API with {"product-name" = all, "top" = 2}
Action: Call Display API with {"type" = "table", "data" = Promo Analysis API Response

User: What are the most effective promotions for Zone 1000 Pet Care in the last quarter?
Thought: I need to call Promo Analysis API for the given item, filter for the top three most effective promotions, and display results to the user.
Action: Call Promo Analysis API with {"product-name" = "Pet Care", "top" = 3}
Action: Call Display API with {"type" = "table", "data" = Promo Analysis API Response

Based on the examples given above, generate a conversation between user and ai.
The Promo Analysis API requires product name, and top parameters. Top refers to top n effective promotions. 
Ask user for missing information. Do not ask questions about information you already have.
Add thoughts and actions as well.
"""

QUERIES_PROMO = """What are the most effective promotions for the Beauty category in the last 3 months?
Give me the top two promotions for Zone 500 Beverages in the last week.
Which are the most successful promotions for the Electronics category in Q2?
What are the top two promotions for Zone 750 Health & Wellness in the current month?
Show me the most effective promotions for the Home & Garden category in the last year.
Which promotions have worked best for the Toys & Games category in Zone 250 in the last 6 months?
Give me the top two promotions for the Snacks category in the current week.
What are the most effective promotions for Zone 1000 Pet Care in the last quarter?
Which promotions have shown the best results for the Cleaning Supplies category in the last 2 months?
Show me the two most successful promotions for the Baby Care category in the current month."""

PROMPT_PRICE_COMPARISON = """
Example:
-------
User: How does our current price position in Frozen Food compare to Walmart?
Thought: I need to call the Price Index API for Frozen Food and Walmart and then display the result to the user.
Thought: I need the location, but user did not specify it.
Action: Call Follow-Up Question API with {"type" = "location"}.
AI: For which location?
User: New England
Thought: User responded New England.
Action: Call Price Index API with {"product-name" = "Frozen Food", "location-name" = "New England", "competitor-name" = "Walmart"}
Action: Call Display API with {"type"="numeric", "data" = Price Index API Response}

Based on the examples given above, generate a conversation between user and ai.
The Price Index API requires product name, location, and competitor name.
Ask user for missing information. Do not ask questions about information you already have.
Add thoughts and actions as well."""

QUERIES_PRICE_COMPARISON = """How does our current price position in Fresh Produce compare to Costco?
What is the average price of Cereal in Zone 25 compared to Target?
Is our price for Avocados competitive in the West Coast region compared to Safeway?
What is the price difference between our store and Publix for Diapers in the last 2 weeks?
How does our price for Ice Cream in Zone 50 compare to Kroger?
What is our price position for Bread in the Northeast region compared to ShopRite?
Is our price for Soda in Zone 10 lower or higher than Albertsons?
How does our current price for Snacks compare to Meijer in the Midwest?
What is the average price of Ground Beef in Zone 75 compared to Whole Foods?
Is our price for Chips competitive in the South region compared to H-E-B?
Compare our current price position in Household Cleaning products to Target.
How do our prices for Snacks compare to Kroger in the last month?
What is the price difference for Beverages between us and Safeway?
Show me a comparison of our prices for Fresh Produce with Wegmans for the past week.
How does our pricing strategy for Meat compare to Costco's over the past year?
Compare our price position for Bakery items with Aldi for the next month.
What is the difference in price for Health & Beauty products between us and Walgreens in Zone 500?
How does our current price position for Pet Food compare to Petco?
Show me the comparison of our prices for Electronics with Best Buy in the last quarter.
Compare our price position for Toys and Games with Toys R Us in Zone 42."""
