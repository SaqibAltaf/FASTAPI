from typing import Union

from fastapi import FastAPI
from web3 import Web3
import json
import requests
from pymongo import MongoClient
import datetime
from bson import ObjectId  # Import ObjectId from bson module

app = FastAPI()

# Ethereum address to check
address = "0xD533a949740bb3306d119CC777fa900bA034cd52"
# Replace this with your preferred Ethereum node provider's URL
provider_url = "https://mainnet.infura.io/v3/cda6db89fabb4afe853eb396ca97f5ed"

# Connect to the Ethereum node
web3 = Web3(Web3.HTTPProvider(provider_url))

# MongoDB connection settings
mongodb_url = "mongodb://localhost:27017/"
mongodb_client = MongoClient(mongodb_url)
mongodb_database = mongodb_client["test"]
mongodb_collection_balance_history = mongodb_database["balace_history"]


@app.get("/get-balance")
async def read_root():
    try:
        # Get the balance in Wei asynchronously
        balance_wei = web3.eth.get_balance(address)
        print(balance_wei)
        # Convert Wei to Ether
        balance_ether = web3.from_wei(balance_wei, "ether")
        timestamp = datetime.datetime.now()
        data = {
            "balance": balance_ether,
            "usd_balance": get_usd_balance(balance_ether),
            "timestamp": timestamp,
        }
        mongodb_collection_balance_history.insert_one(data)
        return {
            "balance": balance_ether,
            "usd balance": get_usd_balance(balance_ether),
        }
    except Exception as e:
        return {"error": str(e)}


def get_usd_balance(amount):
    try:
        # Fetch CRV price from CoinGecko API (you can replace this with your preferred price source)
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "curve-dao-token", "vs_currencies": "usd"},
        )
        print(response.json().get("curve-dao-token", {}))
        get_price_api = response.json().get("curve-dao-token", {}).get("usd")

        usd_balance = amount * get_price_api
        return usd_balance
    except Exception:
        return 0


@app.get("/get-balance-history")
async def getHistory():
    try:
        history = list(mongodb_collection_balance_history.find())
        # Convert ObjectId to string for each document
        for item in history:
            item["_id"] = str(item["_id"])

        return {
            "history": history,
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
