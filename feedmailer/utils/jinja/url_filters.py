from markupsafe import Markup, escape


def url_as_text_filter(value):
    if not value:
        return value

    result = str(escape(value))
    result = result.replace(".", "&period;")
    result = result.replace(":", "&colon;")

    return Markup(result)
