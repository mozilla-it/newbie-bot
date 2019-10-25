#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
'''
config
'''

import os
import re
import pwd
import sys
import time
import logging

from datetime import datetime
from decouple import UndefinedValueError, AutoConfig, config
from functools import lru_cache
from subprocess import Popen, CalledProcessError, PIPE

LOG_LEVELS = [
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL',
]

LOG_LEVEL = config('LOG_LEVEL', logging.WARNING, cast=int)

logging.basicConfig(
    stream=sys.stdout,
    level=LOG_LEVEL,
    format='%(asctime)s %(name)s %(message)s')
logging.Formatter.converter = time.gmtime
log = logging.getLogger(__name__)

class ProjNameSplitError(Exception):
    '''
    ProjNameSplitError
    '''
    def __init__(self, basename):
        '''
        init
        '''
        msg = f'projname split error on "-" with basename={basename}'
        super(ProjNameSplitError, self).__init__(msg)

class NotGitRepoError(Exception):
    def __init__(self, cwd=os.getcwd()):
        msg = f"not a git repository error cwd={cwd}"
        super().__init__(msg)


class GitCommandNotFoundError(Exception):
    def __init__(self):
        msg = "git: command not found"
        super().__init__(msg)


def call(
    cmd, stdout=PIPE, stderr=PIPE, shell=True, nerf=False, throw=True, verbose=False
):
    if verbose or nerf:
        logger.info(f"verbose cmd={cmd}")
        pass
    if nerf:
        return (None, "nerfed", "nerfed")
    process = Popen(cmd, stdout=stdout, stderr=stderr, shell=shell)
    _stdout, _stderr = [
        stream.decode("utf-8") if stream != None else None
        for stream in process.communicate()
    ]
    exitcode = process.poll()
    if verbose:
        if _stdout:
            logger.info(f"verbose stdout={_stdout}")
        if _stderr:
            logger.info(f"verbose stderr={_stderr}")
            pass
    if throw and exitcode:
        raise CalledProcessError(
            exitcode, f"cmd={cmd}; stdout={_stdout}; stderr={_stderr}"
        )
    return exitcode, _stdout, _stderr


def git(args, strip=True, **kwargs):
    try:
        _, stdout, stderr = call("git rev-parse --is-inside-work-tree")
    except CalledProcessError as ex:
        if "not a git repository" in str(ex):
            raise NotGitRepoError
        elif "git: command not found" in str(ex):
            raise GitCommandNotFoundError
        else:
            logger.error("failed repo check but NOT a NotGitRepoError???", ex=ex)
    try:
        _, result, _ = call(f"git {args}", **kwargs)
        if result:
            result = result.strip()
        return result
    except CalledProcessError as ex:
        logger.error(ex)
        raise ex

class AutoConfigPlus(AutoConfig): #pylint: disable=too-many-public-methods
    '''
    thin wrapper around AutoConfig adding some extra features
    '''

    @property
    def APP_UID(self):
        '''
        uid
        '''
        return os.getuid()

    @property
    def APP_GID(self):
        '''
        gid
        '''
        return pwd.getpwuid(self.APP_UID).pw_gid

    @property
    def APP_USER(self):
        '''
        user
        '''
        return pwd.getpwuid(self.APP_UID).pw_name

    @property
    def APP_PORT(self):
        '''
        port
        '''
        return self('APP_PORT', 5000, cast=int)

    @property
    def APP_JOBS(self):
        '''
        jobs
        '''
        try:
            return call('nproc')[1].strip()
        except: #pylint: disable=bare-except
            return 1

    @property
    def APP_TIMEOUT(self):
        '''
        timeout
        '''
        return self('APP_TIMEOUT', 120, cast=int)

    @property
    def APP_WORKERS(self):
        '''
        workers
        '''
        return self('APP_WORKERS', 2, cast=int)

    @property
    def APP_MODULE(self):
        '''
        module
        '''
        return self('APP_MODULE', 'main:app')

    @property
    def APP_REPOROOT(self):
        '''
        reporoot
        '''
        try:
            return git('rev-parse --show-toplevel')
        except NotGitRepoError:
            return self('APP_REPOROOT')

    @property
    def APP_TAGNAME(self):
        '''
        tagname
        '''
        tag = self.APP_VERSION.split('-')[0]
        depenv = {
            'prod': '',
            'stage': '-stage',
            'dev': '-dev'
        }[self.APP_DEPENV]
        return f'{tag}{depenv}'

    @property
    def APP_VERSION(self):
        '''
        version
        '''
        try:
            return git('describe --abbrev=7 --always')
        except NotGitRepoError:
            return self('APP_VERSION')

    @property
    def APP_BRANCH(self):
        '''
        branch
        '''
        try:
            return git('rev-parse --abbrev-ref HEAD')
        except NotGitRepoError:
            return self('APP_BRANCH')

    @property
    def APP_DEPENV(self):
        '''
        depenv
        '''
        env = 'dev'
        if self.APP_BRANCH == 'master':
            env = 'prod'
        elif self.APP_BRANCH.startswith('stage/'):
            env = 'stage'
        return env

    @property
    def APP_SRCTAR(self):
        '''
        srctar
        '''
        try:
            return self('APP_SRCTAR')
        except UndefinedValueError:
            return '.src.tar.gz'

    @property
    def APP_REVISION(self):
        '''
        revision
        '''
        try:
            return git('rev-parse HEAD')
        except NotGitRepoError:
            return self('APP_REVISION')

    @property
    def APP_REMOTE_ORIGIN_URL(self):
        '''
        remote origin url
        '''
        try:
            return git('config --get remote.origin.url')
        except NotGitRepoError:
            return self('APP_REMOTE_ORIGIN_URL')

    @property
    def APP_REPONAME(self):
        '''
        reponame
        '''
        pattern = r'((ssh|https)://)?(git@)?github.com[:/](?P<reponame>[A-Za-z0-9\/\-_]+)(.git)?'
        match = re.search(pattern, self.APP_REMOTE_ORIGIN_URL)
        return match.group('reponame')

    @property
    def APP_PROJNAME(self):
        '''
        projname
        '''
        basename = os.path.basename(self.APP_REPONAME)
        parts = os.path.basename(basename).split('-')
        if len(parts) == 2:
            return parts[0]
        raise ProjNameSplitError(basename)

    @property
    def APP_PROJPATH(self):
        '''
        projpath
        '''
        return os.path.join(self.APP_REPOROOT, self.APP_PROJNAME)

    @property
    def APP_BOTPATH(self):
        '''
        botpath
        '''
        return os.path.join(self.APP_PROJPATH, 'bot')

    @property
    def APP_DBPATH(self):
        '''
        dbpath
        '''
        return os.path.join(self.APP_PROJPATH, 'db')

    @property
    def APP_TESTPATH(self):
        '''
        testpath
        '''
        return os.path.join(self.APP_REPOROOT, 'tests')

    @property
    def APP_LS_REMOTE(self):
        '''
        ls-remote
        '''
        try:
            result = git(f'ls-remote https://github.com/{self.APP_REPONAME}')
        except NotGitRepoError:
            result = self('APP_LS_REMOTE')
        return {
            refname: revision for revision, refname in [line.split() for line in result.split('\n')]
        }

    @property
    def APP_GSM_STATUS(self):
        '''
        gsm status
        '''
        try:
            result = git('submodule status', strip=False)
        except NotGitRepoError:
            result = self('APP_GSM_STATUS')
        pattern = r'([ +-])([a-f0-9]{40}) ([A-Za-z0-9\/\-_.]+)( .*)?'
        matches = re.findall(pattern, result)
        states = {
            ' ': True,  # submodule is checked out the correct revision
            '+': False, # submodule is checked out to a different revision
            '-': None,  # submodule is not checked out
        }
        return {
            repopath: [revision, states[state]] for state, revision, repopath, _ in matches
        }

    def __getattr__(self, attr):
        '''
        getattr
        '''
        log.info(f'attr = {attr}')
        if attr == 'create_doit_tasks': #note: to keep pydoit's hands off
            return lambda: None
        result = self(attr)
        try:
            return int(result)
        except ValueError:
            return result

CFG = AutoConfigPlus()
