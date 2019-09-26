#!/usr/bin/python3

from ldap3 import Server, Connection
from ldap3.utils.dn import to_dn
from os import path, scandir, symlink
import radicale


def create_collection(user,
                      displayname,
                      calendar_description,
                      color="#a1bc9bff"):
    props = {
        "C:calendar-description": calendar_description,
        "C:supported-calendar-component-set": "VEVENT,VJOURNAL,VTODO",
        "D:displayname": displayname,
        "ICAL:calendar-color": color,
        "tag": "VCALENDAR",
        "is_group_calendar": True,
    }
    uuid = radicale.storage.random_uuid4()
    Collection.create_collection(path.join(user, uuid), props=props)


def get_ldap_users(group, connection, ldap_conf):
    group_base = ldap_conf["group_base"]
    group_filter = ldap_conf["group_attribute"] + "=" + group
    found_group = connection.search(
        group_base,
        "({})".format(group_filter),
        attributes=["member"],
        search_scope=ldap_conf.get("ldap_scope", fallback="SUBTREE"),
    )
    if not found_group:
        raise RuntimeError("Group {},{} could not be found!").format(
            group_filter, group_base)
    user_dns = connection.entries[0].member
    return [to_dn(dn, decompose=True)[0][1] for dn in user_dns]


def visible_subdirs(path):
    return [p.name
            for p in scandir(path)
            if not p.name.startswith(".") and p.is_dir()]


# Create collection for every group in calendar_groups,
# if it doesn't already exists
def create_group_calendar(group):
    collections = list(Collection.discover(group, depth=1))
    group_calendar_exists = False
    for collection in collections:
        if collection.get_meta().get("is_group_calendar", False):
            group_calendar_exists = True
    if not group_calendar_exists:
        create_collection(
            group,
            "{} group calendar".format(group),
            "Default group calendar of {}".format(group),
        )


# Symlink group directories into user directories
def symlink_group(group):
    collections = visible_subdirs(path.join(storepath, group))
    ldap_users = set(get_ldap_users(group, connection, ldap_conf))
    for user in ldap_users.intersection(radicale_users):
        for collection in collections:
            source = path.join(storepath, group, collection)
            destination = path.join(storepath, user, collection)
            symlink(source, destination)


config = radicale.config.load(["/etc/radicale/config"])
storepath = path.join(config.get("storage", "filesystem_folder"),
                      "collection-root")
radicale_users = visible_subdirs(storepath)
logger = radicale.log.start("radicale", config.get("logging", "config"))
Collection = radicale.storage.load(config, logger)

ldap_conf = config["rights"]
server = Server(ldap_conf["ldap_url"])
calendar_groups = list(map(str.strip,
                           rights_conf["managed_groups"].split(",")))
connection = Connection(server,
                        ldap_conf["ldap_binddn"],
                        ldap_conf["ldap_password"])

connection.bind()


def main():
    for group in calendar_groups:
        create_group_calendar(group)
        symlink_group(group)
    return 0

