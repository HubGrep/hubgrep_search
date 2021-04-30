# HubGrep

Search for code repositories over many code-hosting services at once. 

This means you don't have to mentally filter non-repo results in view, but perhaps more importantly, 
one service does not get prioritized over another in non-transparent ways - they're all equal to one another with HubGrep.


Try it on [hubgrep.io](https://hubgrep.io/)

[![Documentation Status](https://readthedocs.org/projects/hubgrep-documentation/badge/?version=latest)](https://docs.hubgrep.io/en/latest/?badge=latest)

## Supported services
 
Currently supported service types:

* Github
* Gitlab
* Gitea

A code-hosting service, or hosting-service from now on; is an external site which host code repositories that 
HubGrep support for its searches.

Individual instances of these need to be added manually to HubGrep (see [Adding service-hosters](#adding-service-hosters)).

## Deployment

### Setup (Docker)

#### Creating your configuration

Create a config by copying `.env.dist` to `.env` and add the missing values.

Next, there is a`docker-compose.prod.yml` file, which would start an instance of HubGrep. 
It contains redis db for caching, and postgres to store user data such as service-hosters which have been added.

You should check if the dockerfile contain the configuration you want 
(maybe you want to use another database, for example).

Also, it might be a good idea to make a copy of this dockerfile, so that you dont run into conflicts when pulling new 
versions of this repo.


#### First start

To build an image with generated assets and source code baked in, 
run:

    docker-compose -f docker-compose.prod.yml build
  
Note: This is not needed the first time you start,
but to trigger building the container after an update to a new version this is neccessary.

To start the containers (HubGrep and needed services), run

    docker-compose -f docker-compose.prod.yml up

(or add a `-d` to detach).

On first setup, you need to setup the database and the admin user.
Easiest is, to run a new shell in the container:

    docker-compose -f docker-compose.prod.yml run --rm service /bin/bash

and in there, run:

    flask db upgrade
    flask cli init

The first command migrates the database (creating the database structure that we use), 
the second one creates an admin user as defined in the environment variables.


Afterwards, the service should be accessible on `http://yourip:8080`.


#### Adding service-hosters 

Add hosting-services to enable HubGrep to search for results. Use either the web-frontend 
or the CLI. Hosting-services are tied to the current user while adding them; CLI always uses admin while web-frontend requires a login.
 
Adding via CLI (from within container shell):

    flask cli add-hoster github "https://api.github.com/" "https://github.com/" "{}"
    flask cli add-hoster gitea "https://codeberg.org/api/v1/" "https://codeberg.org/" "{}"
    flask cli add-hoster gitea "https://gitea.com/api/v1/" "https://gitea.com/" "{}"

(For gitlab, see [Adding Gitlab Instances](#adding-gitlab-instances))


#### Nginx setup

You likely want to serve via web-server, not with gunicorn (which serves the app, unless changed in the docker-compose file). 

We recommended you do this so that you can add a certificate for https, and serve assets more efficiently. 

To get the static files, there is an example setup in `docker-compose.prod.yml` already.
Just uncomment the "volumes" section in the compose file, and the `STATIC_PATH` in your `.env`.
This would copy the static files to `./host_static` on startup.

Alternatively, you can run `flask cli copy-static /some/path` inside the container.

You can find an example nginx config [here](./nginx_example.conf).


#### Customizing the About Page

Set environment variable `HUBGREP_ABOUT_MARKDOWN_FILE` to a path containing a markdown file,
and it will be rendered into the about page.


#### Adding Gitlab Instances

Gitlab needs an api key ("token") to use the api.

> ! keep in mind, that with this token, your private repositories can be read as well
> so its recommended to create a new, empty user account for this !

To create a new token:
* log in to your Gitlab account
* find "access tokens" in your user settings, and create a new "personal access token" 
without an expiration date, and with the `read_api` scope.

After you creating your key, add it via CLI as such:
    
    flask cli add-hoster gitlab "https://gitlab.com/api/v4/" "https://gitlab.com/" '{"api_token": "XXXXXXXXXXX"}'
    
Substitute the base url with the url to the Gitlab instance you want to add.

For web-frontend, the add the last parameter in the "config" field (including brackets).


## Development Setup

### Web-frontend:

    docker-compose up

Navigate to `0.0.0.0:8080` in your browser to search. The config for what is included is found in `docker-compose.yml`.


### CLI:

To use the CLI, you must first have a shell inside a running container. Run:

    docker-compose run --rm service /bin/bash

Once inside, run:

    flask cli search <TERMS>


## Testing

Using pytest and pytest-coverage, run:

    ./manage.sh test
    

## Localization

Using Flask-Babel, we generate catalogues by first extracting strings from the application. Strings from templates and
from code which uses "gettext" will be extracted into a .pot file which we then fill in translations for.

* First extract:

        pybabel extract -F babel.cfg -o messages.pot hubgrep

* MANUALLY fill in translation texts in empty "msgstr" fields in the `.pot` file.
* Update existing localization file or init a new one (if the lang doesn't previously exist in `/hubgrep/translations):
  
  Note: `YOUR_LANG` will be matched against language codes as recieved from Accept-Language in request headers. 
        These should resolve to defaults if specific header lang is not found; example `de-DE` should still use the `de` translation if not found. Finally, strings from code and templates are used as a last default.

        pybabel init -l [YOUR_LANG] -i messages.pot -d hubgrep/translations
        
        - OR -
        
        pybabel update -i messages.pot -d hubgrep/translations
    
* Lastly, compile the localization file for usage:

        pybabel compile -d hubgrep/translations -l [YOUR_LANG]
    
Strings should now be replaced by the appropriate locale variant when rendered.


# Funded from March 2021 until August 2021 by

<p align="center">
    <a href="https://www.bmbf.de/en/" rel="nofollow">
        <img src="hubgrep/static/images/logos/bmbf_en.jpg" alt="Logo of the German Ministry for Education and Research" style="max-width:100%;" height="150px">
    </a>
    &nbsp; &nbsp; &nbsp; &nbsp;
    <a href="https://prototypefund.de/en/" rel="nofollow">
        <img src="hubgrep/static/images/logos/prototype_fund.svg" alt="Logo of the Prototype Fund" style="max-width:100%;" height="150px">
    </a>
</p>
