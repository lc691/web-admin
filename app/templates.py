# app/templates.py
"""Konfigurasi template Jinja2 untuk aplikasi."""

from datetime import datetime

from fastapi.templating import Jinja2Templates

# ================================
# Inisialisasi Template Engine
# ================================

# Membuat instance Jinja2Templates dengan direktori template
templates = Jinja2Templates(directory="templates")

# ================================
# Registrasi Fungsi Global
# ================================

# Fungsi tanggal/waktu
templates.env.globals["now"] = datetime.now

# Fungsi matematika bawaan Python
templates.env.globals["max"] = max
templates.env.globals["min"] = min