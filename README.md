# DSA_Python

Key Performance Indicators
• Gross Sales: PHP 5,368,956.93
• Fulfilled Orders: 11,439
• Average Order Value: PHP 434.35
• Top Category: Toys
• Net Sales after Order Discounts: PHP 4,968,543.75
• Customer Count: 22,571 Repeat vs. 4,506 New

Insights and Recommendations
• Insight 1: monthly gross sales fluctuated significantly from January 2024 to January 2026, peaking at approximately PHP 239,000 in August 2025 before declining to around PHP 200,000 by January 2026, which suggests inconsistent sales performance and a weakening trend toward the end of the period. 
• Recommendation 1: analyze the factors behind peak-sales months and replicate successful strategies such as effective promotions or seasonal campaigns – while investigating the late-2025 decline; moreover, implement targeted marketing and sales initiatives to stabilize monthly revenue and sustain growth.
• Insight 2: Toys generate the highest gross sales at approximately PHP 740,000, followed by Electronics at PHP 720,000; Sports has the lowest sales at around PHP 570,000, indicating differences in customer demand across product categories.
• Recommendation 2: prioritize inventory and marketing for high-performing categories like Toys and Electronics to sustain revenue – while reviewing the performance of Sports and other lower-selling categories to identify opportunities for improvement through targeted promotions and product assortment adjustments.
• Insight 3: Central Luzon generates the highest gross sales at approximately PHP 950,000, followed by Central Visayas at PHP 925,000; CALABARZON records the lowest sales at around PHP 830,000, indicating opportunities to improve regional performance.
• Recommendation 3: maintain strong sales strategies in Central Luzon and Central Visayas – while investigating the factors behind CALABARZON’s lower sales; moreover, implement targeted regional promotions and strengthen distribution efforts to increase revenue and reduce performance gaps across regions.
• Insight 4: order values are heavily concentrated below PHP 500, with the highest frequency around PHP 200–300; the distribution is right-skewed, meaning high-value orders are relatively rare.
• Recommendation 4: focus on increasing average order value through targeted upselling, product bundles, and free-shipping incentives for orders above PHP 500 – while maintaining affordable options that appeal to the majority of customers.
• Insight 5: the Web channel generates the highest gross sales, whereas the Marketplace has the lowest; however, sales across all three channels are relatively similar at approximately PHP 1.75–1.80 million.
• Recommendation 5: maintain strong performance across all channels – while analyzing the Web channel’s successful strategies and applying them to the Marketplace to help close the sales gap and increase overall revenue.
• Insight 6: monthly returns fluctuate significantly, ranging from approximately 67 to 119 — with notable peaks in June 2024, November 2024, and July 2025; despite these spikes, returns declined toward the end of 2025 before recovering in January 2026.
• Recommendation 6: investigate the factors driving peak-return months and the sharp declines, then use these insights to develop targeted strategies to stabilize monthly returns and replicate successful performance patterns.
• Insight 7: KidJoy Toys 607 is the top-selling product by gross sales, significantly outperforming the other products, whereas BookNest Groceries 219 ranks lowest among the top 10; this indicates stronger sales performance in certain product categories, particularly toys.
• Recommendation 7: prioritize inventory and marketing for high-performing products like KidJoy Toys 607 to sustain sales momentum – while reviewing the pricing, promotions, and customer demand for lower-performing products to identify opportunities for improvement.

Summary and Conclusions
• Toys emerged as the leading product category, with KidJoy Toys 607 achieving the highest product sales, whereas Sports recorded the lowest category sales.
• Geographically, Central Luzon performed best, whereas CALABARZON offers opportunities for improvement.
• The Web channel generated the highest gross sales, although sales across all channels remained relatively balanced.
• Most orders were valued below PHP 500, suggesting that the business primarily serves budget-conscious customers.
• Monthly sales fluctuated considerably, reaching a peak in August 2025 before declining toward January 2026, whereas product returns also varied throughout the period.
• Customer data shows a strong repeat-customer base, indicating potential customer loyalty and opportunities to attract new buyers.
• Overall, the business demonstrates solid sales performance and a strong repeat-customer base; however, declining recent sales, fluctuating returns, and uneven category and regional performance highlight the need for targeted marketing, improved customer acquisition, effective return management, and strategies to increase average order value and sustain long-term growth.

About This Dashboard
• This dashboard uses the original retail CSV files.
• The application performs basic cleaning before analysis:
•• removes exact duplicate records
•• standardizes product categories
•• converts unit prices to numeric values
•• removes zero or negative quantities
•• parses mixed order-date formats
•• fills missing discounts with zero
•• validates customer, order, and product references
•• keeps completed and shipped orders for sales analysis
• Gross Sales = Quantity × Unit Price
• Net Sales = Gross Sales × (1 − Discount Percentage)
• The average order value is calculated at the order level, not at the order-item level.
• Filtered item rows: 27,077
• Filtered unique orders: 11,439

Capstone Project
• app.py
• app.txt
• Day01_Python.ipynb
• Day02_Python.ipynb
• Day03_Python.ipynb
• Day04_Python.ipynb
• Day05_Python.ipynb
• Days01–06_Python.ipynb
• _order_summary_day5.csv
• _sales_analysis_day5.csv
• customers.csv
• customers_clean.csv
• order_items.csv
• orders.csv
• orders_clean.csv
• payments.csv
• products.csv
• products_clean.csv
• returns.csv
• sales_analysis.csv
• shipments.csv
• -gross-sales-by-product-category.png
• gross-sales-by-region.png
• gross-sales-by-sales-channel.png
• monthly-gross-sales.png
• monthly-return-count.png
• order-value-distribution.png
• top-10-products-by-gross-sales.png
• GitHub Repository Link: https://github.com/allyster-endozo/DSA_Python



