#!/usr/bin/python

from ansible.module_utils.basic import *

import os

base_dir = '/var/www/repo/os-releases'


def parse_name(name):
    dash = '-'
    rest = name.replace('.whl', '')
    distribution, rest = rest.split(dash, 1)
    version, rest = rest.split(dash, 1)
    rest, platform_tag = rest.rsplit(dash, 1)
    rest, abi_tag = rest.rsplit(dash, 1)
    python_tag = rest.rsplit(dash, 1)
    if len(python_tag) > 1:
        rest, python_tag = python_tag

    if rest and rest != '-':
        build_tag = dash
    else:
        build_tag = ''

    return {
        'distribution': distribution,
        'version': version,
        'build_tag': build_tag,
        'python_tag': python_tag,
        'abi_tag': abi_tag,
        'platform_tag': platform_tag,
        'name': name
    }



def get_release_snapshot(release):
    path = os.path.join(base_dir, release)
    snapshot = []
    for f in os.listdir(path):
        if f.endswith('.whl') and os.path.isfile(os.path.join(path, f)):
            snapshot.append(f)
    return sorted(snapshot)
            

def main():
    module = AnsibleModule(argument_spec={})

    snapshot = {}

    for d in os.listdir(base_dir):
        full_path = os.path.join(base_dir, d)
        if os.path.isdir(full_path):
            snapshot.setdefault(d, get_release_snapshot(d))

    module.exit_json(changed=False, pipsnapshot=snapshot)

if __name__ == '__main__':
    main()
