import markdown
from flask import render_template
from flask import current_app as app
from flask import render_template_string
from hubgrep.constants import SITE_TITLE
from hubgrep.frontend_blueprint import frontend


@frontend.route("/about")
def about():
    about_text = """
# about

HubGrep is a search engine for public code repositories.

Based on a list of code hosting services, it searches through all these services,
and shows you the collected results.

That way its less important where projects are hosted - all sources are treated equally.

Also, HubGrep is free software - you can host your own instance, with your own set of code hosters!

You can find the source code (ironically) [on Github](https://github.com/HubGrep/hubgrep_search").  
If you are hosting projects yourself, consider [adding your instance to our list]({{ url_for('security.login') }}) - we currently support Gitea, Gitlab, and Github!


## Funded from March 2021 until August 2021 by

<p style="display: flex; flex-direction: row; justify-content: center; align-items: center;">
    <a href="https://www.bmbf.de/en/" rel="nofollow">
        <img src="{{ url_for('static', filename='images/logos/bmbf_de.jpg') }}" alt="Logo of the German Ministry for Education and Research" style="max-width:100%; padding:20px;" height="150px">
    </a>
    <a href="https://prototypefund.de/en/" rel="nofollow">
        <img src="{{ url_for('static', filename='images/logos/prototype_fund.svg') }}" alt="Logo of the Prototype Fund" style="max-width:100%; padding:20px;" height="150px">
    </a>
</p>
    """

    # read external markdown file if set
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
        title=SITE_TITLE,
        hosting_instances=app.config["CACHED_HOSTING_SERVICES"],
        about_html=about_html,
    )
