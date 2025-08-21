from src.common.config import SupportedLocale

def get_app_def_filename(runtime_directory: str, app_id: str) -> str:
    app_dir = runtime_directory + "/apps/" + app_id
    return app_dir + "/" + app_id + ".xlsx"


def get_cache_file_path(runtime_directory: str, app_id: str, locale: SupportedLocale) -> str:
    return f"{runtime_directory}/apps/{app_id}/cache/cache_{app_id}_{locale}.json"
