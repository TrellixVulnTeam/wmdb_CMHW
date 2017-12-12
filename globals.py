import os
import sqlite3

from datetime import datetime

global db_connection

db_connection = sqlite3.connect(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ym.db'
    )
)


POSTER_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'static',
    'posters'
)


def unix_time(dt):
    """
    Covert datetime object to seconds to/from epoch
    :param dt: datetime object to convert
    :return: seconds from epoch (unix time), may be positive or negative
    """
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds()
