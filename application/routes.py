from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .forms import UpdateAccountForm
from . import db, app
import secrets
import os, json
from PIL import Image
import yfinance as yf
from .models import StockItem, Stock
from datetime import datetime
import numpy as np

views = Blueprint('views', __name__)

datetime_dict = {}

@views.route('/', methods=["POST", "GET"])
@login_required
def home():
    context = {
        "stocks": db.session.query(Stock).all(),
        "last_enter": datetime_dict
    }
    return render_template("home.html", user=current_user, context=context)

stock_tickers = ("AAPL", "TSLA", "TWTR", "NVDA", "AMZN", "NFLX")

def load_data(symbol, interval, start, end):
    ticker = yf.Ticker(symbol)
    dataframe = ticker.history(interval=interval, start=start, end=end, actions=False, rounding=True)
    stock = get_or_create_stock(symbol)

    for data in dataframe.index:
        date_string = data.strftime("%Y-%m-%d %H:%M")
        open = dataframe.iloc[:, 0][data]
        high = dataframe.iloc[:, 1][data]
        low = dataframe.iloc[:, 2][data]
        close = dataframe.iloc[:, 3][data]
        volume = dataframe.iloc[:, 4][data]
        stock_open = StockItem(stock_date=date_string, stock_open=open, stock_high=high, stock_low=low, stock_close=close, stock_volume=volume, stock=stock)
        db.session.add(stock_open)
        db.session.commit()

def get_or_create_stock(symbol):
    ticker = yf.Ticker(symbol)
    stock = db.session.query(Stock).filter(Stock.stock_name == symbol).first()
    if not stock:
        long_name = ticker.info.get("longName")
        business_summary = ticker.info.get("longBusinessSummary")
        website = ticker.info.get("website")
        market_cap = ticker.fast_info.get("market_cap")
        open_price = ticker.fast_info.get("open")
        previous_close = ticker.fast_info.get("previous_close")
        currency = ticker.fast_info.get("currency")
        stock_open = Stock(stock_name=symbol, long_name=long_name, business_summary=business_summary, website=website, market_cap=market_cap, open_price=open_price, previous_close=previous_close, currency=currency)
        db.session.add(stock_open)
        db.session.commit()
        return db.session.query(Stock).filter(Stock.stock_name == symbol).first()
    return stock

load_data("TSLA", "1d", "2022-12-01", "2023-01-23")

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_photos', picture_fn)
    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@views.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!")
        return redirect(url_for('views.account'))
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_photos/' + current_user.image_file)
    return render_template("account.html", title="Account", form=form, image_file=image_file)

def simple_moving_average(values, window):
    weights = np.repeat(1.0, window)/window
    smas = np.convolve(values, weights, 'valid')
    return list(smas)

@views.route("/tables/<symbol>")
@login_required
def tables(symbol):
    date_enter = datetime.now()
    format_date = datetime.strftime(date_enter, "%Y-%m-%d %H:%M:%S")
    datetime_dict[symbol] = format_date

    page = request.args.get('page', 1, type=int)
    stock = db.session.query(Stock).filter(Stock.stock_name == symbol).first()
    items = db.session.query(StockItem).filter(StockItem.stock_id == stock.id).paginate(page=page, per_page=20)

    dates, lowes, highs, opens, closes = stock.get_data()
    sma = simple_moving_average(closes, 5)
    context = {
        "stock": stock,
        "stock_items": items,
        "dates": json.dumps(dates),
        "lowes": json.dumps(lowes),
        "highs": json.dumps(highs),
        "opens": json.dumps(opens),
        "closes": json.dumps(closes),
        "page": page,
        "sma": sma
    }
    return render_template("tables.html", context=context, items=items)