
import argparse
import logging
import sys

LOGLEVELS = ["ERROR","WARNING","INFO","DEBUG"]
def main():
    parser = argparse.ArgumentParser(description="A python async blogging platform",
                                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c','--config',
                        help="Config file",
                        default="/etc/blaiog/blaiog.yaml")
    
    parser.add_argument('-v','--verbose',
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
    
    if args.verbose > len(LOGLEVELS):
        args.verbose = len(LOGLEVELS)
    log.setLevel(getattr(logging,LOGLEVELS[args.verbose-1]))

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    log.addHandler(consoleHandler)
    