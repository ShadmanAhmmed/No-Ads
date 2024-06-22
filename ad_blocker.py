import re
import requests
import os
import time
import progressbar
from typing import List

# URL of the maintained list of ad servers (example)
AD_SERVER_LIST_URL = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"

# Read ad server domains from the provided URL
def get_ad_servers(url: str) -> List[str]:
    response = requests.get(url)
    lines = response.text.splitlines()
    ad_servers = [line for line in lines if line.startswith("0.0.0.0") or line.startswith("127.0.0.1")]
    ad_servers = [re.sub(r'^(0.0.0.0|127.0.0.1)\s+', '', line) for line in ad_servers]
    return ad_servers

# Check if the hosts file is already modified
def is_hosts_modified(ad_servers: List[str]) -> bool:
    with open("/etc/hosts", 'r') as file:
        contents = file.read()
        return all(server in contents for server in ad_servers)

# Location of the hosts file
HOSTS_FILE = "/etc/hosts"
BACKUP_FILE = "/etc/hosts.bak"

# Add ad server entries to the hosts file
def modify_hosts_file(ad_servers: List[str], add: bool):
    # Backup the current hosts file
    if add:
        with open(HOSTS_FILE, 'r') as file:
            backup_contents = file.read()
        with open(BACKUP_FILE, 'w') as file:
            file.write(backup_contents)

    lines = []
    if add:
        with open(HOSTS_FILE, 'r') as file:
            lines = file.readlines()

    progress = progressbar.ProgressBar(max_value=len(ad_servers))

    with open(HOSTS_FILE, 'a' if add else 'w') as file:
        if not add:
            with open(BACKUP_FILE, 'r') as backup_file:
                lines = backup_file.readlines()
            file.writelines(lines)

        for i, server in enumerate(ad_servers):
            if add:
                file.write(f"127.0.0.1 {server}\n")
            else:
                lines = [line for line in lines if server not in line]
            progress.update(i + 1)
            time.sleep(0.01)  # Simulate some delay for the progress bar

        if not add:
            file.writelines(lines)

    progress.finish()

# Main function
def main():
    print("Loading ad server list...")
    ad_servers = get_ad_servers(AD_SERVER_LIST_URL)

    modified = is_hosts_modified(ad_servers)
    status = "green" if modified else "red"
    print(f"Hosts file status: {status}")

    if modified:
        print("1. Remove ad servers from hosts file")
    else:
        print("1. Add ad servers to hosts file")
    print("2. Do nothing")

    choice = input("Enter your choice (1/2): ").strip()
    if choice == "1":
        if modified:
            print("Removing ad servers from hosts file...")
            modify_hosts_file(ad_servers, add=False)
        else:
            print("Adding ad servers to hosts file...")
            modify_hosts_file(ad_servers, add=True)
    else:
        print("No changes made.")

if __name__ == "__main__":
    main()
