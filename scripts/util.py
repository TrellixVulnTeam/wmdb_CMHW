import re

rgx_white_space = re.compile('[\s]+')
rgx_not_words = re.compile('[\W]+')


def user_info(given_name):
    """
    Get the user info (u_name and fake email) from a given name. Parses u_name as first_last and email as
    first_last@ymdb.com
    :param given_name: given name for this user
    :return: (u_name, email) from the given name
    """
    stripped = rgx_white_space.sub('_', given_name)
    stripped = rgx_not_words.sub('', stripped)
    email = stripped + '@ymdb.com'
    return stripped, email
