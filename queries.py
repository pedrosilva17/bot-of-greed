import json
import re
import sqlite3
from typing import Tuple

import constants


def connection_open() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Open connection to database.

    Returns:
        Tuple[sqlite3.Connection, sqlite3.Cursor]: The database connection and a cursor pointing to the top of the
        database's records.
    """
    connection = sqlite3.connect("card-database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    connection.create_function("REGEXP", 2, regexp)
    return connection, cursor


def connection_close(connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    """Close connection to database.

    Args:
        connection (sqlite3.Connection): The database connection.
        cursor (sqlite3.Cursor): The database cursor.
    """
    cursor.close()
    connection.close()


def regexp(pattern: str, item: str) -> (re.Match[str] | None):
    """Function to be used by sqlite to query the database given a regular expression.

    Args:
        pattern (str): The pattern used to match the string.
        item (str): The string to be matched.

    Returns:
        (re.Match[str] | None): The match on the given string, or None if no match is found.
    """
    if item is None:
        return False
    return re.search(pattern, item, re.IGNORECASE) is not None


def is_comparable(parameter: str) -> bool:
    """Check if the parameter is comparable to an integer.

    Args:
        parameter (str): The search parameter.

    Returns:
        bool: True if parameter is comparable, else False.
    """
    return parameter in ["atk", "def", "level", "rank", "linkval", "scale"]


def error_message(parameters: dict, query_text: str) -> str:
    """Generate error message when no card is found or a parameter value is invalid.

    Args:
        parameters (dict): The dictionary of parameters
        query_text (str): The query that would be executed.

    Returns:
        str: The error message.
    """
    error_text = "No card found using the following parameters:\n\n"
    for parameter in parameters.keys():
        if parameters[parameter] is not None and parameter not in ["sort", "order"]:
            if is_comparable(parameter):
                # Extract operator used in query
                try:
                    operator = re.search(f"({parameter}) (>|<|>=|<=|=)\s", query_text).group(2)
                except AttributeError:
                    error_text = "Parameter type error! Make sure you use valid inputs in your parameters."
                    return error_text
                error_text += f"{constants.long_terms[parameter]}: {operator} {parameters[parameter]}\n"
            else:
                error_text += f"{constants.long_terms[parameter]}: {parameters[parameter]}\n"
    return error_text


def parse_comparable(parameter_name: str, parameter_value: str) -> str:
    """Parse a parameter that is comparable, in order to extract any operator used (greater than, etc.) and check it's
    validity.

    Args:
        parameter_name (str): The name of the parameter.
        parameter_value (str): The value of the parameter.

    Returns:
        str: The result of the pattern matching in the parameter value.
    """
    result = "error"
    for (pattern, operator) in constants.regex_comparable_patterns.items():
        if re.search(pattern, parameter_value):
            result = f"{parameter_name} {operator} ? AND "
    return result


def random_card() -> sqlite3.Row:
    """Gets a random card using the local card database.

    Returns:
        sqlite3.Row: A sqlite3 row object with the card information retrieved from the query.
    """
    connection, cursor = connection_open()
    cursor.execute("SELECT * FROM Cards ORDER BY RANDOM() LIMIT 1")
    data = cursor.fetchone()
    connection_close(connection, cursor)
    return data


def card_attribute_list(attribute: str) -> list:
    """Gets all the options for the specified card attribute in the database.

    Args:
        attribute (str): The name of the attribute whose options will be retrieved.

    Returns:
        list: A list with the attribute values retrieved from the query.
    """
    connection, cursor = connection_open()
    query_text = f"SELECT {attribute} FROM Cards"

    # Avoid the (insert character name here) subtypes from Speed Duel Skill Cards
    if attribute == "subtype": query_text += " WHERE type != 'Skill Card'"

    cursor.execute(query_text)
    data = cursor.fetchall()
    connection_close(connection, cursor)
    attribute_set = []
    (attribute_set.append(data[i][attribute]) for i in range(len(data) - 1) if
     data[i][attribute] not in attribute_set and data[i][attribute] is not None)
    attribute_set.sort()
    return attribute_set


def query_parameter(parameters: dict, parameter: str, key_list: list, parameter_list: list, query_text: str) -> Tuple[
    list, list, str]:
    """Progressively build the query string according to the parameters set by the user.
    Needs severe refactoring...

    Args:
        parameters (dict): The dictionary of parameters.
        parameter (str): The parameter to add to the query.
        key_list (list): The current list of parameter names in the query.
        parameter_list (list): The current list of parameter values in the query.
        query_text (str): The current query text.

    Returns:
        Tuple[list, list, str]: The updated query text and parameter name/value lists.
    """
    match parameter:
        case "name":
            key_list = [parameter]
            parameter_list = [parameters[parameter]]
            query_text = f"SELECT * FROM Cards WHERE Name LIKE ? AND "
        case "name_multi":
            key_list.append("name")
            parameter_list.append('%' + parameters[parameter] + '%')
            query_text += "Name LIKE ? AND "
        case "linkmarkers":
            sorted_markers = [param.lower().replace(" ", "") for param in parameters[parameter].split(",")]
            try:
                sorted_markers.sort(key=[marker.lower() for marker in constants.link_markers].index)
            except ValueError:
                return -1
            parameter_regex = ",.*".join(sorted_markers)

            # Match cards with at least the listed markers, but without partially matching hyphenated markers.
            # For example, "Left, Top" doesn't match "Bottom-Left, Top".
            pattern = f"(^|.*[^-]+){parameter_regex}($|[^-]+.*)"

            key_list.append(parameter)
            parameter_list.append(pattern)
            query_text += f"{parameter} REGEXP ? AND "
        case _:
            if is_comparable(parameter):
                key_list.append(parameter)
                parameter_copy = parameters[parameter]
                parameters[parameter] = re.sub('[^0-9]', '', parameters[parameter])
                parameter_list.append(parameters[parameter])
                cmp = parse_comparable(parameter, parameter_copy)
                if cmp == "error":
                    parameters[parameter] = parameter_copy
                    return -1
                query_text += cmp
            else:
                key_list.append(parameter)
                parameter_list.append(parameters[parameter])
                query_text += f"{parameter} LIKE ? AND "
    return key_list, parameter_list, query_text


def query(parameters: dict) -> (list | str):
    """Builds the query string according to the user's chosen parameters and uses it to query the database.

    Args:
        parameters (dict): The dictionary of parameters.

    Returns:
        (list | str): The list of sqlite3 row objects obtained from the database, or an error message.
    """
    key_list = []
    parameter_list = []
    connection, cursor = connection_open()

    query_text = "SELECT * FROM Cards WHERE "
    print(parameters)
    for parameter in parameters:
        if parameters[parameter] is not None and parameter not in ["sort", "order"]:
            try:
                key_list, parameter_list, query_text = query_parameter(parameters, parameter, key_list, parameter_list,
                                                                       query_text)
            except TypeError:
                return error_message(parameters, query_text)
            if parameter == "name":
                break

    if len(parameter_list) > 0:  # If parameters were specified, remove trailing "AND" from query, else remove "WHERE"
        query_text = query_text[:-4]
    else:
        query_text = query_text[:-6]

    if key_list != ["name"]:
        query_text += "ORDER BY " + constants.short_terms[parameters['sort']]
        if parameters["order"] == "Descending":
            query_text += " DESC"

    print(query_text)
    print(parameter_list)
    cursor.execute(query_text, parameter_list)
    print(parameter_list)
    data = cursor.fetchall()
    if len(data) == 0:
        return error_message(parameters, query_text)
    elif len(data) == 1:
        data[0] = dict(data[0])
        new_data = [{}]
        for key in data[0]:
            if data[0][key] is not None:
                new_data[0][key] = data[0][key]
        new_data[0]["card_images"] = json.loads(new_data[0]["card_images"])
        new_data[0]["card_prices"] = json.loads(new_data[0]["card_prices"])
        new_data[0]["misc_info"] = json.loads(new_data[0]["misc_info"])
        try:
            new_data[0]["banlist_info"] = json.loads(new_data[0]["banlist_info"])
        except KeyError:
            pass
        data = new_data

    connection_close(connection, cursor)
    print(data[0]["name"])
    return data
