"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Fav_people
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    all_user = User.query.all()
    serializados = list(map(lambda user: user.serialize(), all_user))
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(serializados), 200

@app.route("/people", methods=['GET'])
def get_people():
    # todos los personajes desde la base de datos
    all_people = People.query.all() #Select * from People
    print(all_people) #el resultado es un arreglo de clases
    # people_serialized = []
    # for people in all_people:
    #     people_serialized.append(people.serialize())
    # return jsonify(people_serialized)
    all_people = list( map(lambda people:people.serialize(), all_people))
    return jsonify(all_people)

#busqueda por parametro
# @app.route("/people/<people_name>", methods=['GET'])
# def one_people(people_name):
#     one = People.query.filter_by(name=people_name).first()
#     return jsonify(one.serialize())

@app.route("/people/<int:people_id>", methods=['GET'])
def one_people(people_id):
    one = People.query.get(people_id) #busqueda solo por el pk
    return jsonify(one.serialize())
   
@app.route("/people/favorite/<int:people_id>", methods=['POST'])
def add_people_fav(people_id):
    one = People.query.get(people_id) #busqueda solo por el pk
    user = User.query.get(1)
    if(one):
        new_fav = Fav_people()
        new_fav.email = user.email
        new_fav.people_id = people_id
        db.session.add(new_fav)
        db.session.commit()
        return "Hecho!"
    else:
        raise APIException("no existe el personaje", status_code=404)

@app.route("/people/favorite/<int:people_id>", methods=['DELETE'])
def delete_people_fav(people_id):
    one = Fav_people.query.filter_by(people_id=people_id).first()
    if(one):
        db.session.delete(one)
        db.session.commit()
        return "eliminado"
    else:
        raise APIException("no existe el personaje", status_code=404)


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
