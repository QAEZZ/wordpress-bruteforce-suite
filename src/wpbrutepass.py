#! /usr/bin/env python3

import argparse
import requests
from pathlib import Path
import os
import sys
from typing import Union


def get_args() -> tuple[str, str, int]:
    parser = argparse.ArgumentParser(
        description="Brute force the password field of a WordPress site."
        "\nTested on WP 4.3.33."
    )
    parser.add_argument(
        "-u",
        "--url",
        dest="URL",
        help="The url of the site, prefix with http(s)://",
        required=True,
    )
    parser.add_argument(
        "-w",
        "--wordlist",
        dest="WORDLIST",
        help="The path to the wordlist you want to use.",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        dest="TIMEOUT",
        help="Timeout of each request, default: 5.",
        required=False,
        default=5,
        type=int,
    )

    args = parser.parse_args()
    url: str = args.URL
    wordlist: str = args.WORDLIST
    timeout: int = args.TIMEOUt

    return (url, wordlist, timeout)


def check_if_site_up(site: str, timeout: int) -> tuple[bool, str]:
    try:
        resp = requests.get(site, timeout=float(timeout))
        if resp.ok:
            return (True, "Site is up.")
        return (False, f"Error: {resp.status_code}")
    except requests.exceptions.Timeout:
        return (False, "Connection timed out.")
    except requests.exceptions.ConnectionError:
        return (False, "Failed to connect to the site.")
    except requests.exceptions.RequestException as ex:
        return (False, f"Something went wrong!\n{str(ex)}")
    except ValueError:
        return (False, f"Timeout must be an int/float, not {type(timeout).__name__}.")
    except Exception as ex:
        return (False, f"Something else went wrong!\n{str(ex)}")


def check_if_file_exists(file_path: str) -> bool:
    file = Path(file_path)
    if file.is_file():
        return True
    return False


def brute_force(
    wp_login_url: str,
    wp_admin_url: str,
    worlist: Union[str, Path],
    s: requests.Session,
    cookies: dict,
) -> tuple[bool, str]:
    return (False, "Coming soon.")


def main() -> None:
    url, wordlist, timeout = get_args()
    print(f"Site....: {url}\nWordlist: {wordlist}\nTimeout.: {timeout}\n")

    print("Not yet implemented.")
    return

    wp_login_url = f"{url}/wp-login.php"
    wp_admin_url = f"{url}/wp-admin"
    wordlist = os.path.abspath(wordlist)

    is_site_up = check_if_site_up(wp_login_url, timeout)

    if not is_site_up[0]:
        print(is_site_up[1])
        return
    elif not check_if_file_exists(wordlist):
        print("The wordlist path does not exist.")
        return

    s = requests.Session()
    cookies = dict(s.get(wp_login_url).cookies)

    result = brute_force(wp_login_url, wp_admin_url, wordlist, s, cookies)

    print(
        f"Password -> {result[1]}"
        if result[0]
        else "None of the passwords worked, sorry."
    )


if __name__ == "__main__":
    main()
