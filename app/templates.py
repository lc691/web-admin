# app/templates.py
from datetime import datetime

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
templates.env.globals["now"] = datetime.now  # global "now()" untuk semua template

# Tambahkan fungsi Python ke Jinja
templates.env.globals["max"] = max
templates.env.globals["min"] = min
