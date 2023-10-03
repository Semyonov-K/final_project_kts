from marshmallow import Schema, ValidationError, fields, validates

class StockIdSchema(Schema):
    stock_id = fields.Int(required=True)


class StockRequestSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Int()


class StockResponseSchema(Schema):
    stock_id = fields.Int()
    name = fields.Str()
    price = fields.Int()


class ChatIdSchema(Schema):
    chat_id = fields.Int(required=True)


class ChatResponseSchema(Schema):
    chat_id = fields.Int()
    start_game = fields.Bool()
    pregame = fields.Bool()
    timer = fields.Str()
    game = fields.Bool()
    endgame = fields.Bool()
