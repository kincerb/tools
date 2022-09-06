#!/usr/bin/env python3
import argparse
import logging
import logging.config
import logging.handlers
from ipaddress import IPv4Address
from pathlib import Path

import requests


def main():
    args = get_args()
    configure_logging(verbosity=args.verbosity)


def get_current_ip(url: str = "https://domains.google.com/checkip") -> IPv4Address:
    try:
        resp = requests.get(url)
    except Exception:
        return
    return IPv4Address(resp.content.decode())


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
