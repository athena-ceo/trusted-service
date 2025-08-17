from src.common.configuration import SupportedLocale


def get_cache_file_path(runtime_directory: str, app_id: str, locale: SupportedLocale) -> str:
    return f"{runtime_directory}/apps/{app_id}/cache_{app_id}_{locale}.json"
