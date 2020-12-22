#!/usr/bin/env python3
import argparse
import logging
import logging.config
import logging.handlers
import os
import sys

logger = logging.getLogger(__name__)


class EnvError(Exception):
    """Exception thrown when there was an environment issue"""
    pass


def main():
    args = get_args()
    configure_logging(verbosity=args.verbosity)
    try:
        personal_user, personal_password = get_creds(args.url)
    except EnvError as err:
        logger.critical(str(err))
        sys.exit(1)

    if args.operation == 'get':
        print_creds(personal_user, personal_password)


def get_creds(url):
    """Get credentials from shell environment

    :param url: repo base url
    :type url: str
    :returns: personal_user, personal_password
    :rtype: tuple
    :raises EnvError: When variables are missing
    """
    if url == 'https://github.com':
        id = 'GITHUB_PERSONAL_ID'
        token = 'GITHUB_PERSONAL_TOKEN'
    else:
        id = 'GITHUB_WORK_ID'
        token = 'GITHUB_WORK_TOKEN'
    reqd_vars = [id, token]
    env_vars = list(os.environ)
    missing_vars = []

    for var in reqd_vars:
        if var not in env_vars:
            missing_vars.append(var)
    if missing_vars:
        raise EnvError('Missing environment variables: {}'.format(', '.join(missing_vars)))

    return (os.environ.get(id), os.environ.get(token))


def print_creds(personal_user, personal_password):
    """Print out credentials"""
    print(f'username={personal_user}')
    print(f'password={personal_password}')


def get_args():
    """Parse arguments passed at invocation

    :returns: arguments parsed namespace
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description='Git credential helper',
        epilog='Example: %(prog)s get'
    )
    parser.add_argument('operation',
                        action='store',
                        type=str,
                        help='Git action (get|store|erase)')
    parser.add_argument('-u', '--url',
                        required=True,
                        dest='url',
                        action='store',
                        help='Repo base url')
    parser.add_argument('-v', '--verbose',
                        required=False,
                        dest='verbosity',
                        action='count',
                        default=0,
                        help='Increase output verbosity.')
    return parser.parse_args()


def configure_logging(verbosity=0):
    """
    Configure logging

    :param verbosity: integer representing level of verbosity, starting at 0
    :type verbosity: int
    :returns: None
    """
    level = 'INFO' if verbosity == 0 else 'DEBUG'
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(levelname)-8s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'console',
            }
        },
        'loggers': {
            __name__: {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(config)


if __name__ == '__main__':
    main()
