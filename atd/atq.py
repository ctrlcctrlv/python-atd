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

from subprocess import check_output
import datetime
import re
import json
import string

# Submodules #
import config

AT_OUTPUT_DATETIME_FORMAT = '%a %b %d %H:%M:%S %Y'
AT_OUTPUT_DATETIME_FORMAT_BSD = '%a %b %d %H:%M:%S %Z %Y'

def _validate_queue(queue):
    valid = (len(queue) == 1 and queue in (string.ascii_lowercase + \
            string.ascii_uppercase))

    if valid: 
        return queue
    else:
        raise ValueError('Invalid queue. Queues must match regex ^[A-Za-z]$')

class AtQueue(object):
    """ The AtQueue class represents the state of the `at` queue at the time 
        when it was initialized. Jobs are stored as a list in AtQueue.jobs. """
    def __init__(self, queue = False):
        """ AtQueue gets you a list of all jobs currently in the queue. Jobs 
            fall out of the queue as they are executed or canceled by you. """
        self.queue = _validate_queue(queue) if queue else False
        self.bsd = False
        self.refresh()

    def _atq_line(self, line):
        """ Parse one line of `atq` output. """
        split = line.split()
        return dict(id = int(split[0]), 
            when = datetime.datetime.strptime(
                (' ').join(split[1:6]),
                AT_OUTPUT_DATETIME_FORMAT),
            queue = split[6],
            who = split[7])

    def _atq_bsd_line(self, line):
        """ Parse one line of `atq` output. (BSD) """
        split = line.split()
        return dict(when = \
            datetime.datetime.strptime(
                (' ').join(split[0:6]),
                AT_OUTPUT_DATETIME_FORMAT_BSD), 
            who = split[6],
            queue = split[7],
            id = split[8])

    def refresh(self):
        """ Refresh this AtQueue, reading from `atq` again.
            This is automatically called on instantiation.
            self.jobs becomes a list of AtJob objects. """
        if self.queue: 
            _validate_queue(self.queue)
            atq_args = ['atq', '-q', self.queue]
        else:
            atq_args = ['atq']

        atq_out = self.raw = check_output(atq_args)
        atqlines = atq_out.splitlines()

        atqueue = list()
        
        for line in atqlines:
            # The format of BSD atq differs...
            if line.strip() == "Date\t\t\t\tOwner\t\tQueue\tJob#":
                self.bsd = True
                continue

            if self.bsd:
                parsed = self._atq_bsd_line(line)
            else:
                parsed = self._atq_line(line)

            atjob = AtJob()
            for k, v in parsed.iteritems():
                setattr(atjob, k, v)
            atqueue.append(atjob)

        self.jobs = atqueue
        return atqueue

    def find_job_by_id(self, id):
        """ Simply iterate through AtQueue.jobs and return the job with the
            given id. Raise ValueError if no job in AtQueue. """
        for job in self.jobs:
            if job.id == id:
                return job

        raise ValueError('Could not find a job with that ID.')

class AtJob(object):
    def __init__(self, jobid = 0, load = False):
        self.id = jobid
        if load: self.load()

    def __str__(self):
        return 'AtJob #{0} which executes `{2}` {3} {1}'.format(self.id,
            self.when, self.command, ('in' if isinstance(self.when,\
            datetime.timedelta) else 'at'))

    def _json_default(self, obj):
        """ For JSON serialization of `when` in AtJobs... """
        if isinstance(obj, datetime.datetime):
            return str(obj)
        elif isinstance(obj, datetime.timedelta): 
            return str(datetime.datetime.now() + obj)
        else: return obj # Unknown class...

    def __repr__(self):
        return json.dumps(self.__dict__, default=self._json_default)

    def __eq__(first, second):
        if not all([first.id, second.id]):
            return False

        return (first.id == second.id)

    def __getattr__(self, name):
        """ `at`'s behavior is quite different depending on if you're retrieving
            information about an already existing job as opposed to creating a 
            new one. To prevent unnecessary calls to `at` on class instantiation
            attributes are only sought out if they're needed. Most of the time
            just an id is enough. """
        if self.id == 0:
            raise ValueError('You tried to get info about a null ('+
            'non-existent) job. Set AtJob.id first.')

        attrs_in_atq = ['when', 'who', 'queue']

        if name in attrs_in_atq:
            atq = AtQueue()
            job = atq.find_job_by_id(self.id)
            for k in attrs_in_atq:
                setattr(self, k, getattr(job, k))

            return job.name

        # NOTE: Getting the command again after calling `at` is not
        # straightforward. This is because `at` doesn't just save the command,
        # it actually creates an entire shell script based on the command you
        # gave it to run. I decided to just take the last non-empty line of the
        # file, but if your command contained any newlines it won't work.
        # Consider (1) using semicolons and not \n or (2) not needing to get
        # the command after saving an AtJob.
        elif name == "command":
            atcat = check_output([config.at_binary, '-c', 
                str(self.id)])

            atcatlines = atcat.splitlines()

            for line in atcatlines:
                if line and line not in list('[]{}()'): 
                    lastline = line

            self.command = lastline
            return lastline

        return None
    
    def load(self):
        """ For performance reasons, information about atjobs is lazy-loaded on
        request (see __get__()). However, you can force load all of it with
        this function, for example for pretty instantaneous JSON output from
        __repr__(). """
        self.command
        self.when

        return True

    def from_at_stderr(self, stderr):
        """ Called by atd.at(), it creates an AtJob from `at`'s stderr. """
        self.raw_stderr = stderr
        match = re.match('.*job (?P<atjob_id>\d+).*', stderr, re.M|re.S)

        if not match:
            raise NotImplementedError('python-atd doesn\'t seem to'+
            ' support your version of at. Please open an issue. '+
            'stderr: {0}'.format(stderr))

        atjob_id = self.id = long(match.group('atjob_id'))
        return atjob_id

