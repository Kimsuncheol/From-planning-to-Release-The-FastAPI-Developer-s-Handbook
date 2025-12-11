def deduplicate_and_sort(items: list[T]) -> list[T]:
    return list(dict.fromkeys(items))