################################################################################
# atd.py - The Unix at scheduler in Python ################## py2k version 0.1 #
################################################################################
# `at` is a command line utility, like cron, that schedules commands to be run #
# at a later time. Unlike cron, whose main purpose is to run a command every n #
# minutes, the purpose of `at` is to run a command once at a known time.       #
# This makes `at` ideal for scheduling jobs. Say you want to run a command 6   #
# hours after an action is taken in your application, with `at` you can. `at`  #
# also is superior to scheduling daemons that keep jobs in RAM, because it     #
# writes its jobs to a recoverable spool on the disk.                          #
################################################################################
## Written by Fredrick Brennan <admin@8chan.co>. Expat License - See LICENSE. ##
################################################################################

import sys
import os
import pipes
from subprocess import Popen, PIPE, check_call
import tempfile
import warnings
import datetime
import re
import json

# Submodules #
from atq import AtQueue, AtJob
import config

def at(command, when, queue = 'a'):
    """ Execute command at when. 

        command may be anything interpreble by /bin/sh. If you need features
        specific to another shell, create a script and then make the command
        <path to shell> <path to script>.

        when may be a datetime.timedelta, a datetime.datetime or a timespec str.
        If a string is provided, it is assumed that it's a valid timespec. See 
        `timespec` doc in `at`'s documentation. """
    posix_time = False
    if isinstance(when, datetime.datetime):
        timespec = convert_datetime(when)
        posix_time = True
    elif isinstance(when, datetime.timedelta):
        timespec = convert_timedelta(when)
    elif isinstance(when, basestring):
        timespec = when # TODO: Validate timespec?
    else:
        raise NotImplementedError('I don\'t support the class you pass'+
                'ed to schedule(). Try the builtin datetime.')

    # Build our `at` command line arguments...
    atargs = list([config.at_binary])
    queue = _validate_queue(queue)
    if posix_time: 
        atargs.append('-t')

    atargs.extend(timespec.split(" "))

    if config.always_send_mail:
        atargs.append('-m')
    elif config.never_send_mail:
        atargs.append('-M')

    # Prevent creation of a needless subprocess by using a temporary file.
    # StringIO cannot be used due to Popen's use of fileno().
    at_stdin = tempfile.TemporaryFile()
    at_stdin.write(command)
    at_stdin.seek(0)

    # Build our Popen keyword arguments...
    atkwargs = dict(stdin=at_stdin, stdout=PIPE, stderr=PIPE)
    if not config.inherit_env:
        atkwargs['env'] = config.atjob_environment

    sp = Popen(atargs, **atkwargs) 
    (at_stdout, at_stderr) = sp.communicate()
    at_stdin.close()

    atjob = AtJob()
    atjob.from_at_stderr(at_stderr)
    atjob.command = command
    atjob.when = when
    atjob.who = os.getenv("LOGNAME")

    return atjob

def atrm(*atjobs):
    """ Cancel one or more AtJobs. Takes an AtJob instance returned by at().
        You may also choose to save the at job ID in a database, and pass its ID
        to cancel(). """
    atrm_args = [config.at_binary, '-r']
    atrm_args.extend([str(job.id) for job in atjobs])

    return (check_call(atrm_args) == 0)

def clear():
    """ Cancel all atjobs. """
    atjobs = AtQueue().jobs
    atrm(*atjobs)

def _can_read_file(self, filename):
    """ On many installations, at.allow and at.deny are not readable by non-root
        users. Assure that they are. """
    if not os.access(filename, os.F_OK): # No file there
        return False

    if not os.access(filename, os.R_OK): # Can't read file
        raise OSError('No permission to use {0}. Try the ' +
        'command `chown 644 {0}` as root.').format(filename)

def _enumerate_users(filename):
    """ Enumerate users in a at.allow or at.deny file, and return them as a 
        list() for the user. """
    if not _can_read_file(filename): # No file there
            return []

    fd = open(filename, 'r')
    users = fd.readlines()
    fd.close()

    return [user.strip() for user in users]

def _validate_queue(queue):
    return queue

def get_allowed_users():
    """ Get a list() of all users allowed to use `at`, or raise an OSError if we
        can't determine it for some reason. """
    return _enumerate_users(config.at_allow_file)

def get_denied_users():
    """ Get a list() of all users disallowed from `at`, or raise an OSError if 
        we can't determine it for some reason. """
    return _enumerate_users(config.at_deny_file)

def convert_datetime(dt):
    """ Convert a datetime object to a POSIX timestamp usable by `at`. It 
        returns a string.

        From the `at` manual:
        -t      Specify the job time using the POSIX time format.  The
        argument should be in the form [[CC]YY]MMDDhhmm[.SS]. """
    if dt.year >= 2038 and (2**64 / 2) - 1 != long(sys.maxsize):
        raise RuntimeWarning('Year >= 2038 detected on system running 32 bit '+ 
        'Python. `at` has undefined behavior with years >= 2038. Please make '+
        'sure your system is 64bit, even if your Python binary isn\'t.')

    return dt.strftime("%C%y%m%d%H%M.%S")

def convert_timedelta(td):
    """ Convert a timedelta object to a timespec usable by `at`. Note that
    `at` does not understand seconds, so extra seconds are rounded down. """
    return 'now + {0} minutes'.format((td.seconds // 60))

# Just some fun examples of how the module works...
if __name__ == "__main__":
    print 'Create some jobs...'
    job1 = at("echo lol >> /tmp/lolol", datetime.datetime.now() + 
            datetime.timedelta(minutes = 2))
    job2 = at("rm /tmp/lolol", datetime.timedelta(minutes=5))

    print "Job 1: {0}".format(job1)
    print "Job 2: {0}".format(job2)

    print 'All right, free up those vars...'
    del job1; del job2

    print 'Check our atd queue for our jobs (`atq`)'
    atq = AtQueue()
    print [str(job) for job in atq.jobs]

    print 'Cancel all our jobs.'
    print [atrm(job) for job in atq.jobs]

    print 'Refresh the AtQueue...'
    atq.refresh()

    print 'Poof!'
    print [str(job) for job in atq.jobs]

    #print 'All right, let\'s have some more fun. Performance test, create'+\
        #' 1,024 jobs.'

    #for i in xrange(1,1024):
        #at("echo lol >> /tmp/lolol", "now + 24 hours")

    #print 'Created 1,024 jobs.'

    #atq.refresh()

    #print 'Counted {0} jobs.'.format(len(atq.jobs))

    #for job in atq.jobs: atrm(job)

    #print 'Deleted {0} jobs.'.format(len(atq.jobs))
