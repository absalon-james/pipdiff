import argparse
import json


parser = argparse.ArgumentParser(description="Diff two pipsnapshot files.")

parser.add_argument('old_snapshot', type=str, help='First pipsnapshot to compare')
parser.add_argument('new_snapshot', type=str, help='Second pipsnapshot to compare')

parser.add_argument('--old-release', type=str, default=None,
                    help='Openstack ansible release of first pipsnaphot')
parser.add_argument('--new-release', type=str, default=None,
                    help='Openstack ansible release of second pipsnapshot')


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


def snapshot_from_wheel(wheel_data):
    snapshot = {}
    for release, data in wheel_data.iteritems():
        snapshot.setdefault(release, {})
        for wheel in data:
            parsed = parse_name(wheel)
            snapshot[release].setdefault(parsed['distribution'], parsed)
    return snapshot


def load_snapshot(filename):
    """Load snapshot from file.

    :param filename: Name of the file containing the snapshot. 
    :type filename: str
    :returns: Snapshot
    :rtype: dict
    """
    with open(filename, 'r') as f:
        wheel_data = json.loads(f.read())
        return snapshot_from_wheel(wheel_data)


def get_release(snapshot, release):
    """Get openstack ansible snapshot for release.

    :param snapshot: Snapshot keyed by releases
    :type snapshot: Dict
    :param release: Openstack ansible release version.
    :type release: str
    :returns: Snapshot for a release
    :rtype: dict
    """
    if not release:
        release = snapshot.keys()[0]
    return snapshot[release]



def missing_packages(a, b):
    """Finds the python package distributions in a but not b.

    :param a: Release snapshot
    :type a: dict
    :param b: Release snapshot
    :type b: dict
    :returns: List of packages in a but not b
    :rtype: list
    """
    a_packages = set(a.keys())
    b_packages = set(b.keys())
    missing = a_packages - b_packages
    missing = list(missing)
    return sorted(missing)


def differences(a, b):
    a_packages = set(a.keys())
    b_packages = set(b.keys())

    # Find packages in both
    inboth = a_packages & b_packages

    differences = []

    # Differences between packages in both
    for pkg_name in inboth:
        if a[pkg_name]['name'] != b[pkg_name]['name']:
            differences.append((pkg_name, a[pkg_name]['name'], b[pkg_name]['name']))

    return differences
    
        

if __name__ == '__main__':
    args = parser.parse_args()

    old = load_snapshot(args.old_snapshot)
    try:
        old = get_release(old, args.old_release)
    except KeyError:
        print "Invalid release for old snapshot."
        exit()

    new = load_snapshot(args.new_snapshot)
    try:
        new = get_release(new, args.new_release)
    except KeyError:
        print "Invalid release for new snapshot."
        exit()

    # Find packages in old but not new
    missing = missing_packages(old, new)
    if missing:
        print "\nThe following packages were in old but not in new..."
        for m in missing:
            print "\t{}".format(m)

    # Find packages in new but not in old
    missing = missing_packages(new, old)
    if missing:
        print "\nThe following packages were in new but not in old..."
        for m in missing:
            print "\t{}".format(m)


    # Find packages in both that might have changed
    diffs = differences(old, new)
    if diffs:
        print "\nThe following changes were detected..."
        for name, o, n in diffs:
            print "\t{}".format(name)
            print "\t\t{} -->".format(o)
            print "\t\t{}".format(n)
    
