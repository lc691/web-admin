def set_flash(request, message: str, category: str = "success"):
    request.session["_flash"] = {
        "message": message,
        "category": category,
    }


def get_flash(request):
    flash = request.session.pop("_flash", None)
    return flash
