from marshmallow import Schema, ValidationError, fields, validates


class UserGaScRequestSchema(Schema):
    vk_id = fields.Int(required=True)


class UserResponseSchema(Schema):
    user_id = fields.Int()
    vk_id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    game_score_id = fields.Int()


class GameScoreResponseSchema(Schema):
    score_id = fields.Int()
    total_score = fields.Int()
    total_games = fields.Int()
    total_win = fields.Int()


class StockRequestSchema(Schema):
    stock_id = fields.Int(required=True)


class StockResponseSchema(Schema):
    stock_id = fields.Int()
    name = fields.Str()
    price = fields.Int()
