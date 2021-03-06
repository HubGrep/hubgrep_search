# HubGrep

Search for code repositories over many code-hosting services at once, without non-repo clutter.


## Setup

create a config by copying `.env.dist` to `.env`, and add the missing values.

then start the service and database

    docker-compose up


and maybe you want to have a container to run cli commands:

    docker-compose run --rm service /bin/bash

in the container you have to run the db migrations


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