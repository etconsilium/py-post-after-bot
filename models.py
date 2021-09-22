##
##
#
#

import json
from zlib import adler32
from json.encoder import JSONEncoder
from datetime import datetime, date, time, timedelta, timezone
import warnings

import dateparser
from dateparser import parse as dparser

# from dateparser import parse


import db
from db import DB
from db import types

# from pprint import pprint, pp


class BasicModel(object):
    """не пытайтесь повторить
    # Do not attempt duplicate this hacks without consulting your pythia first
    """

    # private static / class var
    __driver = DB
    __tablename = None
    # protected / public
    _save_on_exit = True
    _driver = None
    _tablename = None
    _id = None
    _hash = None
    _container = {}
    # public
    key = db.id()  #    aka ROW_ID

    def __new__(cls, *args, **kwargs):

        if __class__.__name__ != cls.__name__:
            cls._tablename = (
                cls.__name__ if cls.__tablename is None else cls.__tablename
            )
            cls._driver = __class__.__driver(cls._tablename)
        # TypeError: object.__new__() takes exactly one argument (the type to instantiate)
        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        """
        Model( {var1:1, var2:2} )
        or
        Model( {var1:1, var2:2}, 'key' )
        or
        Model( var1=1, var2=2, key='key' )
        or
        Model( var1=1, var2=2 )
        or
        Model()
        """

        self._id = id(self)

        if len(args) > 0 and isinstance(args[0], dict):
            self.__dict__.update(args[0])
            if len(args) > 1:
                self.key = str(args[1])

        self.__dict__.update(kwargs)

        if self.key is None:
            self.key = str(db.id())

        self._hash = hash(self)
        # print("init data ", self.__name__, self.__dict__)
        pass

    def __hash__(self) -> int:
        """the fastest. probably"""
        return adler32(bytes(str(self.__dict__), "utf8")) & 0xFFFFFFFF  # see py guide

    def __dir__(self) -> dict:
        """dir() вернёт список легитимных атрибутов, а для избранных __dir__() -- словарь данных"""
        return dict(
            [
                # лень кастомизировать типы
                (k, (str(v) if not isinstance(v, (int, float, bool, str)) else v))
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            ]
        )

    def __repr__(self, **kwargs) -> str:
        return json.dumps(
            self.__dir__(), **dict({"sort_keys": (True), "indent": 2}, **kwargs)
        )

    def __del__(self) -> None:
        """Destructor"""

        if self.__class__._save_on_exit and hash(self) != self._hash:
            self._driver.put(self.__dir__(), key=self.key)

        return

    def __setattr__(self, name, value):

        if value is None:
            self.__delattr__(name)
        else:
            # print("SET attr", self.__class__.__name__, name, value)
            self.__dict__.update({name: value})
        return

    def __getattr__(self, name):
        """oldschool style

        new school:
        def __getattribute__(self, item)
            return object.__getattribute__(self,item)
            return super().__getattribute__(item)
        """
        try:
            return self.__dict__[name]
        except KeyError:
            # lika dict.pop(name, None) but twice as quick
            pass

    def __delattr__(self, name):
        try:
            del self.__dict__[name]
        except KeyError:
            pass

    ##
    ##
    # операции с данными в виде Find\Update\Insert\Delete
    # implementation for the data model operations in accordance FUI(D) pattern
    # find without Lazy
    #

    @classmethod
    def find(cls, criteria=None, limit=1000, last_key=None):
        r = cls._driver.fetch(query=criteria, limit=limit, last=last_key)
        # @TODO
        return r

    def insert(self):
        """Needs implementation
        now it work as db.put()
        """
        warnings.warn("Needs implementation", UserWarning)
        self._driver.put(repr(self), key=self.key)  # !important key=
        return self

    def update(self, data: dict = None, criteria=None):
        """Needs implementation"""
        if data is not None:
            self.__dict__.update(date)
            r = self._driver.update(updates=self.__dict__, key=self.key)
            if r is None:
                # 200
                if criteria is not None:
                    r = self._driver.update(updates=criteria, key=self.key)

                r = self._driver.get(self.key)
                if r is not None:
                    self.__dict__ = r

        return self

    @classmethod
    def one(cls, key: str):
        """Get one row by key
        :key: like row_id
        :return: object(cls) Model
        :example:
        class Model(BasicModel):
            pass

        print( Model.one(string_id) )
        """

        r = (
            cls._driver if cls._driver is not None else __class__.__driver(cls.__name__)
        ).get(key)

        if r is None:
            r = {"key": key}
        if len(r) == 2 and 'key' in r and 'value' in r and type('value') == dict:
            r = dict({"key": key}, **dict(json.loads(r["value"])))
        else:
            # smthng oblivious
            pass

        o = cls.__new__(cls, r)
        o.__init__(r)
        return o


class Record(BasicModel):
    """Damn answering machine tapes!"""

    # _save_on_exit = False

    id = None
    key = None

    sender = None
    from_id = None
    addressee = None
    to_id = None

    keyword = None
    content = "None"

    _created = "now"
    _expires = "in 3 days"

    limits = {"quantity": 1, "keys": 3}

    def __init__(self, message=None):
        """Constructor"""
        super().__init__(message)

        # print("Record init", message)
        # pp(self.__dict__)
        # pp(self._hash)
        # pp(self.__class__._hash)
        # self.id = self.__id
        self._id = id(self)
        self.created = datetime.now()
        self.expires = dparser(self._expires)
