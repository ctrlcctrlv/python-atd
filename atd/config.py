import sys

# Global config for this module.

# Handle platform specific differences between `at`
if sys.platform == 'win32':
	raise NotImplementedError('Windows does not support ' +
	'`at` out of the box. Try cygwin! <https://cygwin.com>')

if sys.platform.startswith('linux') or \
sys.platform.startswith('cygwin'):
	at_allow_file = '/etc/at.allow'
	at_deny_file = '/etc/at.deny'
        at_default_queue = 'a'
        batch_default_queue = 'b'
else: # freebsd and darwin (OS X)
	at_allow_file = '/var/at/at.allow'
	at_deny_file = '/var/at/at.deny'
        at_default_queue = 'c'
        batch_default_queue = 'E'

at_binary = '/usr/bin/at'
atq_binary = '/usr/bin/atq'

always_send_mail = False
never_send_mail = False

# Use of this flag is discourged, but supported. It's discoraged because it can 
# lead to difficult to find bugs. Learn what environment variables your atjobs 
# need, and pass them.
#
inherit_env = False
# By default, not even PATH is inherited. That depends on shell and context. For
# example, if you run `at` typically from bash and your webserver runs it from 
# csh, those are two different PATHs. Put the PATH that you need explicitly in 
# your config.
#
#     "Explicit is better than implicit." ~ The Zen of Python
#
atjob_environment = dict(PATH = "/bin:/usr/bin")
