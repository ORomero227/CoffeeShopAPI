import os

from flask import Flask, jsonify, render_template, request
from marshmallow import ValidationError
from sqlalchemy import func
from schemas import CafeSchema
from database import db, Cafe
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
db.init_app(app)


# Create the Database
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    random_cafe = db.session.execute(db.select(Cafe).order_by(func.random())).scalar()
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def get_cafe_at_location():
    query_params = request.args.get("location")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_params)).scalars()
    all_cafes = result.all()

    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not found": "Sorry, we don't have a cafe at that location."})


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    schema = CafeSchema()
    api_key = request.args.get("api-key")
    if api_key == os.getenv("API_KEY"):
        try:
            # Validate and deserialize data from the request form
            data = schema.load(request.form)
            # Create the new Cafe
            new_cafe = Cafe(**data)
            db.session.add(new_cafe)
            db.session.commit()

            return jsonify(response={"success": "Successfully added the new cafe.", "new_cafe_id": new_cafe.id}), 201
        except ValidationError as err:
            return jsonify(error=err.messages), 400
    else:
        return jsonify({"error": "Sorry, that's is not allowed. Make sure you have the correct api_key."}), 403


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_coffee_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success={"success": "Successfully updated the price"}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == os.getenv("API_KEY"):
        cafe = db.session.get(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success={"success": "The cafe has been successfully deleted"}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404
    else:
        return jsonify({"error": "Sorry, that's is not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run()
