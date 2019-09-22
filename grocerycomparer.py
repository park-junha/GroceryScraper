from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
import urllib.request
import time
import json
# from bs4 import BeautifulSoup

app = Flask(__name__)

# Initialize data structures for json data
responses = []
storenames = []
index = 0

with open('api_urls.json', 'r') as api_f:
    apiurls_dict = json.load(api_f)

for apiurl in apiurls_dict:
    responses.append('')
    storenames.append('')
    responses[index] = requests.get(apiurl['url'])
    responses[index].raise_for_status()
    storenames[index] = apiurl['name']
    index += 1

# Initialize items and prices lists
items = []
prices = []
stores = []
units = []
items_generic = ['Broccoli', 'Green Asparagus', 'Iceberg Lettuce', 'Cucumbers', 'Vine Tomatoes']
header_row = ['Item']
header_row.append(storenames)

# Convert to price per pound
def convertPricePerUnits(basePrice, baseUnit, numberOfUnits):
    retPrice = float(basePrice)
    if baseUnit == "OUNCE":
        retPrice *= 16
    return retPrice/numberOfUnits

def convertUnits(baseUnits):
    retUnits = baseUnits
    if baseUnits == "OUNCE":
        retUnits = "POUND"
    if baseUnits == "LB":
        retUnits = "POUND"
    return retUnits

def unitQuantity(productName, baseUnits):
    wordsArray = productName.lower().split()    # Splits product description into an array of words
    if baseUnits in wordsArray[1:]:
        return wordsArray[wordsArray.index(baseUnits)-1]

# EXACT WORD CHECK (does not yet check tomato vs tomatoes)
# Solves in inefficient time
def pivotSort(items_generic, items, prices, storenames, units, itemcount):
    retTable = []
    for item in items_generic:
        itemGenArr = item.lower().split()
        for store in storenames:
            tableRow = []
            for count in range(itemcount):
                itemArr = items[count].lower().split()
                if all(word in itemArr for word in itemGenArr):
                    tableRow.append(prices[count])
                else:
                    tableRow.append("n/a")
            retTable.append(tableRow)
    return retTable

# Add items and prices
for itemcount in range(20):
    items.append(responses[0].json()['list'][itemcount]['name'])
    prices.append(responses[0].json()['list'][itemcount]['store']['price'])
    stores.append('Whole Foods')
    units.append(responses[0].json()['list'][itemcount]['store']['retail_unit'])
#   items.append(responses[1].json()['search_response']['items']['Item'][i]['title'])
#   prices.append(responses[1].json()['search_response']['items']['Item'][i]['price']['current_retail'])
#   stores.append('Target')
#   units.append('n/a')
    items.append(responses[2].json()['productsinfo'][itemcount]['description'])
    prices.append(convertPricePerUnits(responses[2].json()['productsinfo'][itemcount]['pricePer'],responses[2].json()['productsinfo'][itemcount]['unitOfMeasure'],1))
    stores.append('Safeway')
    units.append(convertUnits(responses[2].json()['productsinfo'][itemcount]['unitOfMeasure']))

groceriesTable = pivotSort(items_generic, items, prices, storenames, units, itemcount)

# Home page routing
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', groceries=zip(*groceriesTable))

# Unsorted table
@app.route("/unsorted")
def unsorted():
    return render_template('unsorted.html', groceries=zip(items, prices, stores, units))

# Enable debugging when running
if __name__ == '__main__':
    app.run(debug=True)
