from apps.models import BaseModel
from ext import db

class User(BaseModel):
    __tablename__ = 'user'
    username = db.Column(db.String(50),nullable=False,unique=True)
    password = db.Column(db.String(128))
    repassword = db.Column(db.String(128))

    def __str__(self):
        return self.username
















