import os
import log
import json
import pymongo
from pymongo import MongoClient
from pathlib import Path

class Database:
    __database_location__ = None
    __database_name__ = None
    __collection_name__ = None
    __relevant_data_in_article__ = None
    __database_timeout_ms__ = None
    __article_collection__ = None
    __logger__ = log.get_logger(__name__)

    
    def __init__(self, config):
        self.__database_location__ = config['database_location'] if 'database_location' in config.keys() else os.getenv('DATABASE_LOCATION')
        self.__database_name__ = config["database_name"]
        self.__collection_name__ = config["collection_name"]
        self.__database_timeout_ms__ = config["database_timeout_ms"]

        client = MongoClient(self.__database_location__, serverSelectionTimeoutMS=self.__database_timeout_ms__)
        db = client[self.__database_name__]
        self.__article_collection__ = db[self.__collection_name__]
        
    def load_article_by_name(self, article):
        self.__logger__.info(f"Retrieving files by test_article_name {article['article_name']}, called from load_article_by_name.")
        result = self.__article_collection__.find_one({"article_name":article['article_name']})
        return result
    def load_all_articles(self):
        self.__logger__.info("Retrieving all files, called from load_all_articles.")
        result = self.__article_collection__.find({})
        return result
    def insert_article(self, article):
        
        file = self.load_article_by_name(article)
        if file is None:
            try:
                self.__logger__.info(f"Attempting to insert article with test_article_name: {article['article_name']}")
                self.__article_collection__.insert(article)
            except pymongo.errors.DuplicateKeyError as ex:
                self.__logger__.info(f"Failed to insert article with test_article_name: {article['article_name']} due to: {ex}")
        elif file['file_content'] != article['file_content']:
            self.__logger__.info(f"Attempting to update article with test_article_name: {file['article_name']}")
            self.__article_collection__.update_one(
            {"_id": file['_id']},
            {"$set":
                {"file_content": article['file_content'],
                "last_updated":article['last_updated'],
                "outdated":article['outdated']}
            })
    def update_outdated_file(self, article):
        file = self.load_article_by_name(article)
        self.__logger__.info(f"Attempting to update article with test_article_name: {file['article_name']}")
        if file['outdated'] != article['outdated']:
            self.__article_collection__.update_one(
                {"_id": file['_id']},
                {"$set":
                    {"outdated":article['outdated']}
                })
