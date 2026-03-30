import os.path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from feedmailer.utils.jinja.url_filters import url_as_text_filter


def create_jinja_environment():
    env = Environment(
        loader=FileSystemLoader(get_template_dir()),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters.update(get_filters())
    return env


def get_template_dir():
    my_path = os.path.dirname(__file__)
    return os.path.join(my_path, "../../templates")


def get_filters():
    return {"url_as_text": url_as_text_filter}
