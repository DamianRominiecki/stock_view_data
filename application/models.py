from . import db, app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=True)
    email = db.Column(db.String, unique=True, nullable=True)
    password = db.Column(db.String, unique=False, nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"{self.username}, {self.email}, {self.password}"

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String, unique=True, nullable=False)
    long_name = db.Column(db.String, unique=True, nullable=False)
    business_summary = db.Column(db.String, unique=False, nullable=False)
    website = db.Column(db.String, unique=False, nullable=False)
    market_cap = db.Column(db.Float, unique=False, nullable=False)
    open_price = db.Column(db.Float, unique=False, nullable=False)
    previous_close = db.Column(db.Float, unique=False, nullable=False)
    currency = db.Column(db.String, unique=False, nullable=False)
    stockitems = db.relationship('StockItem', backref='stock', lazy="joined", order_by="StockItem.id",)

    def __repr__(self):
        return f"{self.id}/{self.stock_name}"

    def get_data(self):
        dates = [item.stock_date for item in self.stockitems]
        lows = [item.stock_open for item in self.stockitems]
        highs = [item.stock_high for item in self.stockitems]
        opens = [item.stock_open for item in self.stockitems]
        closes = [item.stock_close for item in self.stockitems]
        return dates, lows, highs, opens, closes

class StockItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_date = db.Column(db.String, unique=False, nullable=False)
    stock_open = db.Column(db.Float, unique=False, nullable=False)
    stock_high = db.Column(db.Float, unique=False, nullable=False)
    stock_low = db.Column(db.Float, unique=False, nullable=False)
    stock_close = db.Column(db.Float, unique=False, nullable=False)
    stock_volume = db.Column(db.Float, unique=False, nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)

    def __repr__(self):
        return f"{self.id}/{self.stock_open}"