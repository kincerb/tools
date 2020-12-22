#!/usr/local/bin/python3.8
import argparse
import http.server
import logging
import logging.config
import logging.handlers
import os
import socketserver

from pathlib import Path


PORT = 8010
LOG_DIR = Path(os.environ.get('HOME')).joinpath('Documents', 'log')
ROOT_DIR = Path(os.environ.get('HOME')).joinpath('Google', 'devbkincer', 'configs')
logger = logging.getLogger(__name__)


def get_args():
    """Parse arguments passed at invocation

    :returns: arguments parsed namespace
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description='Start a simple HTTP server',
        epilog='Example: %(prog)s'
    )
    parser.add_argument('-v', '--verbose',
                        required=False,
                        dest='verbosity',
                        action='count',
                        default=0,
                        help='Increase output verbosity.')
    return parser.parse_args()


def configure_logging(verbosity=0):
    """Configure logging

    :param verbosity: integer representing level of verbosity, starting at 0
    :type verbosity: int
    :returns: None
    """
    level = 'INFO' if verbosity == 0 else 'DEBUG'
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'file': {
                'format': '%(asctime)s %(levelname)-8s %(message)s'
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(LOG_DIR.joinpath('proxy.log')),
                'level': level,
                'formatter': 'file',
                'maxBytes': 1048576,
                'backupCount': 2,
            },
        },
        'loggers': {
            __name__: {
                'level': level,
                'handlers': ['file'],
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(config)


args = get_args()
configure_logging(args.verbosity)


class DirHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)


with socketserver.TCPServer(('127.0.0.1', PORT), DirHandler) as httpd:
    logger.info(f'listening on port {PORT}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Shutting down')
        httpd.socket.close()
