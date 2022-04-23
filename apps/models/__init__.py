from datetime import datetime

from ext import db


class BaseModel(db.Model):
    __abstract__ = True     # 这段代码的意思为该模型自身不能作为模型来使用，只能被继承来使用
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    date_time = db.Column(db.DateTime,default=datetime.now)