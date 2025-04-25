from typing import TypeVar

T = TypeVar("T")


def remove_dict_with_duplicate_field(
    dict_list: list[dict[str, T]], duplicate_field: str
) -> list[dict[str, T]]:
    """Remove dict with duplicate value for a specified field
    :param dict_list: list of dictionnaries
    :param duplicate_field: name of the field to check for duplicate
    """
    res: list[dict[str, T]] = []
    for d in dict_list:
        if d[duplicate_field] not in [item[duplicate_field] for item in res]:
            res.append(d)
    return res
