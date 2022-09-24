#!/usr/bin/env python3
import argparse
import logging
import logging.config
import logging.handlers
from ipaddress import IPv4Address

import requests


def main():
    args = get_args()
    configure_logging(verbosity=args.verbosity)


def get_local_ip(url: str = "https://domains.google.com/checkip") -> IPv4Address:
    """Return the current IP seen from the outside.

    Args:
        url (str):
            URL to use that returns the IP from the client
            Default: "https://domains.google.com/checkip"

    Returns:
        ipaddress (IPv4Address)
    """
    try:
        resp = requests.get(url)
    except Exception:
        raise
    return IPv4Address(resp.content.decode())


def get_domain_ip(domain: str = "int.nucoder.io") -> IPv4Address:
    """Return the current IP that the domain resolves to.

    Args:
        domain (str):
            Domain to resolve and return
            Default ("int.nucoder.io")
    Returns:
        ipaddress (IPv4Address)
    """
    return IPv4Address("127.0.0.1")


def get_args() -> argparse.Namespace:
    """Parse arguments passed at invocation.

    Returns:
        argparse.Namespace
    """
    parser = argparse.ArgumentParser(description="Manage dynamic DNS for nucoder.io")
    parser.add_argument("action", type=str, choices=["check", "update"], help="Action to perform")
    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        dest="verbosity",
        action="count",
        default=0,
        help="Increase output verbosity.",
    )
    return parser.parse_args()


def configure_logging(verbosity: int = 0) -> None:
    """Configure logging.

    Args:
        verbosity (int):
            Integer representing level of verbosity
            Default: 0

    Returns:
        None
    """
    level = "INFO" if verbosity == 0 else "DEBUG"
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"console": {"format": "%(levelname)-8s %(message)s"}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "console",
            }
        },
        "loggers": {"root": {"level": level, "handlers": ["console"], "propagate": False}},
    }
    logging.config.dictConfig(config)


if __name__ == "__main__":
    main()
# vim:ts=4 sw=4 sts=4
