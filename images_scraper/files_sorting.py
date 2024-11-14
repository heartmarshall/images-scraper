import os


def sort_files(sorting_dir: str, files_list: list, large_size=1048576, small_size=512000):
    """
    Раскладывает файлы по трём папкам: large, medium, small

    :param sorting_dir: директория в которой лежат файлы, которые нужно рассортировать
    :param files_list: название файлов, которые будут отсортированы
    """
    for dir_name in ("large", "medium", "small"):
        os.makedirs(dir_name, exist_ok=True)

    for file_name in files_list:
        file_size = os.stat(os.path.join(sorting_dir, file_name)).st_size
        if file_size >= large_size:
            category = "large"
        elif small_size <= file_size < large_size:
            category = "medium"
        else:
            category = "small"
        os.replace(os.path.join(sorting_dir, file_name),
                   os.path.join(sorting_dir, category, file_name))
    return 
