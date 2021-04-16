# HubGrep

Search for code repositories over many code-hosting services at once, without non-repo clutter.


## Deployment

### Setup (Docker)

#### Creating your configuration

Create a config by copying `.env.dist` to `.env`, 
and add the missing values.

Next, there is a`docker-compose.prod.yml` file, 
which would start an instance of hubgrep. along with a redis db for caching,
and postgres to store user data, like hosters you want to include in your searches.

You should check if this is running the configuration you want (maybe you want to use another database, for example).

Also, it might be a good idea to make a copy of that file to use, 
so that you dont run into conflicts when pulling new versions of this repo.

#### First start

To build an image with generated assets and source code baked in, 
run `docker-compose -f docker-compose.prod.yml build`.  
This is not needed the first time you start,
but to trigger building the container after an update to a new version this is neccessary.

To start the containers, run

    docker-compose -f docker-compose.prod.yml up

(or add a `-d` to detach).


On first setup, you need to setup the database and the admin user.
Easiest is, to run a new shell in the container:

    docker-compose -f docker-compose.prod.yml run --rm service /bin/bash


and in there, run

    flask db upgrade
    flask cli init

The first command migrates the database (meaning, it creates the neccessary tables), 
the second one creates an admin user as defined in the environment variables.


Afterwards, the service should be accessible on `http://yourip:8080`.

#### Adding some hosters

after that, add some hosters to search. use either the frontend, 
or the cli, to add some:

    flask cli add-hoster github "https://api.github.com/" "https://github.com/" "{}"
    flask cli add-hoster gitea "https://codeberg.org/api/v1/" "https://codeberg.org/" "{}"
    flask cli add-hoster gitea "https://gitea.com/api/v1/" "https://gitea.com/" "{}"

(For gitlab, see [this note](#adding-gitlab-instances))

#### Nginx setup

You probably want to serve everything via webserver,
not with gunicorn (the thing that serves the app, 
if you didnt change the docker-compose file), 
so that you can add a certificate for https, 
and to serve the assets more efficiently. 

To get the static files, there is an example setup in `docker-compose.prod.yml` already.
Just uncomment the "volumes" section in the compose file, and the `STATIC_PATH` in your `.env`.
This would copy the static files to `./host_static` on startup.

Alternatively, you can run `flask cli copy-static /some/path` inside the container.

You can find an example nginx config [here](./nginx_example.conf).


#### Customizing the About Page

Set environment variable `HUBGREP_ABOUT_MARKDOWN_FILE` to a path containing a markdown file,
and it will be rendered into the about page.


#### Adding Gitlab Instances

gitlab needs an api key ("token") to use the api.

> ! keep in mind, that with this token, your private repositories can be read as well
> so its recommended to create a new, empty user account for this !

to create a new token, log in to your gitlab account, 
find "access tokens" in your user settings, and create a new "personal access token" 
without an expiration date, and with the `read_api` scope.

after you created your key, you can add this instance as well:
    
    flask cli add-hoster gitlab "https://gitlab.com/api/v4/" "https://gitlab.com/" '{"api_token": "XXXXXXXXXXX"}'


substitute the base url with whatever gitlab instance you want to add, of course. :)



## Development Setup

### Web-fronend:

    docker-compose up

Navigate to `0.0.0.0:8080` in your browser to search.

### CLI:

```
docker-compose run --rm service /bin/bash
flask cli search <TERMS>
```

## Testing

Using pytest and pytest-coverage, run:

    ./manage.sh test
    

## Localization

Using Flask-Babel, we generate catalogues by first extracting strings from the application. Strings from templates and
from code which uses "gettext" (for example) will be extracted into a .pot file which we then fill in translation for.

First extract:

    pybabel extract -F babel.cfg -o messages.pot hubgrep

Then, after MANUALLY filling in translation texts in this file (empty "msgstr" fields), either update existing or init:

    pybabel init -l [YOUR_LANG] -i messages.pot -d hubgrep/translations
    - OR -
    pybabel update -i messages.pot -d hubgrep/translations
    
Finally, compile the translation for usage:

    pybabel compile -d hubgrep/translations -l [YOUR_LANG]
    
Strings should now be replaced by the appropriate locale variant when rendered.



# Funded from March 2021 until August 2021 by

<p style="display: flex; flex-direction: row; justify-content: center; align-items: center; background:#ffffff;">
    <a href="https://www.bmbf.de/en/" rel="nofollow">
        <img src="hubgrep/static/images/logos/bmbf_en.jpg" alt="Logo of the German Ministry for Education and Research" style="max-width:100%; padding:20px;" height="150px">
    </a>
    <a href="https://prototypefund.de/en/" rel="nofollow">
        <img src="hubgrep/static/images/logos/prototype_fund.svg" alt="Logo of the Prototype Fund" style="max-width:100%; padding:20px;" height="150px">
    </a>
</p>
