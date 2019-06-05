# coding=utf-8

from pymongo import MongoClient
from freeproxy.settings import MONGO_HOST, MONGO_PORT, DB

client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
db_crawler = client[DB]

