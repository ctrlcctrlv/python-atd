################################################################################
# atd.py - The Unix at scheduler in Python ################## py2k version 0.1 #
################################################################################
## Written by Fredrick Brennan <admin@8chan.co>. Expat License - See LICENSE. ##
################################################################################
# Unit tests for AtQueue, AtJob, and `at` utilities...                         #
#                                                                              #
# It is highly recommended to run the unit tests before using `atd.py` in a    #
# production environment. The unit tests can give you valuable information     #
# about the setup of your atd and whether atjob creation and cancelation       #
# is working as expected.                                                      #
################################################################################

import atd
import unittest
import datetime

class TimeConversionTests(unittest.TestCase):
    def test_datetime(self):
        dt = datetime.datetime(2015, 9, 16, 17, 8, 22, 496479)

        self.assertEqual(atd.convert_datetime(dt), '201509161708.22')

        print "Success: Datetime conversion"

    def test_timedelta(self):
        td = datetime.timedelta(seconds = 60)
        td2 = datetime.timedelta(seconds = 120)
        td3 = datetime.timedelta(days = -1)

        self.assertEqual(atd.convert_timedelta(td), 'now + 1 minute')

        self.assertEqual(atd.convert_timedelta(td2), 'now + 2 minutes')

        self.assertEqual(atd.convert_timedelta(td3), 'now + -1440 minutes')

        print "Success: Timedelta conversion"

class ScheduleTests(unittest.TestCase):
    def test_at_cancel(self):
        job = atd.at("echo lol", datetime.timedelta(seconds=7200))

        self.assertGreater(job.id, 0)

        print "Success: Created atjob {}".format(job.id)

        # Test if we can find our job again by command in `atq`
	atq = atd.AtQueue()

        n_jobs = len(atq.jobs)
    
        # We should have at least one job in the queue since we just created
        # one above ...
        self.assertGreater(n_jobs, 0) 

        print "Success: At least one job in queue ({} jobs)".format(n_jobs)

        our_job = None
        for j in atq.jobs:
            if job.command == "echo lol":
                our_job = j

        self.assertIsNotNone(our_job)
        self.assertEqual(our_job.id, job.id)

        print "Success: Found our job again. Job #{}".format(our_job.id)

        result = atd.atrm(our_job)
        
        self.assertTrue(result)

        print "Success: Deleted our job"

class NoNullAtJobComparisonTest(unittest.TestCase):
    def test_null_atjob_comparison(self):
        atj1 = atd.AtJob(0)
        atj2 = atd.AtJob(0)

        self.assertNotEqual(atj1, atj2)
        print "Success: Null atjobs not equal"

if __name__ == '__main__':
    unittest.main()
