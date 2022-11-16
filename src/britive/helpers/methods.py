def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default