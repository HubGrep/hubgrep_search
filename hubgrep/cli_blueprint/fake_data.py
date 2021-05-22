import os
import faker
import time
from faker import Faker
from faker.providers import lorem

from hubgrep.models import HostingService, Repository
from hubgrep import security
from hubgrep import db


fake = Faker()
fake.add_provider(lorem)


def create_instance_data(hosting_service: HostingService):
    # create 10 mio repos
    owners = 10
    batch_size = 1_000_000 # repos
    all_in_all_repos = owners * batch_size
    for owner_id in range(owners):
        time_before = time.time()
        print(f"{owner_id} / {owners}")
        print(f"creating next {batch_size} of {all_in_all_repos} @{time.time()}")
        new_repos = []
        for r in range(batch_size):
            new_repos.append(Repository.from_fake(fake, hosting_service))
        
        print(f"generating took {time.time() - time_before})")
        time_before = time.time()
        db.session.bulk_save_objects(new_repos)
        print(f"storing took {time.time() - time_before})")
        db.session.commit()


def add_hoster(type, api_url, landingpage_url, config):
    admin_email = os.environ["HUBGREP_ADMIN_EMAIL"]
    admin = security.datastore.find_user(email=admin_email)
    if not admin:
        print(
            'admin user not found. set the HUBGREP_ADMIN_EMAIL envvar and run "flask cli init"!'
        )
        exit(0)

    h = HostingService.query.filter_by(api_url=api_url).first()
    if not h:
        h = HostingService()
        h.user_id = admin.id
        h.type = type

        # todo: validate
        h.api_url = api_url
        h.landingpage_url = landingpage_url
        h.config = config
        h.set_service_label()

        print(f"adding {h.api_url}")

        db.session.add(h)
        db.session.commit()
    return h


import click
from hubgrep.cli_blueprint import cli_bp


import shutil


@cli_bp.cli.command(help="create some fake data to search")
def create_dummydata():
    db.engine.dialect.psycopg2_batch_mode = True
    fake_hosters_dict = [
        dict(
            type="sphinx",
            api_url="https://fakehoster.com/api",
            landingpage_url="https://fakehoster.com/",
            config="{}",
        )
    ]
    for hoster_dict in fake_hosters_dict:
        hoster = add_hoster(**hoster_dict)
        create_instance_data(hoster)
