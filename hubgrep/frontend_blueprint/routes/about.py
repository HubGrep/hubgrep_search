import markdown
from flask import render_template
from flask import current_app as app
from flask import render_template_string
from hubgrep.constants import SITE_TITLE
from hubgrep.frontend_blueprint import frontend


about_text = """
# about

HubGrep is a search engine for public code repositories.

Based on a list of code hosting services, it searches through all these services,
and shows you the collected results.

That way its less important where projects are hosted - all sources are treated equally.

Also, HubGrep is free software - you can host your own instance, with your own set of code hosters!

You can find the source code (ironically) [on Github](https://github.com/HubGrep/hubgrep_search").  
If you are hosting projects yourself, consider [adding your instance to our list]({{ url_for('security.login') }}) - we currently support Gitea, Gitlab, and Github!
"""


@frontend.route("/about")
def about():
    # read external markdown file if set
    markdown_file = app.config.get('HUBGREP_ABOUT_MARKDOWN_FILE')
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
        title=SITE_TITLE,
        hosting_instances=app.config["CACHED_HOSTING_SERVICES"],
        about_html=about_html,
    )
