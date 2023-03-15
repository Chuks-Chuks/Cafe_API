from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def converttodict(self):
        """This returns a dictionary of the table with the column name as the key and the column value as the value"""
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


#  HTTP GET - Read Record
@app.route('/get_random')
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(random_cafe.converttodict())


@app.route('/all')
def get_all():
    cafes = db.session.query(Cafe).all()
    display_cafe_list = {
        'cafe_': []
    }
    for cafe in cafes:
        display_cafe_list['cafe_'].append(cafe.converttodict())
    return jsonify(display_cafe_list)


@app.route('/search')
def search():
    loc = request.args.get('loc')
    print(loc)
    get_cafe = db.session.query(Cafe).filter_by(location=loc).all()
    if get_cafe:
        cafes = [(cafe.converttodict()) for cafe in get_cafe]
        return jsonify(cafes)
    else:
        return jsonify(
            {
                'error': "Sorry, there are no such locations."
            }
        )


# HTTP POST - Create Record
@app.route('/add_cafe', methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form.get('name'),
        map_url=request.form.get('map_url'),
        img_url=request.form.get('img_url'),
        location=request.form.get('location'),
        seats=request.form.get('seats'),
        has_toilet=bool(request.form.get('has_toilet')),
        has_wifi=bool(request.form.get('has_wifi')),
        has_sockets=bool(request.form.get('has_sockets')),
        can_take_calls=bool(request.form.get('can_take_calls')),
        coffee_price=request.form.get('coffee_price'),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(
        {
            'response': {
                'Success': 'Cafe added successfully'
            }
        }

    )


# HTTP PUT/PATCH - Update Record
@app.route('/update_cafe/<int:id_num>', methods=['PATCH'])
def update(id_num):
    cafe_to_be_update = db.session.get(Cafe, id_num)
    print(cafe_to_be_update)
    if cafe_to_be_update:
        # if request.method == 'POST':
        new_price = request.args.get('new_price')
        cafe_to_be_update.coffee_price = f'£{new_price}'
        db.session.commit()
        return jsonify(
            {
                'Success': 'Successfully updated'
            }
        )
    else:
        return jsonify(
            {
                'error': "Sorry, we don't have such a cafe available."
            }
        ), 404
# HTTP DELETE - Delete Record


@app.route('/delete_cafe/<int:id_num>', methods=['DELETE'])
def delete(id_num):
    top_secret_key = 'CAFE_DELETE'
    user_secret_key = request.args.get('api_key')
    cafe_to_be_deleted = db.session.get(Cafe, id_num)
    if cafe_to_be_deleted:
        if user_secret_key == top_secret_key:
            db.session.delete(cafe_to_be_deleted)
            db.session.commit()
            return jsonify(
                {
                    'success': 'cafe has been successfully deleted.'
                }
            )
        else:
            return jsonify(
                {
                    'error': 'you are not authorized to do that'
                }
            ), 404
    else:
        return jsonify(
            {
                'error': 'sorry there is no cafe available'
            }
        ), 404


if __name__ == '__main__':
    app.run(debug=True)
    with app.app_context():
        db.create_all()
