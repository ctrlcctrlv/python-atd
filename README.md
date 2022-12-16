atd package (v0.2.2)
====================

https://pypi.org/project/python-atd/

at is the companion of cron. While cron says "execute command every 5 minutes",
at says, "execute command once at exactly 2:00 PM". at is the original Unix
scheduler.

This Python module aims to support all at operations in a safe way.

Installation
============

```bash
pip install python-atd
```

Tests
=====

If installing from repository with `python setup.py install`, it's recommended
to run the tests to make sure at is configured properly.

Supports Python 2 and Python 3.

Simple usage example
====================

```python3
from atd import atd
import datetime

print('Create some jobs...')
job1 = atd.at("echo lol >> /tmp/lolol", datetime.datetime.now() + 
	datetime.timedelta(minutes = 2))
job2 = atd.at("rm /tmp/lolol", datetime.timedelta(minutes=5))

print("Job 1: {0}".format(job1))
print("Job 2: {0}".format(job2))

print('All right, free up those vars...')
del job1; del job2

print('Check our atd queue for our jobs (`atq`)')
atq = atd.AtQueue()
print [str(job) for job in atq.jobs]

print('Cancel all our jobs.')
print [atd.atrm(job) for job in atq.jobs]

print('Refresh the AtQueue...')
atq.refresh()

print('Poof!')
print [str(job) for job in atq.jobs]
```

Submodules
==========

atd module
==========

at(command, when, queue='a')

> Execute command at when.
>
> command may be anything interpreble by /bin/sh. If you need features specific
> to another shell, create a script and then make the command &lt;path to
> shell&gt; &lt;path to script&gt;.
>
> when may be a datetime.timedelta, a datetime.datetime or a timespec str. If a
> string is provided, it is assumed that it's a valid timespec. See *timespec*
> doc in at's documentation.
> 
> python-atd also has good support for named queues. Both GNU and BSD at
> support the concept of named queues, which allow you to easily separate
> different types of jobs based on type.For example, if you owned a bank, you'd
> have different types of jobs. Check clearing might go in queue "c" 24 hours
> after request, while international wire clearing would go in queue "i" 48
> hours after request. An unfortunate limitation of at is that all jobs can
> only be one letter, A-Z or a-z. This means there are only 52 available queues
> in both BSD at and GNU at.

atrm(\*atjobs)

> Cancel one or more AtJobs. Takes an AtJob instance returned by at(). You may
> also choose to save the at job ID in a database, and pass its ID to cancel().

clear(queue = False)

> Cancel all atjobs. You may also specify a queue.

convert\_datetime(dt)

> Convert a datetime object to a POSIX timestamp usable by at. It returns a
> string.
>
> From the at manual: -t Specify the job time using the POSIX time format. The
> argument should be in the form \[\[CC\]YY\]MMDDhhmm\[.SS\].

convert\_timedelta(td)

> Convert a timedelta object to a timespec usable by at. Note that at does not
> understand seconds, so extra seconds are rounded down.

get\_allowed\_users()

> Get a list() of all users allowed to use at, or raise an OSError if we can't
> determine it for some reason.

get\_denied\_users()

> Get a list() of all users disallowed from at, or raise an OSError if we can't
> determine it for some reason.

atq module
==========

class class atq.AtJob(jobid=0, load=False)

> Bases: "object"
>
> from\_at\_stderr(stderr)
>
> > Called by at(), it creates an AtJob from at's stderr.
>
> load()
>
> > For performance reasons, information about atjobs is lazy-loaded on request
> > (see \_\_get\_\_()). However, you can force load all of it with this
> > function, for example for pretty instantaneous JSON output from
> > \_\_repr\_\_().

class class atq.AtQueue(queue=False)

> Bases: "object"
>
> The AtQueue class represents the state of the at queue at the time when it
> was initialized. Jobs are stored as a list in AtQueue.jobs.
>
> find\_job\_by\_id(id)
>
> > Simply iterate through AtQueue.jobs and return the job with the given id.
> > Raise ValueError if no job in AtQueue.
>
> refresh()
>
> > Refresh this AtQueue, reading from atq again. This is automatically called
> > on instantiation. self.jobs becomes a list of AtJob objects.

config module
=============

tests module
============

class class tests.NoNullAtJobComparisonTest(methodName='runTest')

> Bases: "unittest.case.TestCase"
>
> test\_null\_atjob\_comparison()

class class tests.ScheduleTests(methodName='runTest')

> Bases: "unittest.case.TestCase"
>
> test\_at\_cancel()

class class tests.TimeConversionTests(methodName='runTest')

> Bases: "unittest.case.TestCase"
>
> test\_datetime()
>
> test\_timedelta()

Module contents
===============

