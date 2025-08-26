import base64
import hashlib

from src.common.config import SupportedLocale


def get_app_def_filename(runtime_directory: str, app_id: str) -> str:
    app_dir = runtime_directory + "/apps/" + app_id
    return app_dir + "/" + app_id + ".xlsx"


def get_cache_file_path2(runtime_directory: str, app_id: str, locale: SupportedLocale, hashed) -> str:
    # return f"{runtime_directory}/apps/{app_id}/cache/cache_{app_id}_{locale}_{hashed}.json"
    return f"{runtime_directory}/apps/{app_id}/cache/cache_{app_id}_{locale}.json"


def short_hash(s: str) -> str:
    """
    :param s: the string to hash
    :return: SHA256 Hash base64-encoded then truncated to 6 characters
    """
    digest = hashlib.sha256(s.encode()).digest()
    b64 = base64.urlsafe_b64encode(digest).decode()
    return b64[:6]


def get_cache_file_path(runtime_directory: str, app_id: str, locale: SupportedLocale, system_prompt: str, text: str) -> str:
    hashed = short_hash(system_prompt + text)
    return get_cache_file_path2(runtime_directory, app_id, locale, hashed)
