from __future__ import annotations

from typing import Optional

from pymongo import MongoClient as _MongoClient
from pymongo.database import Database as _Database


class MongoClient:
    """Содержит методы управления MongoDB клиентом."""

    def __init__(self, db_name: str, host='localhost', port=27017):
        self._host = host
        self._port = port
        self._db_name = db_name

        self._mongo: Optional[_MongoClient] = None
        self._db: Optional[_Database] = None

    def _get_client(self) -> _MongoClient:
        if not isinstance(self._mongo, _MongoClient):
            uri = f'mongodb://{self._host}:{self._port}'
            self._mongo = _MongoClient(uri)
        return self._mongo

    def get_db(self) -> _Database:
        if not isinstance(self._db, _Database):
            mongo = self._get_client()
            self._db = mongo.get_database(self._db_name)
        return self._db

    def close(self):
        if self._mongo:
            self._mongo.close()


class MongoDatabase(MongoClient):
    """Содержит базовые методы для взаимодействия с базой данных."""

    def count_objects(self, collection: str, _filter=None) -> int:
        db = self.get_db()
        _filter = _filter or {}
        return db[collection].count_documents(_filter)

    def add_object(self, collection: str, object_data: dict) -> str:
        """Добавляет объект в коллекцию, возращает его _id."""
        db = self.get_db()
        result = db[collection].insert_one(object_data)
        return str(result.inserted_id)

    def add_objects(self, collection: str, objects_data: list[dict]):
        """Добавляет объекты в коллекцию, возращает их _id."""
        db = self.get_db()
        results = db[collection].insert_many(objects_data)
        return [str(i) for i in results.inserted_ids]

    def get_object(self, collection: str, _filter: dict) -> Optional[dict]:
        """Возвращает из коллекции объект или None."""
        db = self.get_db()
        return db[collection].find_one(_filter)

    def get_objects(self, collection: str, _filter: dict) -> list[dict]:
        """Возвращает из коллекции список объектов."""
        db = self.get_db()
        return [obj for obj in db[collection].find(_filter)]

    def update_object(self, collection: str, _filter: dict, operator: str, update: dict, upsert=False):
        """Обновляет объект в коллекции, может создать новый объект при [upsert=True]."""
        db = self.get_db()
        db[collection].update_one(_filter, {operator: update}, upsert=upsert)

    def update_objects(self, collection: str, _filter: dict, operator: str, update: dict, upsert=False):
        """Обновляет объекты в коллекции, может создать новый объекты при [upsert=True]."""
        db = self.get_db()
        db[collection].update_many(_filter, {operator: update}, upsert=upsert)

    def delete_object(self, collection: str, _filter: dict):
        """Удаляет объект из коллекции."""
        db = self.get_db()
        db[collection].delete_one(_filter)

    def delete_objects(self, collection: str, _filter: dict):
        """Удаляет объекты из коллекции."""
        db = self.get_db()
        db[collection].delete_many(_filter)
