# HubGrep

Search for code repositories over many code-hosting services at once, without non-repo clutter.


## Setup

create a config by copying `.env.dist` to `.env`, and add the missing values.

then start the service and database

    docker-compose up


and maybe you want to have a container to run cli commands:

    docker-compose run --rm service /bin/bash

in the container you have to run the db migrations

    # create migration files, 
    # only if you changed something in the models
    #flask db migrate  

    # upgrade your datbase
    flask db upgrade

create the admin user

    


## Usage - localdev

#### Web-fronend:

    docker-compose up

Navigate to `0.0.0.0:8080` in your browser to search.

#### CLI:

```
docker-compose run --rm service /bin/bash
flask cli search <TERMS>
```


## Testing

Using pytest and pytest-coverage, run:

    pytest --cov=hubgrep .
    
    
## Deploy

TODO

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
