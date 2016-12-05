from blaiog.exceptions import *
from blaiog import config as conf
import blaiog.cli.configuration
import blaiog.cli.db
import argparse
import logging
import sys
import blaiog.blaiog

LOGLEVELS = ["ERROR", "WARNING", "INFO", "DEBUG"]


def main():
    desc = "A python async blogging platform"
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=formatter)
    parser.add_argument('-c', '--config',
                        help="Config file",
                        default="/etc/blaiog/blaiog.yaml")
    parser.add_argument('-v', '--verbose',
                        help="Increase verbosity",
                        action="count", default=1)

    starters = parser.add_mutually_exclusive_group()

    starters.add_argument('--init-database',
                          help="Initialize the database",
                          action="store_true")
    starters.add_argument('--init-config',
                          help="Create a config file containing the defaults",
                          action="store_true")
    starters.add_argument('--add-superuser',
                          help="Add a super user to the database",
                          dest="superuser", metavar="user")
    starters.add_argument('--change-password',
                          help="Change a users password",
                          dest="changepass", metavar="user")
    starters.add_argument('--verify-password',
                          help="Verify a users password",
                          dest="verifypass", metavar="user")

    args = parser.parse_args()

    # Setup logger
    logFormatter = logging.Formatter("%(asctime)s [%(name)s] \
[%(levelname)-5.5s]  %(message)s")
    log = logging.getLogger("blaiog")
    sqllog = logging.getLogger('sqlalchemy.engine')
    sqllog.setLevel(logging.INFO)

    if args.verbose > len(LOGLEVELS):
        args.verbose = len(LOGLEVELS)
    log.setLevel(getattr(logging, LOGLEVELS[args.verbose-1]))
    sqllog.setLevel(getattr(logging, LOGLEVELS[args.verbose-1]))

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    log.addHandler(consoleHandler)
    sqllog.addHandler(consoleHandler)
    if args.init_config:
        blaiog.cli.configuration.init_config(conf, args)

    log.debug("Opening config file {}".format(args.config))
    try:
        config = conf.Config(args.config).get()
    except ConfigNotFoundError as exc:
        log.error(exc)
        exit(1)
    except ConfigNotParsedError as exc:
        log.error("Unable to parse configfile: {}".format(exc))
        exit(1)

    if args.init_database:
        blaiog.cli.db.init_db(config)
        exit(0)
    if args.superuser:
        blaiog.cli.db.create_superuser(config, args)
        exit(0)
    blaiog.blaiog.main(config)
