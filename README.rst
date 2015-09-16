
atd package
===========


Submodules
==========


atd module
==============

at(command, when, queue='a')

   Execute command at when.

   command may be anything interpretable by /bin/sh. If you need
   features specific to another shell, create a script and then make
   the command <path to shell> <path to script>.

   when may be a datetime.timedelta, a datetime.datetime or a timespec
   str. If a string is provided, it is assumed that it's a valid
   timespec. See  *timespec* doc in *at*'s documentation.

atrm(*atjobs)

   Cancel one or more AtJobs. Takes an AtJob instance returned by
   at(). You may also choose to save the at job ID in a database, and
   pass its ID to cancel().

clear()

   Cancel all atjobs.

convert_datetime(dt)

   Convert a datetime object to a POSIX timestamp usable by *at*. It
   returns a string.

   From the *at* manual: -t      Specify the job time using the POSIX
   time format.  The argument should be in the form
   [[CC]YY]MMDDhhmm[.SS].

convert_timedelta(td)

   Convert a timedelta object to a timespec usable by *at*. Note that
   *at* does not understand seconds, so extra seconds are rounded
   down.

get_allowed_users()

   Get a list() of all users allowed to use *at*, or raise an OSError
   if we can't determine it for some reason.

get_denied_users()

   Get a list() of all users disallowed from *at*, or raise an OSError
   if we can't determine it for some reason.


atq module
==============

class class atq.AtJob(jobid=0, load=False)

   Bases: "object"

   from_at_stderr(stderr)

      Called by at(), it creates an AtJob from *at*'s stderr.

   load()

      For performance reasons, information about atjobs is lazy-loaded
      on request (see __get__()). However, you can force load all of
      it with this function, for example for pretty instantaneous JSON
      output from __repr__().

class class atq.AtQueue(queue=False)

   Bases: "object"

   The AtQueue class represents the state of the *at* queue at the
   time when it was initialized. Jobs are stored as a list in
   AtQueue.jobs.

   find_job_by_id(id)

      Simply iterate through AtQueue.jobs and return the job with the
      given id. Raise ValueError if no job in AtQueue.

   refresh()

      Refresh this AtQueue, reading from *atq* again. This is
      automatically called on instantiation. self.jobs becomes a list
      of AtJob objects.


config module
=================


tests module
================

class class tests.NoNullAtJobComparisonTest(methodName='runTest')

   Bases: "unittest.case.TestCase"

   test_null_atjob_comparison()

class class tests.ScheduleTests(methodName='runTest')

   Bases: "unittest.case.TestCase"

   test_at_cancel()

class class tests.TimeConversionTests(methodName='runTest')

   Bases: "unittest.case.TestCase"

   test_datetime()

   test_timedelta()


Module contents
===============
