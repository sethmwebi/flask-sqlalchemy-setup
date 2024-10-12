from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:sethmwebi@localhost:3308/rest_apis"
)
db = SQLAlchemy(app)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    specialization = db.Column(db.String(50), nullable=False)

    def __init__(self, name, specialization):
        self.name = name
        self.specialization = specialization

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return "<Author %d>" % self.id


class AuthorSchema(SQLAlchemyAutoSchema):
    id = auto_field(dump_only=True)
    name = fields.String(required=True)
    specialization = fields.String(required=True)

    class Meta(SQLAlchemyAutoSchema.Meta):
        model = Author
        load_instance = True


with app.app_context():
    db.create_all()


@app.route("/authors", methods=["GET"])
def index():
    get_authors = db.session.query(Author).all()
    author_schema = AuthorSchema(many=True)
    authors = author_schema.dump(get_authors)
    return make_response(jsonify({"authors": authors}))


@app.route("/authors", methods=["POST"])
def create_author():
    data = request.get_json()
    author_schema = AuthorSchema()

    # validate and deserialize input data
    author = author_schema.load(data, session=db.session)

    db.session.add(author)
    db.session.commit()

    # serialize
    result = author_schema.dump(author)
    return make_response(jsonify({"author": result}), 201)


@app.route("/authors/<int:id>", methods=["GET"])
def get_author_by_id(id):
    get_author = db.session.get(Author, id)
    author_schema = AuthorSchema()

    author = author_schema.dump(get_author)
    return make_response(jsonify({"author": author}))


@app.route("/authors/<int:id>", methods=["PUT"])
def update_author_by_id(id):
    data = request.get_json()

    author = db.session.get(Author, id)

    if author is None:
        return make_response(jsonify({"error": "Author not found"}), 404)

    if "specialization" in data:
        author.specialization = data["specialization"]
    if "name" in data:
        author.name = data["name"]

    db.session.commit()

    author_schema = AuthorSchema()
    result = author_schema.dump(author)

    return make_response(jsonify({"author": result}), 200)


@app.route("/authors/<int:id>", methods=["DELETE"])
def delete_author_by_id(id):
    author = db.session.get(Author, id)

    if author is None:
        return make_response(jsonify({"error": "Author not found"}), 404)

    try:
        db.session.delete(author)
        db.session.commit()
        return make_response("", 204)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error": "An error occurred"}), 500)


if __name__ == "__main__":
    app.run(debug=True)
