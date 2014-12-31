__author__ = 'yufa'

import logging
import logging.config
import ConfigParser

import ezdb

logging.config.fileConfig('logging.cnf')
config = ConfigParser.ConfigParser()
config.read('ezdb.cnf')


def parse_options(section, option):
	try:
		return config.get(section, option)
	except ConfigParser.NoOptionError:
		print 'Make sure option [%s] is set under section [%s].' % (option, section)
	except ConfigParser.NoSectionError:
		print 'Make sure section [%s] is set.' % section


_boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                   '0': False, 'no': False, 'false': False, 'off': False}

enable_snapshot = parse_options('snapshot_function', 'enable_snapshot')
common_db_dir = parse_options('db_compiler', 'common_db_dir')
source_db_dir = parse_options('db_compiler', 'source_db_dir')
target_db_dir = parse_options('db_compiler', 'target_db_dir')
release_number = parse_options('db_compiler', 'release_number')

enable_snapshot = _boolean_states.get(enable_snapshot.lower(), False)
if enable_snapshot:
	ezdb.enable_snapshot(enable_snapshot)

if common_db_dir and source_db_dir and target_db_dir and release_number:
	ezdb.compile_db(common_db_dir, source_db_dir, target_db_dir, release_number)
