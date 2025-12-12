# Best_shops
### Project Name
    Best Shop
## Description
The goal of this project is to build a desktop application that helps users track grocery product information and monitor price changes. The system combines a graphical user interface with a MySQL database to provide fast product lookup, price comparison, and basic historical price analysis.

The application focuses on four core capabilities:

1. Display Consumer Price Index (CPI) Forecast Data

The Home tab displays official Consumer Price Index forecast data pulled from the database.
This gives users an overview of expected inflation trends for food-related categories.

2. Manage and Search Grocery Products

* Users can browse all products stored in the database with options to:
    search by product name,
    filter by category,
    view other product details,
    open historical price records for any item.

* This supports quick identification of items and easy database navigation.

3. Add New Products to the Database

* The system allows creation of new product entries, automatically handling cases where:
    the category does not exist yet (creates a new one),
    the brand does not exist yet (creates a new one)

* This ensures the product list remains expandable and consistently structured.

4. Record Store Prices and User Observations

* Users can submit real-world price entries for any product, specifying:
    store name,
    store location,
    observed price

* If a store does not exist in the database, it is automatically created.
* These observations populate the price_observation table and support future price_history.

5. View Historical Average Prices (price_history)

* The system can display historical national average prices stored in the database.
* This helps users compare their observed prices to long-term trends.

## Databases used
* bg_cpi_monthly        -> https://www.bls.gov/cpi/
* bg_price_history      -> https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset
* bg_usda_food_forecast -> https://www.ers.usda.gov/data-products/food-price-outlook

## E-R diagram
Find it in the file Best_Shop.drawio.pdf, open it using the draw.io software.