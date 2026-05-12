from flask import render_template
from flask_smorest import Blueprint
from GameBaseAPI.extensions import limiter

html_bp = Blueprint("html", __name__, url_prefix="/", description="loads HTML pages, not for Swagger usage")


# ===== PROFILE =====

@html_bp.route("/profile")
def profile_page():
    return render_template("profile/profile.html")


@html_bp.route("/profile/update")
def update_profile_page():
    return render_template("profile/update_profile.html")


@html_bp.route("/profile/delete")
def delete_profile_page():
    return render_template("profile/delete_profile.html")


# ===== AUTH =====

@html_bp.route("/registration-page")
def registration_page():
    return render_template("registration.html")


# ===== GAMES (LISTING) =====

@html_bp.route("/all-games")
def all_games_page():
    return render_template("games/get.html")


@html_bp.route("/developer-games")
def developer_games_page():
    return render_template("games/get_by_developer.html")


@html_bp.route("/my-games")
def my_games_page():
    return render_template("games/get_my_games.html")


@html_bp.route("/genres-games")
def genre_games_page():
    return render_template("games/get_by_genre.html")


# ===== GAME DETAILS =====

@html_bp.route("/game-page/<int:game_id>")
def game_page(game_id):
    return render_template("games/game_page.html", game_id=game_id)


@html_bp.route("/developers/<int:dev_id>/game-page/<int:game_id>")
def developer_game_page(dev_id, game_id):
    return render_template("games/game_page.html", dev_id=dev_id, game_id=game_id)


@html_bp.route("/developer/<int:dev_id>/game-page/<int:game_id>")
def my_developer_game_page(dev_id, game_id):
    return render_template("games/my_game_page.html", dev_id=dev_id, game_id=game_id)


@html_bp.route("/genres/<int:gr_id>/game-page/<int:game_id>")
def genre_game_page(gr_id, game_id):
    return render_template("games/game_page.html", gr_id=gr_id, game_id=game_id)


# ===== GAME REPORT =====

@html_bp.route("/game-report-page/<int:game_id>")
def game_report_page(game_id):
    return render_template("games/report_game.html", game_id=game_id)


@html_bp.route("/developers/<int:dev_id>/game-report-page/<int:game_id>")
def developer_game_report_page(dev_id, game_id):
    return render_template("games/report_game.html", dev_id=dev_id, game_id=game_id)


@html_bp.route("/developer/<int:dev_id>/game-report-page/<int:game_id>")
def my_game_report_page(dev_id, game_id):
    return render_template("games/report_game.html", dev_id=dev_id, game_id=game_id)


@html_bp.route("/genres/<int:gr_id>/game-report-page/<int:game_id>")
def genre_game_report_page(gr_id, game_id):
    return render_template("games/report_game.html", gr_id=gr_id, game_id=game_id)


# ===== REVIEWS =====

@html_bp.route("/games/<int:game_id>/reviews-page")
def reviews_page(game_id):
    return render_template("games/get_reviews.html", game_id=game_id)


@html_bp.route("/developers/<int:dev_id>/games/<int:game_id>/reviews-page")
def developer_reviews_page(dev_id, game_id):
    return render_template("games/get_reviews.html", dev_id=dev_id, game_id=game_id)


@html_bp.route("/developer/<int:dev_id>/games/<int:game_id>/reviews-page")
def my_developer_reviews_page(dev_id, game_id):
    return render_template("games/get_reviews.html", dev_id=dev_id, game_id=game_id)


@html_bp.route("/genres/<int:gr_id>/games/<int:game_id>/reviews-page")
def genre_reviews_page(gr_id, game_id):
    return render_template("games/get_reviews.html", gr_id=gr_id, game_id=game_id)


# ===== GAME CRUD =====

@html_bp.route("/create-game")
def create_game_page():
    return render_template("games/post_game.html")


@html_bp.route("/all-games/update-game/<int:game_id>")
def update_game_page(game_id):
    return render_template("games/update_game.html", game_id=game_id)


@html_bp.route("/developer/update-game/<int:game_id>")
def my_update_game_page(game_id):
    return render_template("games/update_game.html", game_id=game_id)

@html_bp.route("/developers/<int:dev_id>/update-game/<int:game_id>")
def developer_update_game_page(dev_id, game_id):
    return render_template("games/update_game.html", dev_id=dev_id, game_id=game_id)


@html_bp.route("/genres/<int:gr_id>/update-game/<int:game_id>")
def genre_update_game_page(gr_id, game_id):
    return render_template("games/update_game.html", gr_id=gr_id, game_id=game_id)


@html_bp.route("/delete-game/<int:game_id>")
def delete_game_page(game_id):
    return render_template("games/delete_game.html", game_id=game_id)


# ===== DEVELOPERS =====

@html_bp.route("/developer-profile-page")
def developer_profile_page():
    return render_template("developer_profile/get.html")


@html_bp.route("/create-developer-profile-page")
def create_developer_profile_page():
    return render_template("developer_profile/create.html")


@html_bp.route("/update-developer-profile-page")
def update_developer_profile_page():
    return render_template("developer_profile/update.html")


@html_bp.route("/developers/update-developer-profile-page/<int:dev_id>")
def update_other_developer_profile_page(dev_id):
    return render_template("developer_profile/update_other.html", dev_id=dev_id)


@html_bp.route("/delete-developer-profile-page")
def delete_developer_profile_page():
    return render_template("developer_profile/delete.html")


@html_bp.route("/all-developers")
def all_developers_page():
    return render_template("developer_profile/get_all.html")


# ===== GENRES =====

@html_bp.route("/all-genres")
def all_genres_page():
    return render_template("genres/get_all.html")


@html_bp.route("/create-genre")
def create_genre_page():
    return render_template("genres/create.html")