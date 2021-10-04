####
##
#
#
""" # Do NOT attempt duplicate the hacks used here without consulting your pythia first """


import json
import warnings
from zlib import adler32
from datetime import datetime

# from datetime import datetime, date, time, timedelta, timezone
# from pprint import pprint as pp
# from var_dump import var_dump

from db import dateparser, strdateparser
from db import DB, id as row_id, message_id

from settings import log


class BasicModel(object):

    # private static / class var

    # pylint: disable=W0212,W0238
    # W0212: Access to a protected member __driver of a client class (protected-access)
    # W0238: Unused private member `BasicModel.__driver` (unused-private-member)
    __driver = DB

    # protected / public
    _save_on_exit = True
    _tablename = None
    _driver = None
    _tablename = None
    _id = None
    _hash = None
    _container = {}

    # public
    key = None  #    aka ROW_ID

    def __new__(cls, *args, **kwargs):
        # pylint: disable=W0613
        # Unused arguments (unused-argument)
        cls.__init_driver(cls)

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

        if len(args) > 0 and isinstance(args[0], dict):
            self.__dict__.update(args[0])
            if len(args) > 1:
                self.key = str(args[1])
        else:
            if len(args) == 1:
                self.key = str(args[0])

        self.__dict__.update(kwargs)

        self.key = str(row_id() if not self.key else self.key)  # string only

        # !discussion
        # r = self._driver.get(self.key)  # try data raise
        # if isinstance(r, dict) and len(r):
        # self.__dict__ = dict(r, **self.__dict__)
        # наоборот, надо дополнять значения инициализации значениями из базы
        #     self.__dict__.update(r)

        self._id = id(self)
        self._hash = hash(self)

        # return self    # __init__

    def __init_driver(cls):
        if __class__.__name__ != cls.__name__:
            if cls._tablename is None:
                cls._tablename = cls.__name__
            if cls._driver is None:
                cls._driver = __class__.__driver(cls._tablename)

    def __dir__(self) -> dict:
        """dir() вернёт список легитимных атрибутов, а для избранных __dir__() вернет словарь данных"""
        return dict(
            (
                k,
                (
                    str(v)  # лень кастомизировать типы
                    if not isinstance(v, (int, float, bool, str, type(None)))
                    else v
                ),
            )
            for k, v in sorted(self.__dict__.items())
            if not k.startswith("_")
        )

    def __repr__(self, **kwargs) -> str:
        return json.dumps(
            self.__dir__(), **dict({"sort_keys": (True), "indent": 2}, **kwargs)
        )

    def __hash__(self) -> int:
        """the faster than fast. probably"""
        # return adler32(bytes(str(self.__dict__), "utf8")) & 0xFFFFFFFF  # see py guide
        return adler32(bytes(str(self.__dir__()), "utf8")) & 0xFFFFFFFF  # see py guide

    def __setattr__(self, name, value):
        """принципиальной необходимости нет
        введено для удобной обработки отсутствующих свойств
        AttributeError: 'Class' object has no attribute 'name'
        """
        # пс: и для удаления через присвоение None ;)

        if value is None:
            self.__delattr__(name)
        else:
            # print("SET attr", self.__class__.__name__, name, value)
            self.__dict__.update({name: value})
        return

    def __getattr__(self, name):
        """пара к __setattr__

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
        return None  #!important

    def __delattr__(self, name):
        try:
            del self.__dict__[name]
        except KeyError:
            pass

    def __del__(self):
        """Finalizer"""

        if self.__class__._save_on_exit and hash(self) != self._hash:
            try:
                # self.update()
                self._driver.put(self.__dir__(), key=self.key)
            except Exception as exc:
                log.warning(
                    "деструктор не отработал корректно, информация не сохранена. // "
                    + str(exc)
                )
        pass

    ##
    ##
    # операции с данными в виде Find\Update\Insert\Delete
    # implementation for the data model operations in accordance FUI(D) pattern
    # find without Lazy
    #

    @classmethod
    def find(cls, criteria=None, limit=1000, last_key=None):
        cls.__init_driver(cls)
        r = cls._driver.fetch(query=criteria, limit=limit, last=last_key)
        # @TODO

        # if r.count>0:
        return {"count": r.count, "last_key": r.last, "data": [cls(d) for d in r.items]}

    def insert(self):
        """Needs implementation
        now it work as db.put()
        """
        self._driver.put(self.__dir__(), key=self.key)  # !important key=
        self._hash = hash(self)
        return self

    def update(self, data: dict = None, criteria=None):
        """Needs implementation"""
        warnings.warn("Needs implementation", UserWarning)

        if data is not None:
            # pylint: disable=E0203
            # Access to member '__dict__' before its definition (access-member-before-definition)
            # ничего не понимаю ¯\_(ツ)_/¯
            self.__dict__.update(data)
            r = self._driver.update(updates=self.__dict__, key=self.key)
            if r is None:
                # 200
                if criteria is not None:
                    r = self._driver.update(updates=criteria, key=self.key)

                r = self._driver.get(self.key)
                if r is not None:
                    self.__dict__ = r

        else:
            self.insert()

        self._hash = hash(self)

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

        o = cls.__new__(cls)
        r = o._driver.get(key)

        if r is None:
            r = {"key": key}
        if len(r) == 2 and "key" in r and "value" in r and type("value") == dict:
            r = dict({"key": key}, **dict(json.loads(r["value"])))
        else:
            # smthng oblivious
            pass

        o.__init__(r)
        return o

    pass  # BasicModel


class Record(BasicModel):
    """Damn answering machine tapes!"""

    # _save_on_exit = False
    _created = "now"
    _expires = "in 3 days"

    limits = {"quantity": 1, "keys": 3}

    def __init__(self, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)

        self._id = id(self)
        self.created = dateparser(self._created) if not self.created else self.created
        self.expires = dateparser(self._expires)

    def id(self):
        return row_id()

    pass  # Record


class Message(Record):

    keyword = None
    content = "None"

    _created = "now"
    _expires = "in 1 hour"

    # pylint: disable=W1113
    # W1113: Keyword argument before variable positional arguments list in the definition of __init__ function (keyword-arg-before-vararg)
    def __init__(self, message=None, *args, **kwargs):
        print(args, message, kwargs)
        super().__init__(*args, **dict(kwargs, **{"message": message}))

        if message is not None:
            self.id = message_id(message)
            self.sender = message.from_user.name
            self.from_id = message.from_user.id
            self.addressee = None
            self.to_id = None
            self.value = message

        self.keyword = None
        self.content = ""

    pass  # Message
