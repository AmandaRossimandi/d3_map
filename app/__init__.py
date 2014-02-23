import os
from flask import Flask
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
app.config.from_object('config')
cache = SimpleCache()
from app import views
