from apps.models import BaseModel
from ext import db


class User_rec(BaseModel):
    __tablename__ = 'user_rec'
    username = db.Column(db.String(50), nullable=False)
    imagename = db.Column(db.String(50))
    image_rec = db.Column(db.String(50))

    def __str__(self):
        return self.username
