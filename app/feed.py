import os
from flask import Blueprint, redirect, Response

from email_exporter.feed_endpoint import get_feed_rss

DEFAULT_REDIRECT = "https://www.podfwd.com"


feed_blueprint = Blueprint("feed", __name__)


@feed_blueprint.route("/")
def redirect_index():
    redirect_to = os.environ.get("REDIRECT_TO", DEFAULT_REDIRECT)
    return redirect(redirect_to)


@feed_blueprint.route("/<feed_name>", methods=["GET"])
def get_feed_name(feed_name):
    try:
        rss = get_feed_rss(feed_name)
    except KeyError:
        return "Feed not found", 404

    return Response(rss, mimetype="text/xml")


@feed_blueprint.route("/favicon.ico")
def favicon():
    redirect_to = os.environ.get("REDIRECT_TO", DEFAULT_REDIRECT)
    return redirect(f"{redirect_to}/favicon.ico")
