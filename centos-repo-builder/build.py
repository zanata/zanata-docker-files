#!/usr/bin/env python
"""Rpm repo builder

@author:    Ding-Yi Chen

@copyright:  2018 Red Hat Asia Pacific. All rights reserved.

@license:    LGPLv2+

@contact:    dchen@redhat.com
"""
from __future__ import absolute_import, division, print_function

import argparse
import datetime
import glob
import locale
import logging
import re
import os
import shutil
import subprocess
import sys

REPO_DIR = "@REPO_DIR@"
DISTRO_DIR = "@REPO_DIR@/epel-@CENTOS_VERSION@"

locale.setlocale(locale.LC_ALL, 'C')


def run_check_call(cmd):
    """Display debug messages, run command, then check the exit code

    Args:
        cmd (List[str]): Command to be run

    Returns:
        int: exit status of cmd
    """
    logging.debug(" ".join(cmd))
    return subprocess.check_call(cmd)


def run_check_output(cmd):
    """Display debug messages, run command, then return the stdout as str

    Args:
        cmd ([type]):  Command to be run

    Returns:
        str: stdout from executing the cmd
    """
    logging.debug(" ".join(cmd))
    # EL6 does not have subprocess.check_output
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return proc.communicate()[0].rstrip()


def rsync(src, dest, options=None):
    """Rsync from src to dest

    Args:
        src (str): sync source in form of [[USER@]HOST:]DIR
        dest (str): sync destination in form of [[USER@]HOST:]DIR
        options (List[str], optional): Defaults to None.
                Additional rsync options.

    Returns:
        int: exit status of cmd
    """
    cmd_prefix = [
            '/usr/bin/rsync',
            '--cvs-exclude', '--recursive', '--verbose', '--links',
            '--update', '--compress', '--exclude', '*.core', '--stats',
            '--progress', '--archive', '--keep-dirlinks', '--delete']
    if options:
        cmd_prefix += options

    full_cmd = cmd_prefix + [src, dest]

    return run_check_call(full_cmd)


class RpmSpec(object):
    """Content of a RPM spec file

    Attributes:
        content: RPM spec file content as List of strings.
    """

    # We only interested in these tags
    TAGS = ['Name', 'Version', 'Release']

    def __init__(self, **kwargs):
        # type (Any) -> None
        """
        Constructor
        """
        for v in kwargs:
            setattr(self, v, kwargs.get(v))
        self.content = []

    def parse_spec_tag(self, line):
        # type (str) -> None
        """Parse the tag value from line if the line looks like
        spec tag definition, otherwise do nothing"""

        s = line.rstrip()

        matched = re.match(r"([A-Z][A-Za-z]*):\s*(.+)", s)
        if matched:
            if matched.group(1) in RpmSpec.TAGS:

                tag = matched.group(1)
                if not hasattr(self, tag):
                    # Only use the first match
                    setattr(self, tag, matched .group(2))
        return s

    @classmethod
    def init_from_file(cls, spec_file):
        # type (str) -> None
        """Init from existing spec file

        Args:
            spec_file (str): RPM spec file

        Raises:
            OSError e: File error

        Returns:
            RpmSpec: Instance read from spec_file
        """
        try:
            with open(spec_file, 'r') as in_file:
                self = cls()
                self.content = [
                        self.parse_spec_tag(l)
                        for l in in_file.readlines()]
        except OSError as e:
            raise e
        return self

    def update_version(self, version):
        # type (str) -> bool
        """Update to new version

        Args:
            version (str): new version to be set
        """
        if getattr(self, 'Version') == version:
            logging.warning("Spec file is already with version %s", version)
            return False

        setattr(self, 'Version', version)

        # Update content
        new_content = []
        for line in self.content:
            matched = re.match(r"^Version:(\s*)(.+)", line)
            if matched:
                new_content.append(
                        "Version:%s%s" % (matched.group(1), version))
                continue

            changelog_matched = re.match("^%changelog", line)
            if changelog_matched:
                now = datetime.datetime.now().strftime("%a %b %d %Y")
                changelog_item = (
                        "* {date} {email} {version}-1\n"
                        "- Upgrade to upstream version {version}\n".format(
                                date=now,
                                email=os.getenv(
                                        'MAINTAINER_EMAIL',
                                        'noreply@zanata.org'),
                                version=version))
                new_content.append(line)
                new_content.append(changelog_item)
                continue

            new_content.append(line)

        setattr(self, 'content', new_content)
        return True

    def write_to_file(self, spec_file):
        """Write the spec to file

        Args:
            spec_file (str): RPM spec file

        Raises:
            OSError e: File error
        """
        try:
            with open(spec_file, 'w') as out_file:
                out_file.write(str(self))

        except OSError as e:
            logging.error("Failed to write to %s", spec_file)
            raise e

    def __str__(self):
        return "\n".join(getattr(self, 'content'))


def main(argv=None):
    # type (dict) -> None
    """Run as command line program"""
    if not argv:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument(
            "-b", "--build-dep", action='store_true',
            help='Run yum build-dep to get dependencies')
    parser.add_argument(
            "-d", "--debug", action='store_true',
            help="Show debug")
    parser.add_argument(
            "-O", "--rsync-options", type=str,
            help="rsync options which will be used with '-S' and '-D'")
    parser.add_argument(
            "-S", "--rsync-source", type=str,
            help="Use rsync to get the repo from")
    parser.add_argument(
            "-D", "--rsync-dest", type=str,
            help="Use rsync to output the repo to")
    parser.add_argument(
            "-u", "--update-version", type=str,
            help="Update version in spec")
    parser.add_argument(
            "spec_file", type=str,
            help="Relative location of spec-file")
    args = parser.parse_args(argv)

    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Get the source dir
    if args.rsync_source:
        rsync(
                args.rsync_source, os.path.join(REPO_DIR, ""),
                None if not hasattr(args, "options") else args.options)

    os.chdir(REPO_DIR)

    # Update spec version
    if args.update_version:
        spec = RpmSpec.init_from_file(args.spec_file)
        spec.update_version(args.update_version)
        spec.write_to_file(args.spec_file)

    # Install dependencies
    if args.build_dep:
        subprocess.check_call([
                "sudo", "/usr/bin/yum-builddep", args.spec_file])

    # Build RPM
    run_check_call(["spectool", "-R", "-g", args.spec_file])
    run_check_call(["rpmbuild", "-ba", args.spec_file])

    arch = run_check_output([
            "rpm", "-q", "--qf", "%{arch}", "--specfile", args.spec_file])

    os.chdir(DISTRO_DIR)
    if arch == "noarch":
        os.chdir(os.path.join(DISTRO_DIR, "i386"))
        for rpm in glob.glob('*.noarch.rpm'):
            os.remove(rpm)

        os.chdir(os.path.join(DISTRO_DIR, "noarch"))
        for rpm in glob.glob("*.noarch.rpm"):
            os.rename(rpm, os.path.join(DISTRO_DIR, "x86_64", rpm))
            os.symlink(
                    os.path.join("..", "x86_64", rpm),
                    os.path.join(DISTRO_DIR, "i386", rpm))
        os.chdir(DISTRO_DIR)
        shutil.rmtree(os.path.join(DISTRO_DIR, "noarch"))

    # Create Repo
    for arch in ['SRPMS', 'x86_64', 'i386']:
        run_check_call([
                "createrepo", "--update", "--database", "--verbose",
                "--delta", arch])

    # Output dir
    if args.rsync_dest:
        rsync(
                os.path.join(REPO_DIR, ""), args.rsync_dest,
                None if not hasattr(args, "options") else args.options)


if __name__ == '__main__':
    main()
