#!/usr/bin/env python3.8
import argparse
import logging
import logging.config
import re
import sys
import statistics

from collections import namedtuple

from pathlib import Path

import tools

logger = logging.getLogger(__name__)
SCRIPT_NAME = Path(__file__).stem
Transaction = namedtuple('Transaction', ('timestamp', 'response_time', 'transaction_string'))


class NotFoundError(Exception):
    """Raised when no regex match was found"""
    pass


def main():
    args = get_args()
    try:
        config = tools.config.create_config()
    except tools.ToolsError as err:
        logger.critical(str(err))
        sys.exit(3)

    log_file = Path(config.defaults().get('log_dir')).joinpath(f'{SCRIPT_NAME}.log').expanduser()
    logging.config.dictConfig(tools.utils.get_log_config(log_file, __name__, verbosity=args.verbosity))
    process_log(Path(args.log_file).expanduser(), args.field, args.max_diff)


def process_log(log_file, field_name, max_diff):
    """Look for all values in log file

    Args:
        log_file (Path): path object of nginx log file
        field_name (str): field to pull out
        max_diff (float): max diff as decimal percentage

    Returns:

    """
    all_transactions = [transaction_info for transaction_info in pull_times(log_file, field_name)]
    resp_time_avg = round(statistics.mean([transaction.response_time for transaction in all_transactions]), 4)
    logger.info(f'{len(all_transactions)} entries, with an avg of {round(resp_time_avg, 4)}')
    long_resp_time = round(resp_time_avg * max_diff, 4)
    logger.info(f'Looking for response times greater than {long_resp_time}')
    for transaction in all_transactions:
        if transaction.response_time > long_resp_time:
            logger.info(f'{transaction.timestamp} {transaction.transaction_string} '
                        f'{field_name}={transaction.response_time}')


def pull_times(log_file, field_name):
    """Pull value of regex out of line in log

    Args:
        log_file (Path): path object of nginx log file
        field_name (str): upstream field

    Returns:
        collections.Iterable[Transaction]: namedtuple of results
    """
    response_regex = re.compile(r'{}="(?P<response_time>\S+)"'.format(field_name))
    timestamp_regex = re.compile(r'(?P<time_stamp>^.*)\s+elvmt0049\s+dockerd')
    transaction_regex = re.compile(r'\]\s+"(?P<transaction_string>\w+.*\s+aiohttp\S+)"')

    try:
        with log_file.open() as f:
            for _line in f:
                response_match = response_regex.search(_line)
                timestamp_match = timestamp_regex.search(_line)
                transaction_match = transaction_regex.search(_line)
                if not all((response_match, timestamp_match, transaction_match)):
                    continue
                try:
                    response_time = float(response_match.group('response_time'))
                    timestamp = timestamp_match.group('time_stamp')
                    transaction = transaction_match.group('transaction_string')
                except ValueError:
                    continue
                yield Transaction(timestamp=timestamp, response_time=response_time, transaction_string=transaction)
    except OSError as err:
        logger.critical(f'{err.strerror}: {err.filename}')
        sys.exit(err.errno)


def get_args():
    """Parse arguments passed at invocation

    Returns:
        argparse.Namespace: arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Analyze nginx logs',
        epilog='Example: %(prog)s --log-file ~/Documents/log/nginx.log --max-diff 1.75'
    )
    parser.add_argument('--log-file',
                        dest='log_file',
                        required=True,
                        help='Log file to analyze')
    parser.add_argument('--field',
                        dest='field',
                        required=False,
                        default='urt',
                        help='Field to measure from file (default: "urt")')
    parser.add_argument('--max-diff',
                        dest='max_diff',
                        required=False,
                        type=float,
                        default=5.00,
                        help='Max diff as decimal percentage of avg response to consider normal (default: 5.00)')
    parser.add_argument('-v', '--verbose',
                        required=False,
                        dest='verbosity',
                        action='count',
                        default=0,
                        help='Increase output verbosity')
    return parser.parse_args()


if __name__ == '__main__':
    main()
