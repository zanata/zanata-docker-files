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

class DockerTag:
    "Docker image tag, it may contains version-postrelease, version, or simply 'latest'"
    def __init__(self, tag):
        # type: (str) -> None
        match = re.search('^([^-]*)-(.*)', tag)
        if match:
            self.version = match.group(1)
            self.extra = match.group(2)
            if re.match('^[a-zA-Z]', self.extra):
                ## alpha or rc
                self.prerelease = self.extra
                self.artifactVersion = tag
            else:
                self.postrelease = self.extra
                self.artifactVersion = self.version
        elif re.match('^[0-9.]*', tag):
            self.version = tag
        else:
            pass

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

_docker_name_db = {
    'server': {
        'dir': 'zanata-server',
        'url': 'https://github.com/zanata/zanata-platform',
        'tag_prefix': 'platform-',
    }
}

def _docker_name_to_dir(docker_name):
    # type: (str) -> str
    """Convert docker_name to the directory that contains Dockerfile"""
    if (docker_name in _docker_name_db):
        return _docker_name_db[docker_name]['dir']
    return docker_name

def _get_tag_names(docker_name):
    # type: (str) -> List[str]
    """Return the name of tags as list"""
    tag_url = 'https://registry.hub.docker.com/v2/repositories/' + args.repo_name + '/' + docker_name + '/tags/'
    result = [] # type: List[str]
    while tag_url:
        ## Enforce https
        tag_url_without_protocal = re.sub('^[^:/]+://', '', tag_url)
        logging.info("Getting tags from https://" + tag_url_without_protocal)
        response = urllib2.urlopen('https://' + tag_url_without_protocal)
        logging.debug(response.info())

        tags_json = json.load(response)
        result += [elem["name"] for elem in tags_json["results"]]
        tag_url = tags_json.get("next", "")
    return result

def get_tags(args):
    # type: (argparse.Namespace) -> None
    """Return the name of tags as list"""
    logging.info("get-tags for %s/%s", args.repo_name, args.docker_name)

    tags_list = _get_tag_names(args.docker_name)
    print('\n'.join(str(tag) for tag in tags_list))

def _has_tag(docker_name, tag):
    # type: (str, str) -> int
    """Whether the docker image has the given tag"""

    tags_list = _get_tag_names(docker_name)
    return tag in tags_list

def has_tag(args):
    # type: (argparse.Namespace) -> None
    """Whether the docker image has the given tag"""

    if _has_tag(args.docker_name, args.tag):
        print("yes")
        sys.exit(EXIT_OK)
    else:
        print("no")
        sys.exit(EXIT_RETURN_FALSE)

def git_remote_get_latest_tag(repo_url, tag_glob = '*'):
    # type: (str, str) -> str
    tag = subprocess.check_output(
            [
                GIT_CMD, 'ls-remote', '--tags',
                repo_url,
                'refs/tags/' + tag_glob + '[^^{}]'
            ]).split()[-1].split('/')[-1]
    logging.info("latest tag of %s is %s", repo_url, tag)
    return tag

def git_remote_get_latest_version(repo_url, tag_prefix = None):
    # type: (str, str) -> str
    return git_remote_get_latest_tag(repo_url,
            tag_prefix + '*' if tag_prefix else '*')[len(tag_prefix if tag_prefix else 0):]

def _next_release(docker_name, version):
    # type: (str, str) -> int
    prog = re.compile("^%s-([0-9]+)" % version)
    current_release = 0
    for tag in _get_tag_names(docker_name):
        m = re.match(prog, tag)
        if not m:
            continue
        if int(m.group(1)) > current_release:
            current_release = int(m.group(1))
    return current_release + 1

def _next_version_release(docker_name):
    if docker_name in _docker_name_db:
        version = git_remote_get_latest_version(
                _docker_name_db[docker_name]['url'],
                _docker_name_db[docker_name]['tag_prefix'])
        next_release = _next_release(docker_name, version)
        return "%s-%s" % (version, next_release)
    else:
        logger.error("next_version_release does not support docker_name %s" % docker_name)
        sys.exit(EXIT_FATAL_INVALID_ARGUMENTS)

def _dockerfile_update(docker_name, tag):
    # type: (str, str) -> int
    """Update the Dockerfile according to tag, it accepts either x.y.z-r or 'auto' as tag"""

    image_tag = DockerTag(tag)
    release = 1 if not hasattr(image_tag, 'postrelease') else int(image_tag.postrelease)
    dockerfile_name = _docker_name_to_dir(docker_name) + '/Dockerfile'

    dockerfile_file = fileinput.FileInput([dockerfile_name], inplace=1, backup='.bak')
    for line in iter(dockerfile_file):
        if re.match(r'^ARG ZANATA_VERSION=.*$', line):
            sys.stdout.write(re.sub(r'^ARG ZANATA_VERSION=.*$',
                    'ARG ZANATA_VERSION=' + image_tag.version, line))
        elif re.match(r'\s*Release="([0-9]+)"', line):
            sys.stdout.write((re.sub(r'Release=".*"',
                    ('Release="%s"' % (release)) , line)))
        else:
            sys.stdout.write(line)

    sys.stdout.flush()
    dockerfile_file.close()

def docker_tag_determine(args):
    # type: (argparse.Namespace) -> str
    """Docker tag can be either in the form of x.y.z-r, or 'auto'.
    This function resolves the actual docker tag name."""
    return args.tag if not args.tag == 'auto' else _next_version_release(args.docker_name)

def dockerfile_update(args):
    # type: (argparse.Namespace) -> int
    _dockerfile_update(args.docker_name, docker_tag_determine(args))

def publish(args):
    # type: (argparse.Namespace) -> None
    """Publish docker image to docker hub, as well as git commit"""
    tag = docker_tag_determine(args)
    logging.info("docker tag to be publish: %s", tag)
    if _has_tag(args.docker_name, tag):
        logger.error("Tag %s already exists", tag)
        sys.exit(EXIT_FATAL_INVALID_ARGUMENTS)

    ## Update Docker file
    _dockerfile_update(args.docker_name, tag)
    docker_image_name = "%s/%s:%s" % (args.repo_name, args.docker_name, tag)
    if subprocess.call([GIT_CMD, 'diff', '--exit-code']) != 0:
        subprocess.check_call([
                GIT_CMD, 'commit', '-a', '-m',
                "[release] Image %s is released" % docker_image_name])

    ## Building docker image
    logging.info("Building image %s", docker_image_name)
    subprocess.check_call([
            DOCKER_CMD, 'build', '-t', docker_image_name, _docker_name_to_dir(args.docker_name)])

    ## Tag docker image
    for t in [ tag, 'latest' ]:
        subprocess.check_call([
                DOCKER_CMD, 'tag', docker_image_name,
                "%s/%s/%s:%s" % (args.registry, args.repo_name, args.docker_name, t)])

    ## Pushing docker image
    for t in [ tag, 'latest' ]:
        subprocess.check_call([
                DOCKER_CMD, 'push',
                "%s/%s/%s:%s" % (args.registry, args.repo_name, args.docker_name, t)])

    ## Git push to master if there is unpushed comments
    if subprocess.call(GIT_CMD, "diff", "--exit-code", "origin", "HEAD") != 0 :
        # git_detached_merge_branch is needed in Jenkins as it checkout as detached
        subprocess.check_call(CURL_CMD + "-q https://raw.githubusercontent.com/zanata/zanata-scripts/master/zanata-functions | bash -s - run git_detached_merge_branch master", shell=True)
        subprocess.check_call([GIT_CMD, 'push', 'origin', 'master'])

if __name__ == '__main__':
    ## Parse options and arguments
    parser = argparse.ArgumentParser(description='Docker helper functions')
    parser.add_argument('-r', '--repo-name', type=str,
            default = 'zanata',
            help = 'Docker Repository name. Default: zanata')
    parser.add_argument('-R', '--registry', type=str,
            default = 'docker.io',
            help = 'Docker Registry name. Default: docker.io')

    subparsers = parser.add_subparsers(title='Command',
            description='Valid commands',  help='Command help')
    has_tag_parser = subparsers.add_parser('has-tag',
            help = 'Whether the docker image has the given tag')
    has_tag_parser.add_argument('docker_name', type=str,
            help = 'Docker name, e.g. "server"')
    has_tag_parser.add_argument('tag', type=str, help = 'tag')
    has_tag_parser.set_defaults(func=has_tag)

    get_tags_parser = subparsers.add_parser('get-tags',
            help = 'Get all existing tags')
    get_tags_parser.add_argument('docker_name', type=str,
            help = 'Docker name, e.g. "server"')
    get_tags_parser.set_defaults(func=get_tags)

    dockerfile_update_parser = subparsers.add_parser('dockerfile-update',
            help = 'Update the Dockerfile according to tag')
    dockerfile_update_parser.add_argument('docker_name', type=str,
            help = 'Docker name, e.g. "server"')
    dockerfile_update_parser.add_argument('tag', type=str,
            help = 'tag to be publish')
    dockerfile_update_parser.set_defaults(func=dockerfile_update)

    publish_parser = subparsers.add_parser('publish',
            help = 'publish docker image according to the tag')
    publish_parser.add_argument('docker_name', type=str,
            help = 'Docker name, e.g. "server"')
    publish_parser.add_argument('tag', type=str,
            help = 'tag to be publish')
    publish_parser.set_defaults(func=publish)

    args = parser.parse_args()
    args.func(args)

