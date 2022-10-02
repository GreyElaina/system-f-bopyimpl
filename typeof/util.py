def unique_string(excludes: set[str]):
    counter = 0
    while f"X{counter}" in excludes:
        counter += 1
    return f"X{counter}"
