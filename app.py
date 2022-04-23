import os
import sys

from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager

# from apps.user.models import *
# from apps.article.models import *

from apps import create_app
from ext import db


app = create_app()


manager = Manager(app=app)
migrate = Migrate(app=app,db=db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':

    manager.run()





































