import logging
import urllib.parse
from hubgrep import db
from sqlalchemy import Index
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hubgrep.models.hosting_service import HostingService

logger = logging.getLogger(__name__)


class Repository(db.Model):
    __tablename__ = "repositories"
    __table_args__ = (Index("repo_index", "foreign_id", "hosting_service_id"),)

    # id on the hosting_service
    foreign_id = db.Column(db.Integer, primary_key=True)
    import_timestamp = db.Column(db.Float, primary_key=True)

    hosting_service_id = db.Column(
        db.Integer, db.ForeignKey("hosting_service.id"), nullable=False, primary_key=True
    )
    hosting_service = db.relationship(
        "HostingService", backref=db.backref("repos", lazy=True)
    )

    namespace = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(500), nullable=False)

    description = db.Column(db.Text(), nullable=True)
    is_fork = db.Column(db.Boolean())
    homepage = db.Column(db.String(500), nullable=True)
    # url to the repo!
    html_url = db.Column(db.String(500), nullable=True)
    language = db.Column(db.String(500), nullable=True)
    forks_count = db.Column(db.Integer(), nullable=True)
    stars_count = db.Column(db.Integer(), nullable=True)
    size = db.Column(db.Integer(), nullable=True)
    open_issues_count = db.Column(db.Integer(), nullable=True)
    is_archived = db.Column(db.Boolean())
    is_disabled = db.Column(db.Boolean())
    pushed_at = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
    subscribers_count = db.Column(db.Integer(), nullable=True)
    license_name = db.Column(db.String(500), nullable=True)

    @classmethod
    def from_dict(cls, d, hosting_service: 'HostingService', import_timestamp):
        if hosting_service.type == "gitea":
            return cls.from_gitea_dict(d, hosting_service, import_timestamp)
        elif hosting_service.type == "github":
            return cls.from_github_dict(d, hosting_service, import_timestamp)
    @classmethod
    def to_unified_dict(cls, d, hosting_service, import_timestamp):
        if hosting_service.type == "gitea":
            return cls.to_unified_from_gitea_dict(d, hosting_service, import_timestamp)
        elif hosting_service.type == "github":
            return cls.to_unified_from_github_dict(d, hosting_service, import_timestamp)

    @classmethod
    def to_unified_from_gitea_dict(cls, d, hosting_service, import_timestamp):
        foreign_id = d["gitea_id"]
        r = {}
        r['hosting_service_id'] = hosting_service.id
        r['foreign_id'] = foreign_id
        r['import_timestamp'] = import_timestamp
        r['name'] = d["name"]
        r['namespace'] = d["owner_username"]
        r['description'] = d["description"]
        r['subscribers_count'] = d['watchers_count']
        # r['is_empty'] = d["empty"]
        r['is_fork'] = d["fork"]
        # r['is_mirror'] = d["mirror"] = self.mirror
        r['size'] = d["size"]
        r['homepage'] = d["website"]
        path_to_user = urllib.parse.urljoin(hosting_service.landingpage_url, r.namespace + "/")
        r['html_url'] = urllib.parse.urljoin(path_to_user, r.name)
        r['stars_count'] = d["stars_count"]
        r['forks_count'] = d["forks_count"]
        r['watchers_count'] = d["watchers_count"]
        r['open_issues_count'] = d["open_issues_count"]
        r['default_branch'] = d["default_branch"]
        r['created_at'] = d["created_at"]
        r['updated_at'] = d["updated_at"]
        return r

    @classmethod
    def to_unified_from_github_dict(cls, d, hosting_service, import_timestamp):
        foreign_id = d["github_id"]
        r = {}
        r['hosting_service_id'] = hosting_service.id
        r['foreign_id'] = foreign_id
        r['import_timestamp'] = import_timestamp
        r['name'] = d["name"]
        r['namespace'] = d["owner_login"]
        r['description'] = d["description"]
        r['is_empty'] = d["is_empty"]
        r['is_fork'] = d["is_fork"]
        # r['is_mirror'] = d["mirror"] = self.mirror
        r['size'] = d["disk_usage"]
        r['homepage'] = d["homepage_url"]
        r['html_url'] = d['url']
        r['stars_count'] = d["stargazer_count"]
        r['forks_count'] = d["fork_count"]
        #r['watchers_count'] = d["watchers_count"]
        #r['open_issues_count'] = d["open_issues_count"]
        #r['default_branch'] = d["default_branch"]
        r['created_at'] = d["created_at"]
        r['updated_at'] = d["updated_at"]
        r['pushed_at'] = d['pushed_at']
        r['license_name'] = d['license_name']
        return r

    @classmethod
    def from_gitea_dict(cls, d, hosting_service, import_timestamp):
        foreign_id = d["gitea_id"]
        r = cls()
        r.hosting_service_id = hosting_service.id
        r.foreign_id = foreign_id
        r.import_timestamp = import_timestamp
        r.name = d["name"]
        r.namespace = d["owner_username"]
        r.description = d["description"]
        r.subscribers_count = d['watchers_count']
        # r.is_empty = d["empty"]
        r.is_fork = d["fork"]
        # r.is_mirror = d["mirror"] = self.mirror
        r.size = d["size"]
        r.homepage = d["website"]
        path_to_user = urllib.parse.urljoin(hosting_service.landingpage_url, r.namespace + "/")
        r.html_url = urllib.parse.urljoin(path_to_user, r.name)
        r.stars_count = d["stars_count"]
        r.forks_count = d["forks_count"]
        r.watchers_count = d["watchers_count"]
        r.open_issues_count = d["open_issues_count"]
        r.default_branch = d["default_branch"]
        r.created_at = d["created_at"]
        r.updated_at = d["updated_at"]
        return r

    @classmethod
    def from_github_dict(cls, d, hosting_service, import_timestamp):
        foreign_id = d["github_id"]
        r = cls()
        r.hosting_service_id = hosting_service.id
        r.foreign_id = foreign_id
        r.import_timestamp = import_timestamp
        r.name = d["name"]
        r.namespace = d["owner_login"]
        r.description = d["description"]
        r.is_empty = d["is_empty"]
        r.is_fork = d["is_fork"]
        # r.is_mirror = d["mirror"] = self.mirror
        r.size = d["disk_usage"]
        r.homepage = d["homepage_url"]
        r.html_url = d['url']
        r.stars_count = d["stargazer_count"]
        r.forks_count = d["fork_count"]
        #r.watchers_count = d["watchers_count"]
        #r.open_issues_count = d["open_issues_count"]
        #r.default_branch = d["default_branch"]
        r.created_at = d["created_at"]
        r.updated_at = d["updated_at"]
        r.pushed_at = d['pushed_at']
        r.license_name = d['license_name']
        return r

