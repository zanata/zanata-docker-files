#!/usr/bin/env python

from typing import List, Any
# We need to import List and Any for mypy to work
import argparse
import fileinput
import json
import logging
import re
import subprocess
import sys
import urllib2

class GitHelper:
    "Helper functions for git"
    GIT_CMD = '/bin/git'

    @staticmethod
    def remote_get_latest_tag(repo_url, tag_glob='*'):
        # type: (str, str) -> str
        """Get latest (newest) tag from git remote
        Known Bug: If the tag 4.4.4 is newer than 4.5.0,
        then the 'latest' tag will be 4.4.4"""

        tag = subprocess.check_output([
            GIT_CMD, 'ls-remote', '--tags', repo_url,
            'refs/tags/' + tag_glob + '[^^{}]'
            ]).split()[-1].split('/')[-1]
        logging.info("latest tag of %s is %s", repo_url, tag)
        return tag

    @staticmethod
    def branch_get_current():
        # type: () -> str
        """Return either current branch, or 'HEAD' if in detached mode
        This method assume you are already in correct directory"""
        return subprocess.check_output([GIT_CMD, 'rev-parse', '--abbrev-ref', 'HEAD'])

    @staticmethod
    def branch_merge_detached(target_branch):
        # type: (str) -> None
        """Merge to target_branch if in git detached mode, or no-op
        This method assume you are already in correct directory"""
        commit_sha = subprocess.check_output([GIT_CMD, 'rev-parse', 'HEAD'])
        tmp_branch = 'br-' + commit_sha
        if GitHelper.branch_get_current() == 'HEAD':
            subprocess.check_call([GIT_CMD, 'branch', tmp_branch, commit_sha])
            subprocess.check_call([GIT_CMD, 'checkout', target_branch])
            subprocess.check_call([GIT_CMD, 'merge', tmp_branch])
            subprocess.check_call([GIT_CMD, 'branch', '-D', tmp_branch])

    @staticmethod
    def push(target_branch):
        # type: (str) -> None
        "Git push to master if there is unpushed commits"
        if subprocess.call([GIT_CMD, "diff", "--exit-code", "origin", "HEAD"]) != 0:
            # git_detached_merge_branch is needed in Jenkins as it checkout as detached
            GitHelper.branch_merge_detached(target_branch)
            subprocess.check_call([GIT_CMD, 'push', '--follow-tags', 'origin', 'master'])

    def __init__(self, repo_url, tag_prefix=''):
        # type: (str, str) -> None
        self.repo_url = repo_url
        self.latest_tag = GitHelper.remote_get_latest_tag(self.repo_url, tag_prefix+'*')
        self.latest_version = self.latest_tag[len(tag_prefix):]

    def __getitem__(self, key):
        # type: (str) -> str
        return self[key]

class DockerTag:
    "Docker image tag, it may contains version-postrelease, version, or simply 'latest'"

    @staticmethod
    def list_tags(repo_name, docker_name):
        # type: (str, str) -> List[str]
        """Return the name of tags as list"""
        tag_url = 'https://registry.hub.docker.com/v2/repositories/%s/%s/tags/' % (repo_name, docker_name)
        result = [] # type: List[str]
        while tag_url:
            logging.info("Getting tags from %s", tag_url)
            request = urllib2.Request(tag_url)
            response = urllib2.urlopen(request)
            logging.debug(response.info())

            tags_json = json.load(response)
            result += [elem["name"] for elem in tags_json["results"]]
            tag_url = tags_json.get("next", "")
        return result

    @staticmethod
    def has_tag(repo_name, docker_name, tag):
        # type: (str, str, str) -> int
        """Whether the docker image has the given tag"""
        tags_list = DockerTag.list_tags(repo_name, docker_name)
        return tag in tags_list

    @staticmethod
    def next_postrelease(repo_name, docker_name, version):
        # type: (str, str, str) -> int
        "Next unused postrelease"
        prog = re.compile("^%s-([0-9]+)" % version)
        current_release = 0
        for tag in DockerTag.list_tags(repo_name, docker_name):
            matched = re.match(prog, tag)
            if not matched:
                continue
            if int(matched.group(1)) > current_release:
                current_release = int(matched.group(1))
        return current_release + 1

    def __init__(self, tag):
        # type: (str) -> None
        """Update the Dockerfile according to tag, it accepts either x.y.z-r or 'auto' as tag
        Properties:
            orig_name: The parameter passed
            version: e.g. 4.4.3
            extra: whatever after [version]-. Could be something like alpha-1 or 2
            prerelesae: e.g. alpha-1
            postrelease: e.g. 2
            name: Final resolved name, like 4.4.3-2"""
        self.orig_name = tag
        if self.orig_name == 'latest':
            self.name = 'latest'
            return
        elif self.orig_name == 'auto':
            if args.docker_name in DOCKER_NAME_DB:
                git_helper = GitHelper(DOCKER_NAME_DB[args.docker_name]['url'],
                        DOCKER_NAME_DB[args.docker_name]['tag_prefix'])

                self.version = git_helper.latest_version
                self.postrelease = DockerTag.next_postrelease(
                        args.repo_name, args.docker_name, self.version)
            else:
                logger.error("next_version_release does not support docker_name %s",
                        args.docker_name)
                sys.exit(EXIT_FATAL_INVALID_ARGUMENTS)
            self.name = "%s-%d" % (self.version, self.postrelease)
        else:
            match = re.search('^([^-]*)-(.*)', tag)
            if match:
                self.version = match.group(1)
                self.extra = match.group(2)
                if re.match('^[0-9]+', self.extra):
                    self.postrelease = int(self.extra)
                    self.name = "%s-%d" % (self.version, self.postrelease)
                else:
                    ## alpha or rc
                    self.prerelease = self.extra
                    self.name = self.orig_name
            elif re.match('^[0-9.]+', tag):
                self.version = tag
                self.name = self.orig_name

    def __getitem__(self, key):
        # type: (str) -> str
        return self[key]

## Cmd full path
GIT_CMD = '/bin/git'
CURL_CMD = '/bin/curl'
DOCKER_CMD = '/bin/docker'

## Exit Status
EXIT_OK = 0
EXIT_FATAL_INVALID_OPTIONS = 3
EXIT_FATAL_INVALID_ARGUMENTS = 7
EXIT_RETURN_FALSE = 40

## Set logging
logging.basicConfig(format='%(asctime)-15s [%(levelname)s] %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

DOCKER_NAME_DB = {
    'server': {
        'dir': 'zanata-server',
        'url': 'https://github.com/zanata/zanata-platform',
        'tag_prefix': 'platform-',
    }
}

def _docker_name_to_dir(docker_name):
    # type: (str) -> str
    """Convert docker_name to the directory that contains Dockerfile"""
    if docker_name in DOCKER_NAME_DB:
        return DOCKER_NAME_DB[docker_name]['dir']
    return docker_name

def get_tags():
    # type: () -> None
    """Return the name of tags as list"""
    logging.info("get-tags for %s/%s", args.repo_name, args.docker_name)

    tags_list = DockerTag.list_tags(args.repo_name, args.docker_name)
    print('\n'.join(str(tag) for tag in tags_list))

def has_tag():
    # type: () -> None
    """Whether the docker image has the given tag"""

    if DockerTag.has_tag(args.repo_name, args.docker_name, args.tag):
        print("yes")
        sys.exit(EXIT_OK)
    else:
        print("no")
        sys.exit(EXIT_RETURN_FALSE)


def _dockerfile_update(docker_name, docker_tag):
    # type: (str, DockerTag) -> None

    release = 1 if not hasattr(docker_tag, 'postrelease') else int(docker_tag.postrelease)
    dockerfile_name = _docker_name_to_dir(docker_name) + '/Dockerfile'

    dockerfile_file = fileinput.FileInput([dockerfile_name], inplace=True, backup='.bak')
    for line in iter(dockerfile_file):
        if re.match(r'^ARG ZANATA_VERSION=.*$', line):
            sys.stdout.write(re.sub(r'^ARG ZANATA_VERSION=.*$',
                    'ARG ZANATA_VERSION=' + docker_tag.version, line))
        elif re.match(r'\s*Release="([0-9]+)"', line):
            sys.stdout.write((re.sub(r'Release=".*"',
                    ('Release="%s"' % (release)), line)))
        else:
            sys.stdout.write(line)

    sys.stdout.flush()
    dockerfile_file.close()

def dockerfile_update():
    # type: () -> None
    "Update the Dockerfile according to given tag"
    docker_tag = DockerTag(args.tag)
    _dockerfile_update(args.docker_name, docker_tag)

def publish():
    # type: () -> None
    """Publish docker image to docker hub, as well as git commit"""
    if DockerTag.has_tag(args.repo_name, args.docker_name, args.tag):
        logger.error("Tag %s already exists", args.tag)
        sys.exit(EXIT_FATAL_INVALID_ARGUMENTS)
    else:
        logging.info("docker tag to be publish: %s", args.tag)

    ## Update Docker file
    docker_tag = DockerTag(args.tag)
    _dockerfile_update(args.docker_name, docker_tag)
    docker_image_name = "%s/%s:%s" % (args.repo_name, args.docker_name, docker_tag.name)
    if subprocess.call([GitHelper.GIT_CMD, 'diff', '--exit-code']) != 0:
        subprocess.check_call([
                GitHelper.GIT_CMD, 'commit', '-a', '-m',
                "[release] Image %s is released" % docker_image_name])

    ## Building docker image
    logging.info("Building image %s", docker_image_name)
    subprocess.check_call([
            DOCKER_CMD, 'build', '-t', docker_image_name, _docker_name_to_dir(args.docker_name)])

    ## Tag docker image
    for current_tag in [docker_tag.name, 'latest']:
        subprocess.check_call([
                DOCKER_CMD, 'tag', docker_image_name,
                "%s/%s/%s:%s" % (args.registry, args.repo_name, args.docker_name, current_tag)])

    ## Pushing docker image
    for current_tag in [docker_tag.name, 'latest']:
        subprocess.check_call([
                DOCKER_CMD, 'push',
                "%s/%s/%s:%s" % (args.registry, args.repo_name, args.docker_name, current_tag)])

    ## Git push to master if there is unpushed commits
    GitHelper.push('master')

if __name__ == '__main__':
    ## Parse options and arguments
    parser = argparse.ArgumentParser(description='Docker helper functions')
    parser.add_argument(
            '-r', '--repo-name', type=str,
            default='zanata',
            help='Docker Repository name. Default: zanata')
    parser.add_argument(
            '-R', '--registry', type=str,
            default='docker.io',
            help='Docker Registry name. Default: docker.io')

    subparsers = parser.add_subparsers(title='Command',
            description='Valid commands', help='Command help')
    has_tag_parser = subparsers.add_parser('has-tag',
            help='Whether the docker image has the given tag')
    has_tag_parser.add_argument('docker_name', type=str,
            help='Docker name, e.g. "server"')
    has_tag_parser.add_argument('tag', type=str, help='tag')
    has_tag_parser.set_defaults(func=has_tag)

    get_tags_parser = subparsers.add_parser('get-tags',
            help='Get all existing tags')
    get_tags_parser.add_argument('docker_name', type=str,
            help='Docker name, e.g. "server"')
    get_tags_parser.set_defaults(func=get_tags)

    dockerfile_update_parser = subparsers.add_parser('dockerfile-update',
            help='Update the Dockerfile according to tag')
    dockerfile_update_parser.add_argument('docker_name', type=str,
            help='Docker name, e.g. "server"')
    dockerfile_update_parser.add_argument('tag', type=str,
            help='tag to be publish')
    dockerfile_update_parser.set_defaults(func=dockerfile_update)

    publish_parser = subparsers.add_parser('publish',
            help='publish docker image according to the tag')
    publish_parser.add_argument('docker_name', type=str,
            help='Docker name, e.g. "server"')
    publish_parser.add_argument('tag', type=str,
            help='tag to be publish')
    publish_parser.set_defaults(func=publish)

    args = parser.parse_args()
    args.func()
