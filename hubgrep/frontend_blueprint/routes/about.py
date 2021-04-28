""" About page route. """

import markdown
from flask import render_template
from flask import current_app as app
from flask import render_template_string
from hubgrep.frontend_blueprint import frontend


@frontend.route("/about")
def about():
    contact_description = app.config["CONTACT_DESCRIPTION"]
    contact_address = app.config["CONTACT_ADDRESS"]
    contact_email = app.config["CONTACT_EMAIL"]
    contact_phone = app.config["CONTACT_PHONE"]

    # read external markdown file
    markdown_file = app.config.get("ABOUT_MARKDOWN_FILE")
    if markdown_file:
        with open(markdown_file) as f:
            about_text = f.read()

    # render jinja stuff in the markdown text first
    jinja_rendered_about = render_template_string(about_text)

    # then, render the markdown
    about_html = markdown.markdown(jinja_rendered_about)

    # in the template, we need to add the "safe" filter, otherwise our html will be escaped
    return render_template(
        "about/about.html",
        hosting_instances=app.config["CACHED_HOSTING_SERVICES"],
        contact_description=contact_description,
        contact_address=contact_address,
        contact_email=contact_email,
        contact_phone=contact_phone,
        about_html=about_html,
    )
