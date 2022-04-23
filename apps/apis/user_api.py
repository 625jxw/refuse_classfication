import json
import os.path
import random
import shutil
import uuid

import werkzeug.datastructures
from flask import Blueprint, make_response, request, render_template, Response
from flask_restful import Api, reqparse, Resource, fields
from werkzeug.datastructures import FileStorage

from apps.models.user_model import User
from ext import db, cache
from settings import Config
from test import pic_recognize

from apps.apis import spw

from apps.models.user_rec_model import User_rec

user_bp = Blueprint('user', __name__)

api = Api(user_bp)

sms_parser = reqparse.RequestParser()  # 接收前端
sms_parser.add_argument('username', required=True, location=['form', 'args'])
sms_parser.add_argument('password', required=True, location=['form', 'args'])
sms_parser.add_argument('repassword', location=['form', 'args'])


class Html(Resource):
    def get(self):
        response = make_response(render_template('html/index.html'))
        response.headers['Content-Type'] = 'text/html; charset=UFT-8'
        return response


class Home(Resource):
    def get(self):
        response = make_response(render_template('html/home.html'))
        response.headers['Content-Type'] = 'text/html; charset=UFT-8'
        return response


class History(Resource):
    def get(self):
        list_1 = []
        username = request.cookies.get('username')
        data = User_rec.query.filter(User.username == username).all()
        for i in data:
            print("-------------------------->")
            print("**************************")
            print(i.imagename)

            dict = {
                "id": i.id,
                "datatime": str(i.date_time),
                "user_img": i.imagename,
                "image_rec": i.image_rec
            }
            list_1.append(dict)
        json_data = json.dumps(list_1)
        return json_data


delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', required=True, location=['form', 'args'])


class History_Delete(Resource):
    def get(self):
        args = delete_parser.parse_args()
        id = args.get('id')
        user_rec = User_rec.query.filter(User_rec.id == id).first()
        imagename = user_rec.imagename
        os.remove(r'C:\Users\sunshenao\deeplearn\project\WebTest\refuse_classification\static\img_name' + '/' + imagename)
        db.session.delete(user_rec)
        db.session.commit()
        return {'status': 200}

class History_DeleteAll(Resource):
    def get(self):
        username = request.cookies.get('username')
        user_rec = User_rec.query.filter(User_rec.username == username).all()
        for x in user_rec:
            db.session.delete(x)
            imagename = x.imagename
            os.remove(r'C:\Users\sunshenao\deeplearn\project\WebTest\refuse_classification\static\img_name' + '/' + imagename)
        db.session.commit()
        return {'status': 200}


class RegisterApi(Resource):
    def get(self):
        return '成功！'

    def post(self):

        args = sms_parser.parse_args()
        print(args)
        username = args.get('username')
        password = args.get('password')
        print(password)
        repassword = args.get('repassword')
        print(repassword)

        if username:

            user = User.query.filter(User.username == username).first()
            if not user:

                if password == repassword:
                    user = User()
                    user.username = username
                    user.password = password
                    user.repassword = repassword
                    db.session.add(user)
                    db.session.commit()

                    return {'status': 200}

                else:

                    return '两次输入的密码不一致'
            else:

                return '用户名已存在'


class LoginApi(RegisterApi):
    def post(self):
        args = sms_parser.parse_args()
        username = args.get('username')
        password = args.get('password')

        if username and password:
            user = User.query.filter(User.username == username).first()
            if not user:
                return {'status': 404, 'msg': '未输入用户名或密码!'}
            else:
                if user.password == password:
                    response = Response(json.dumps({'status': 200, 'msg': '登陆成功！'}), content_type='application/json')
                    response.set_cookie("username", username)
                    print(response)

                    return response


parser = reqparse.RequestParser()
parser.add_argument('images', type=werkzeug.datastructures.FileStorage, location=['files'],
                    help="I cant find the images")
parser.add_argument('icon_1', type=str, location=['form'], help="not find the icon_1")


class Photo_recognize(Resource):
    def post(self):
        list_3 = []
        list_1 = []
        list_name = []
        args = request.files.getlist('images')
        username = request.cookies.get('username')
        print(args)
        print(args)
        for icon in args:
            back_name = icon.filename.split(".")[-1]
            front_name = icon.filename.split(".")[0]
            upload_path = os.path.join(Config.UPLOAD_ICON_DIR, icon.filename)

            icon.save(upload_path)

            md5_name = spw(username + '_' + front_name) + '.' + back_name
            shutil.copyfile(upload_path, r'C:\Users\sunshenao\deeplearn\project\WebTest\refuse_classification\static\img_name' + '/' +
                            md5_name)

            list_name.append(md5_name)

        list_1, list_2 = pic_recognize()
        for i in list_2:
            list_3.append(spw(i))
        data = dict(zip(list_3, list_1))
        json_data = json.dumps(data)
        shutil.rmtree(r'C:\Users\sunshenao\deeplearn\project\WebTest\refuse_classification\static\upload\icon', ignore_errors=True)

        os.mkdir(r'C:\Users\sunshenao\deeplearn\project\WebTest\refuse_classification\static\upload\icon')
        for x in range(0, len(list_2)):
            user_rec = User_rec()
            user_rec.username = username
            user_rec.imagename = list_name[x]
            user_rec.image_rec = list_1[x]
            db.session.add(user_rec)
        db.session.commit()
        return json_data


class Delete_Cookie(Resource):
    def get(self):
        response = Response(json.dumps({'status': 200, 'msg': '退出成功！'}), content_type='application/json')
        response.delete_cookie('username')
        return response


api.add_resource(RegisterApi, '/register')
api.add_resource(Html, '/')
api.add_resource(Home, '/home')
api.add_resource(LoginApi, '/login')
api.add_resource(Photo_recognize, '/photo_rec')
api.add_resource(History_Delete, '/delete')
api.add_resource(History, '/history')
api.add_resource(History_DeleteAll, '/deleteAll')
api.add_resource(Delete_Cookie, '/logout')
