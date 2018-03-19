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
            GitHelper.GIT_CMD, 'ls-remote', '--tags', repo_url,
            'refs/tags/' + tag_glob + '[^^{}]'
            ]).split()[-1].split('/')[-1]
        logging.info("latest tag of %s is %s", repo_url, tag)
        return tag

    @staticmethod
    def branch_get_current():
        # type: () -> str
        """Return either current branch, or 'HEAD' if in detached mode
        This method assume you are already in correct directory"""
        return subprocess.check_output(
                [GitHelper.GIT_CMD, 'rev-parse', '--abbrev-ref', 'HEAD'])

    @staticmethod
    def branch_merge_detached(target_branch):
        # type: (str) -> None
        """Merge to target_branch if in git detached mode, or no-op
        This method assume you are already in correct directory"""
        commit_sha = subprocess.check_output(
                [GitHelper.GIT_CMD, 'rev-parse', 'HEAD'])
        tmp_branch = 'br-' + commit_sha
        if GitHelper.branch_get_current() == 'HEAD':
            subprocess.check_call(
                    [GitHelper.GIT_CMD, 'branch', tmp_branch, commit_sha])
            subprocess.check_call(
                    [GitHelper.GIT_CMD, 'checkout', target_branch])
            subprocess.check_call(
                    [GitHelper.GIT_CMD, 'merge', tmp_branch])
            subprocess.check_call(
                    [GitHelper.GIT_CMD, 'branch', '-D', tmp_branch])

    @staticmethod
    def push(target_branch):
        # type: (str) -> None
        "Git push to master if there is unpushed commits"
        if subprocess.call(
                [GitHelper.GIT_CMD, 'diff', '--exit-code', 'origin', 'HEAD']
                ) != 0:
            # branch_merge_detached is needed in Jenkins
            # as it checkout as detached
            GitHelper.branch_merge_detached(target_branch)
            subprocess.check_call(
                    [
                            GitHelper.GIT_CMD, 'push', '--follow-tags',
                            'origin', 'master'])

    def __init__(self, repo_url, tag_prefix=''):
        # type: (str, str) -> None
        self.repo_url = repo_url
        self.latest_tag = GitHelper.remote_get_latest_tag(
                self.repo_url, tag_prefix+'*')
        self.latest_version = self.latest_tag[len(tag_prefix):]

    def __getitem__(self, key):
        # type: (str) -> str
        return self[key]


class DockerImage:
    """This class contains information about Docker image tag and dockerfile
    tag: version-postrelease, version, or simply 'latest'
    dockerfile: path"""

    # Cmd full path
    DOCKER_CMD = '/bin/docker'

    DOCKER_NAME_DB = {
        'server': {
            'dir': 'zanata-server',
            'url': 'https://github.com/zanata/zanata-platform',
            'tag_prefix': 'platform-',
        }
    }

    @staticmethod
    def list_tags(repo_name, docker_name):
        # type: (str, str) -> List[str]
        """Return the name of tags as list"""
        tag_url = 'https://%s/%s/%s/tags/' % (
                'registry.hub.docker.com/v2/repositories',
                repo_name, docker_name)
        result = []  # type: List[str]
        while tag_url:
            logging.info("Getting tags from %s", tag_url)
            # Audited urlopen URL
            response = urllib2.urlopen(tag_url)  # nosec
            logging.debug(response.info())

            tags_json = json.load(response)
            result += [elem["name"] for elem in tags_json["results"]]
            tag_url = tags_json.get("next", "")
        return result

    @staticmethod
    def has_tag(repo_name, docker_name, tag):
        # type: (str, str, str) -> int
        """Whether the docker image has the given tag"""
        tags_list = DockerImage.list_tags(repo_name, docker_name)
        return tag in tags_list

    @staticmethod
    def next_postrelease(repo_name, docker_name, version):
        # type: (str, str, str) -> int
        "Next unused postrelease"
        prog = re.compile("^%s-([0-9]+)" % version)
        current_release = 0
        for tag in DockerImage.list_tags(repo_name, docker_name):
            matched = re.match(prog, tag)
            if not matched:
                continue
            if int(matched.group(1)) > current_release:
                current_release = int(matched.group(1))
        return current_release + 1

    def __init__(self, repo_name, docker_name, tag_param):
        # type: (str, str, str) -> None
        """Properties:
            tag_param: The tag parameter, it accepts either  x.y.z-r or 'auto'
            version: e.g. 4.4.3
            extra: whatever after [version]-.
                Could be either the pre-release like alpha-1
                or post-release like 2
            prerelesae: e.g. alpha-1
            postrelease: e.g. 2
            final_tag: Final resolved tag, like 4.4.3-2"""

        self.repo_name = repo_name
        # Dockerfile
        self.docker_name = docker_name
        if docker_name in DockerImage.DOCKER_NAME_DB:
            dockerfile_dir = DockerImage.DOCKER_NAME_DB[docker_name]['dir']
        else:
            dockerfile_dir = docker_name

        self.dockerfile_name = "%s/Dockerfile" % dockerfile_dir

        # Docker Tag
        self.tag_param = tag_param
        if self.tag_param == 'latest':
            self.final_tag = 'latest'
            return
        elif self.tag_param == 'auto':
            if args.docker_name in DockerImage.DOCKER_NAME_DB:
                git_helper = GitHelper(
                        DockerImage.DOCKER_NAME_DB[docker_name]['url'],
                        DockerImage.DOCKER_NAME_DB[docker_name]['tag_prefix'])

                self.version = git_helper.latest_version
                self.postrelease = DockerImage.next_postrelease(
                        repo_name, docker_name, self.version)
            else:
                logger.error("Unsupported docker_name %s", docker_name)
                sys.exit(EXIT_FATAL_INVALID_ARGUMENTS)
            self.final_tag = "%s-%d" % (self.version, self.postrelease)
        else:
            match = re.search('^([^-]*)-(.*)', self.tag_param)
            if match:
                self.version = match.group(1)
                self.extra = match.group(2)
                if re.match('^[0-9]+', self.extra):
                    self.postrelease = int(self.extra)
                    self.final_tag = "%s-%d" % (self.version, self.postrelease)
                else:
                    # alpha or rc
                    self.prerelease = self.extra
                    self.final_tag = self.tag_param
            elif re.match('^[0-9.]+', self.tag_param):
                self.version = self.tag_param
                self.final_tag = self.tag_param
        self.image_name = "%s/%s:%s" % (
                self.repo_name, self.docker_name, self.final_tag)

    def __getitem__(self, key):
        # type: (str) -> str
        return self[key]

    def dockerfile_update(self):
        # type: () -> None

        release = 1 if not hasattr(self, 'postrelease') else int(self.postrelease)

        dockerfile_file = fileinput.FileInput(
                [self.dockerfile_name], inplace=True, backup='.bak')
        for line in iter(dockerfile_file):
            if re.match(r'^ARG ZANATA_VERSION=.*$', line):
                sys.stdout.write(
                        re.sub(r'^ARG ZANATA_VERSION=.*$',
                               'ARG ZANATA_VERSION=%s' % self.version, line))
            elif re.match(r'\s*Release="([0-9]+)"', line):
                sys.stdout.write(
                        re.sub(r'Release=".*"',
                               'Release="%d"' % release, line))
            else:
                sys.stdout.write(line)

        sys.stdout.flush()
        dockerfile_file.close()


# Exit Status
EXIT_OK = 0
EXIT_FATAL_INVALID_OPTIONS = 3
EXIT_FATAL_INVALID_ARGUMENTS = 7
EXIT_RETURN_FALSE = 40

# Set logging
logging.basicConfig(format='%(asctime)-15s [%(levelname)s] %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_tags():
    # type: () -> None
    """Return the name of tags as list"""
    logging.info("get-tags for %s/%s", args.repo_name, args.docker_name)

    tags_list = DockerImage.list_tags(args.repo_name, args.docker_name)
    print('\n'.join(str(tag) for tag in tags_list))


def has_tag():
    # type: () -> None
    """Whether the docker image has the given tag"""

    if DockerImage.has_tag(args.repo_name, args.docker_name, args.tag):
        print("yes")
        sys.exit(EXIT_OK)
    else:
        print("no")
        sys.exit(EXIT_RETURN_FALSE)


def dockerfile_update():
    # type: () -> None
    "Update the Dockerfile according to given tag"
    image = DockerImage(args.repo_name, args.docker_name, args.tag)
    image.dockerfile_update()


def publish():
    # type: () -> None
    """Publish docker image to docker hub, as well as git commit"""
    if DockerImage.has_tag(args.repo_name, args.docker_name, args.tag):
        logger.error("Tag %s already exists", args.tag)
        sys.exit(EXIT_FATAL_INVALID_ARGUMENTS)
    else:
        logging.info("docker tag to be publish: %s", args.tag)

    # Update Docker file
    image = DockerImage(args.repo_name, args.docker_name, args.tag)
    image.dockerfile_update()
    if subprocess.call([GitHelper.GIT_CMD, 'diff', '--exit-code']) != 0:
        subprocess.check_call([
                GitHelper.GIT_CMD, 'commit', '-a', '-m',
                "[release] Image %s is released" % image.image_name])

    # Building docker image
    logging.info("Building image %s", image.image_name)
    subprocess.check_call([
            DockerImage.DOCKER_CMD, 'build',
            '-t', image.image_name, image.dockerfile_name])

    # Tag docker image
    for current_tag in [image.final_tag, 'latest']:
        subprocess.check_call([
                DockerImage.DOCKER_CMD, 'tag', image.image_name,
                "%s/%s/%s:%s" % (
                        args.registry, args.repo_name,
                        args.docker_name, current_tag)])

    # Pushing docker image
    for current_tag in [image.final_tag, 'latest']:
        subprocess.check_call([
                DockerImage.DOCKER_CMD, 'push',
                "%s/%s/%s:%s" % (
                        args.registry, args.repo_name,
                        args.docker_name, current_tag)])

    # Git push to master if there is unpushed commits
    GitHelper.push('master')


if __name__ == '__main__':
    # Parse options and arguments
    parser = argparse.ArgumentParser(description='Docker helper functions')
    parser.add_argument(
            '-r', '--repo-name', type=str,
            default='zanata',
            help='Docker Repository name. Default: zanata')
    parser.add_argument(
            '-R', '--registry', type=str,
            default='docker.io',
            help='Docker Registry name. Default: docker.io')

    subparsers = parser.add_subparsers(
            title='Command', description='Valid commands',
            help='Command help')
    has_tag_parser = subparsers.add_parser(
            'has-tag',
            help='Whether the docker image has the given tag')
    has_tag_parser.add_argument(
            'docker_name', type=str,
            help='Docker name, e.g. "server"')
    has_tag_parser.add_argument('tag', type=str, help='tag')
    has_tag_parser.set_defaults(func=has_tag)

    get_tags_parser = subparsers.add_parser(
            'get-tags',
            help='Get all existing tags')
    get_tags_parser.add_argument(
            'docker_name', type=str,
            help='Docker name, e.g. "server"')
    get_tags_parser.set_defaults(func=get_tags)

    dockerfile_update_parser = subparsers.add_parser(
            'dockerfile-update',
            help='Update the Dockerfile according to tag')
    dockerfile_update_parser.add_argument(
            'docker_name', type=str,
            help='Docker name, e.g. "server"')
    dockerfile_update_parser.add_argument(
            'tag', type=str,
            help='tag to be publish')
    dockerfile_update_parser.set_defaults(func=dockerfile_update)

    publish_parser = subparsers.add_parser(
            'publish',
            help='publish docker image according to the tag')
    publish_parser.add_argument(
            'docker_name', type=str,
            help='Docker name, e.g. "server"')
    publish_parser.add_argument(
            'tag', type=str,
            help='tag to be publish')
    publish_parser.set_defaults(func=publish)

    args = parser.parse_args()
    args.func()
