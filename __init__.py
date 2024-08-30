import hashlib
import copy
import datetime

from flask import render_template_string, abort, request

from CTFd.models import Users
from CTFd.schemas.tokens import TokenSchema
from CTFd.utils.decorators import admins_only
from CTFd.plugins import register_plugin_assets_directory
from CTFd.utils.security.auth import generate_user_token

MAIN_PAGE="""
{% extends "admin/base.html" %}

{% block content %}
<div class="jumbotron">
	<div class="container">
		<h1>Token For</h1>
	</div>
</div>
<div class="container">
    <p>This plugins adds a new API endpoint /token_for which allows admins to create tokens for users</p>
</div>
{% endblock content %}
"""

def load(app):
    # Register route for plugin page
    @app.route("/admin/token_for", methods=["GET"])
    @admins_only
    def token_for_main_page():
        return render_template_string(MAIN_PAGE)

    # Register API route for plugin page
    # Adapted from api/v1/tokens.py (Copyright belongs to CTFd, Apache License)
    @app.route("/api/v1/token_for/<user_id>", methods=["POST"])
    @admins_only
    def create_token_for(user_id):
        req = request.get_json()
        expiration = req.get("expiration")
        description = req.get("description")
        if expiration:
            expiration = datetime.datetime.strptime(expiration, "%Y-%m-%d")

        # Use provided user instead of current user
        user = Users.query.filter_by(id=user_id).first()
        if user is None:
            abort(404)

        token = generate_user_token(
            user, expiration=expiration, description=description
        )

        # Explicitly use admin view so that user's can see the value of their token
        schema = TokenSchema(view="admin")
        response = schema.dump(token)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    # END ADAPTED FROM CTFD tokens.py

    
    # Register assets
    register_plugin_assets_directory(app, base_path="/plugins/token_for/assets")
