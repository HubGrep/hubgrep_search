# HubGrep Metasearch

WIP


backend for various crawlers


## dev setup

create a config by copying `.env.dist` to `.env`, and add the missing values.

then start the service and database

    docker-compose up


and maybe you want to have a container to run cli commands:

    docker-compose run --rm service /bin/bash

in the container you have to run the db migrations



## running a search

right now only via cli:

```
docker-compose run --rm service /bin/bash
flask cli search <TERMS>
```


