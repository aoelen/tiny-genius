from pymongo import MongoClient

client = MongoClient("mongodb://root:rootpassword@mongodb_container:27017/")
database = "tinyGenius"
cursor = client[database]
collection_papers = cursor["papers"]
collection_properties = cursor["properties"]
collection_resources = cursor["resources"]
