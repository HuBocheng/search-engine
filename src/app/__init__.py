from flask import Flask
from markupsafe import Markup, escape

app = Flask(__name__, static_folder="../../static")
app.secret_key = "'62a6e03e2988675819fa418551b488c0'"

from app import routes
