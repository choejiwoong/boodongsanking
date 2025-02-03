from pymongo import MongoClient

# MongoDB 연결 함수
def connect_to_mongodb(uri, db_name, collection_name):
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    return collection

# 데이터 삽입 함수
def insert_document(collection, data):
    result = collection.insert_one(data)
    return f"Inserted document with ID: {result.inserted_id}"

# 데이터 조회 함수 (모든 문서 조회)
def get_all_documents(collection):
    documents = list(collection.find())
    return documents

# 특정 조건으로 데이터 조회 함수
def find_documents(collection, query, projection=None):
    documents = list(collection.find(query, projection))
    return documents

# 데이터 업데이트 함수
def update_document(collection, query, new_values):
    result = collection.update_one(query, {'$set': new_values})
    return f"Matched: {result.matched_count}, Modified: {result.modified_count}"

# 데이터 덮어쓰기 함수
def overwrite_document(collection, query, new_values):
    result = collection.replace_one(query, new_values)  # 전체 문서 교체
    return f"Matched: {result.matched_count}, Modified: {result.modified_count}"

# 데이터 삭제 함수
def delete_document(collection, query):
    result = collection.delete_one(query)
    return f"Deleted documents count: {result.deleted_count}"