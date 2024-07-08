#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants_Resource(Resource):
    def get(self):
        restaurants = [restaurant.to_dict(only=("id", "name", "address")) for restaurant in Restaurant.query.all()]
        response = make_response(restaurants, 200)

        return response
    
class Single_Restaurant_Resource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if restaurant:
            rest_dict = restaurant.to_dict()
            response = make_response(rest_dict, 200)
        else:
            response = make_response({"error": "Restaurant not found"}, 404)

        return response

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response = make_response({"message": "Restaurant deleted"}, 204)
        else:
            response = make_response({"error": "Restaurant not found"}, 404)
            
        return response

class Pizzas_Resource(Resource):
    def get(self):
        pizzas = [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in Pizza.query.all()]

        response = make_response(pizzas, 200)

        return response

class RestaurantPizzas_Resource(Resource):
    def post(self):
        data = request.get_json()

        try:
            restaurant_id = data['restaurant_id']
            pizza_id = data['pizza_id']
            price = data['price']

            if price < 1 or price > 30:
                response = make_response({"errors": ["validation errors"]}, 400)

                return response

            # Create a new instance of RestaurantPizza
            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            pizza_dict = new_restaurant_pizza.to_dict()

            response = make_response(pizza_dict, 201)
            
            return response

        # Handle errors
        except KeyError as e:
            return make_response({"errors": [f"Missing key: {str(e)}"]}, 400)
        except Exception as e:
            db.session.rollback()
            return make_response({"errors": [str(e)]}, 400)
        finally:
            db.session.close()

api.add_resource(Restaurants_Resource, "/restaurants")
api.add_resource(Single_Restaurant_Resource, "/restaurants/<int:id>")
api.add_resource(Pizzas_Resource, "/pizzas")
api.add_resource(RestaurantPizzas_Resource, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)