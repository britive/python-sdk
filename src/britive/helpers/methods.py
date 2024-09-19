from typing import Union


def safe_list_get(lst, idx, default) -> Union[str, None]:
    try:
        return lst[idx]
    except IndexError:
        return default