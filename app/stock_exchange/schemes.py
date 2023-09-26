from marshmallow import Schema, ValidationError, fields, validates


class UserRequestSchema(Schema):
    vk_id = fields.Int(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)


class UserIdSchema(Schema):
    vk_id = fields.Int(required=True)


class GameScoreResponseSchema(Schema):
    score_id = fields.Int()
    total_score = fields.Int()
    total_games = fields.Int()
    total_win = fields.Int()


class UserResponseSchema(Schema):
    vk_id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    game_score = fields.Nested("GameScoreResponseSchema")


class StockIdSchema(Schema):
    stock_id = fields.Int(required=True)


class StockRequestSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Int()


class StockResponseSchema(Schema):
    stock_id = fields.Int()
    name = fields.Str()
    price = fields.Int()


class GameIdSchema(Schema):
    chat_id = fields.Int(required=True)


class GameRequestSchema(Schema):
    users = fields.Nested("UserResponseSchema", many=True)
    number_of_moves = fields.Int()
    stocks = fields.Nested("StockResponseSchema", many=True)


class GameResponseSchema(Schema):
    chat_id = fields.Int()
    users = fields.Nested("UserResponseSchema", many=True)
    number_of_moves = fields.Int()
    stocks = fields.Nested("StockResponseSchema", many=True)
