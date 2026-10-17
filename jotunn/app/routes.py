from flask import Flask, Blueprint, render_template, request
from .player import Player

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("index.html")


@main_bp.route("/main")
def main():
    return render_template("main.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@main_bp.route("/loading")
def load():
    query = request.args.get("q", None)
    return render_template("loading.html", query=query)


@main_bp.route("/player")
def player():
    query = request.args.get("q", None)
    if query is None:
        return render_template("player.html", found=False, data=None)

    player = Player(query)
    if not player.process():
        return render_template("player.html", found=False, data=None)
    else:
        return render_template("player.html", found=True, data=player)


@main_bp.route("/compare")
def compare():
    p1 = request.args.get("p1", None)
    p2 = request.args.get("p2", None)
    if (p1 is None) or (p2 is None):
        return render_template("compare.html", found=False, data=None)

    player_1 = Player(p1)
    player_1.process()
    player_2 = Player(p2)
    player_2.process()

    return render_template(
        "compare.html", found=True, player1=player_1, player2=player_2
    )
