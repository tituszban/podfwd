import os
from flask import redirect, Response
from . import app

from email_exporter.feed_endpoint import get_feed_rss

DEFAULT_REDIRECT = "https://www.podfwd.com"


@app.route("/")
def redirect_index():
    redirect_to = os.environ.get("REDIRECT_TO", DEFAULT_REDIRECT)
    return redirect(redirect_to)


@app.route("/<feed_name>", methods=["GET"])
def get_feed_name(feed_name):
    try:
        rss = get_feed_rss(feed_name)
    except KeyError:
        return "Feed not found", 404

    return Response(rss, mimetype="text/xml")


@app.route("/favicon.ico")
def favicon():
    redirect_to = os.environ.get("REDIRECT_TO", DEFAULT_REDIRECT)
    return redirect(f"{redirect_to}/favicon.ico")
