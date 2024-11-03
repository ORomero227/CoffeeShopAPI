from marshmallow import Schema, fields


# Custom validation for the coffee price
# def validate_price(value):
#     if not value.replace("$", "").replace(".", "").isdigit():
#         raise ValidationError("Invalid price format. Must be a valid number e.g $5.00")


class CafeSchema(Schema):
    name = fields.String(required=True)
    map_url = fields.Url(required=True)
    img_url = fields.Url(required=True)
    location = fields.String(required=True)
    seats = fields.String(required=True)
    has_toilet = fields.Boolean(required=False)
    has_wifi = fields.Boolean(required=False)
    has_sockets = fields.Boolean(required=False)
    can_take_calls = fields.Boolean(required=False)
    coffee_price = fields.Float(required=True)

