import pymongo
from bson.json_util import dumps
from bson.objectid import ObjectId


class MongoServiceException(Exception):
    def __init__(self, msg):
        self.msg = msg


class MongoClient():
    def __init__(self, url, port=None):
        self.client = pymongo.MongoClient(url, port=port)
        self.db = None
        self.codec_options = None
    

    def connect(self, db_name):
        self.db = getattr(self.client, db_name)
    

    def set_codec_options(self, codec_options):
        self.codec_options = codec_options
    

    def find_one(self, collection, condition):
        collection = self.db.get_collection(collection, codec_options=self.codec_options)
        response = collection.find_one(condition)
        return response
    

    def find_all(self, collection, condition):
        collection = self.db.get_collection(collection, codec_options=self.codec_options)
        cursor = collection.find(condition)
        return cursor


    def insert_record(self, collection, record):
        inserted_record = self.db.get_collection(collection, codec_options=self.codec_options).insert_one(record)
        return inserted_record.inserted_id


    def list_all_collections(self):
        return self.db.list_collection_names()
    

    def update_record(self, collection, record, set_expression):
        self.db.get_collection(collection, codec_options=self.codec_options).update_one({
            '_id': record['_id'],
        },  {
            '$set': set_expression,
        }, upsert=False)

    
    def increment_record(self, collection, record, increment_expression):
        try:
            self.db.get_collection(collection, codec_options=self.codec_options).update_one({
                '_id': record['_id'],
            },  {
                '$inc': increment_expression,
            }, upsert=False)
        except pymongo.errors.WriteError:
            set_expression = {}
            for field, value in increment_expression.items():
                set_expression[field] = record[field] + value
            self.update_record(collection, record, set_expression)


    def delete_records(self, collection, record_id):
        if isinstance(record_id, int):
            return self.db.get_collection(collection, codec_options=self.codec_options).delete_many({"_id": ObjectId(record_id)})
        elif isinstance(record_id, ObjectId):
            return self.db.get_collection(collection, codec_options=self.codec_options).delete_many({"_id": record_id})
        else:
            raise MongoServiceException(f"Invalid type of id: {record_id}")


    def delete_all_documents(self, collection):
        self.db[collection].drop()
    
    
    def fetch_all(self, cursor, container=[], func='append'):
        for record in cursor.sort([('$natural', 1,)]):
            getattr(container, func)(record)
        return container
