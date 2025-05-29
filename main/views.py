from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from django.contrib import messages
from urllib.parse import urlparse


load_dotenv(override=True)

# DB_POOL = psycopg2.pool.SimpleConnectionPool(
#     1, 20,
#     dbname=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),
#     host=os.getenv("DB_HOST"),
#     port=os.getenv("DB_PORT"),
#     options="-c search_path=sizopi"
# )
db_url = os.getenv("DATABASE_URL")
parsed = urlparse(db_url)

DB_POOL = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    dbname=parsed.path.lstrip('/'),
    user=parsed.username,
    password=parsed.password,
    host=parsed.hostname,
    port=parsed.port,
    options='-c search_path=sizopi'
)


def get_db_connection():
    conn = DB_POOL.getconn()
    with conn.cursor() as cur:
        cur.execute("SET search_path TO sizopi")
    return conn

def release_db_connection(conn):
    DB_POOL.putconn(conn)

def main_view(request):
    user = request.session.get("user", {})
    is_authenticated = request.session.get("is_authenticated", False)

    context = {
        "is_logged_in": is_authenticated,
        "user_role": user.get("role", ""),
        "is_adopter": user.get("is_adopter", False),
        "username": user.get("username", ""), 
    }
    return render(request, "main.html", context)


def homepage(request):
    context = {
        "is_logged_in": False,
        "user_role": "",
        "is_adopter": False,
    }

    if request.session.get("is_authenticated"):
        user = request.session.get("user", {})
        context["is_logged_in"] = True
        context["user_role"] = user.get("role", "")
        context["is_adopter"] = user.get("is_adopter", False)  # opsional

    return render(request, "home.html", context)