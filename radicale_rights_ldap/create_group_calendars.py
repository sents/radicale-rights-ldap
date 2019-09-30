#!/usr/bin/python3

from os import path, scandir, symlink
import radicale
import sys


def create_collection(collection_class,
                      user,
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
    collection_class.create_collection(path.join(user, uuid), props=props)


def visible_subdirs(path):
    return [p.name
            for p in scandir(path)
            if not p.name.startswith(".") and p.is_dir()]


# Create collection for every group in calendar_groups,
# if it doesn't already exists
def create_group_calendar(group, collection_class):
    collections = list(collection_class.discover(group, depth=1))
    group_calendar_exists = False
    for collection in collections:
        if collection.get_meta().get("is_group_calendar", False):
            group_calendar_exists = True
    if not group_calendar_exists:
        create_collection(
            collection_class,
            group,
            "{} group calendar".format(group),
            "Default group calendar of {}".format(group),
        )


def main():
    config = radicale.config.load([sys.argv[1]])
    storepath = path.join(config.get("storage", "filesystem_folder"),
                          "collection-root")
    radicale_users = visible_subdirs(storepath)
    logger = radicale.log.start("radicale", config.get("logging", "config"))
    Collection = radicale.storage.load(config, logger)
    rights_conf = config["rights"]
    calendar_groups = list(map(str.strip,
                               rights_conf["managed_groups"].split(",")))
    for group in calendar_groups:
        create_group_calendar(group, Collection)
    return 0


if __name__ == "__main__":
    main()
