from demo.homepage import bp


@bp.route("/")
def home():
    return "Hello"