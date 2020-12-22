#!/usr/bin/env python3.8
import argparse
import logging
import logging.config
import os
import sys
from pathlib import Path
from time import sleep
import sshtunnel

LOG_DIR = Path(os.environ.get('HOME')).joinpath('Documents', 'log')
logger = logging.getLogger(__name__)
logger = sshtunnel.create_logger(logger)


def main():
    args = get_args()
    configure_logging(args.verbosity)
    create_tunnel(args.hostname, args.private_key, args.remote_port, args.local_port, username=args.user)


def create_tunnel(hostname, private_key,
                  remote_bind_port, local_bind_port,
                  username=None, remote_bind_ip='127.0.0.1', local_bind_ip='0.0.0.0'):
    """
    Establish tunnel for remote port forwading

    Arguments:
        hostname (str):
            Target host to create tunnel
        private_key (str):
            Path to private key file
        remote_bind_port (int):
            Port to forward on remote server
        local_bind_port (int):
            Port to listen to locally, forwarding to remote port

    Keyword Arguments:
        username (str):
            Username for authentication
            Default: ``None``
        remote_bind_ip (str):
            IP to bind to on remote server
            Default: '127.0.0.1'
        local_bind_ip (str):
            IP to bind to on local server
            Default: '0.0.0.0'

    Example:
        >>> create_tunnel('nuc', '~/.ssh/kincerb_forward', 443, 8888)
    """
    if not _private_key_verified(private_key):
        return

    while True:
        try:
            tunnel = sshtunnel.open_tunnel(
                hostname,
                ssh_username=username,
                ssh_pkey=private_key,
                allow_agent=False,
                remote_bind_address=(remote_bind_ip, remote_bind_port),
                local_bind_address=(local_bind_ip, local_bind_port),
                set_keepalive=120.0
            )
        except (sshtunnel.BaseSSHTunnelForwarderError, sshtunnel.HandlerSSHTunnelForwarderError) as err:
            logger.error(err)
            sleep(60)
            continue
        except KeyboardInterrupt:
            logger.info('CTRL-C caught, exiting.')
            tunnel.close()
            sys.exit(0)
        except Exception as err:
            logger.error(err)
            sleep(60)
            continue
        else:
            logger.info(f'Initial tunnel established')

        while True:
            try:
                tunnel.check_tunnels()
                success_msg = 'restarted'
                try:
                    if not any(tunnel.tunnel_is_up.values()):
                        tunnel.start()
                    else:
                        success_msg = 'still up'
                except (sshtunnel.BaseSSHTunnelForwarderError, sshtunnel.HandlerSSHTunnelForwarderError) as err:
                    logger.error(err)
                    sleep(60)
                    continue
                except Exception as err:
                    logger.error(err)
                    tunnel.close()
                    sleep(60)
                    break
                else:
                    logger.info(f'Tunnel {success_msg}')
                    sleep(300)
            except KeyboardInterrupt:
                logger.info('CTRL-C caught, exiting.')
                tunnel.close()
                sys.exit(0)


def _private_key_verified(key_path):
    """
    Verify private key exists

    Arguments:
        key_path (str):
            Path to private key
    Return:
        boolean
    """
    private_key = Path(key_path).expanduser()
    return private_key.exists()


def get_args():
    """Parse arguments passed at invocation

    Return:
        argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description='Create ssh tunnel for remote port forwarding',
        epilog='Example: %(prog)s'
    )
    parser.add_argument('-u', '--user',
                        dest='user',
                        required=False,
                        default=None,
                        help='Username')
    parser.add_argument('-s', '--server',
                        dest='hostname',
                        required=True,
                        help='Hostname of server')
    parser.add_argument('-p', '--private-key',
                        dest='private_key',
                        required=True,
                        help='Path to private key')
    parser.add_argument('--remote-port',
                        dest='remote_port',
                        required=True,
                        type=int,
                        help='Port to forward from server')
    parser.add_argument('--local-port',
                        dest='local_port',
                        required=True,
                        type=int,
                        help='Port to forward from localhost')
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
                'filename': str(LOG_DIR.joinpath('ssh-connd.log')),
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


if __name__ == '__main__':
    main()
