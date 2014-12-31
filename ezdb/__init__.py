__author__ = 'yufa'

import os
import shutil
import logging

import compiler.dbobject.dbmeta as dbmeta
import compiler.xmlparser as xmlparser
import generator.ifs as installation


__all__ = ['enable_snapshot', 'compile_db']

_enable_snapshot = False


def enable_snapshot(flag=False):
	global _enable_snapshot
	_enable_snapshot = flag


def _create_db_package_structure(root_dir, db_folder, force_create=False):
	"""
	Create the folder structure of the generated db package for installation/upgrade.
	The folder structure is like -
	DB-
	 |--TOOLS
	     |--SCHEMA_CREATION
	     |--COMMON
	     |--AUTO_UPGRADE
	 |--TABLE
	 |--INIT_TABLE
	 |--VIEW
	 |--PACKAGE
	 |--PROCEDURE
	 |--FUNCTION
	 |--TYPE
	 |--TRIGGER
	 |--SEQUENCE
	 |--SYNONYM
	"""

	logging.info('Start creating the folder structure: %s.' % db_folder)

	os.chdir(root_dir)
	if os.path.exists(db_folder):
		if force_create:
			shutil.rmtree(db_folder, ignore_errors=False)
		else:
			raise Exception('Folder [DB] has already exists!')

	os.mkdir(db_folder)
	os.chdir(db_folder)
	for folder in ('TOOLS', 'TABLE', 'INIT_TABLE', 'VIEW', 'PACKAGE', 'PROCEDURE',
	               'FUNCTION', 'TYPE', 'TRIGGER', 'SEQUENCE', 'SYNONYM'):
		os.mkdir(folder)

	os.chdir('TOOLS')
	for folder in ('SCHEMA_CREATION', 'COMMON', 'AUTO_UPGRADE'):
		os.mkdir(folder)

	logging.info('Finish creating the folder structure: %s.' % db_folder)


def _generate_install_script(target_db_dir, release_number):
	"""
	Generate installation from scratch (IFS) script
	"""

	logging.info('Start generating installation script (ifs)...')

	ifs_script = os.path.join(target_db_dir, 'TOOLS', 'SCHEMA_CREATION', 'IFS_MODEL.SQL')
	with open(ifs_script, 'w') as t:
		for line in installation.generate_ifs_model_script(target_db_dir, release_number):
			t.write(line)

	logging.info('Finish generating installation script.')


def _copy_template_files(from_db_dir, to_db_dir):
	"""
	Copy the static template files (TOOLS folder) from one directory to another
	"""

	logging.info('Start copying some template files...')

	for folder in os.listdir(os.path.join(from_db_dir, 'TOOLS')):
		source_dir = os.path.join(from_db_dir, 'TOOLS', folder)
		target_dir = os.path.join(to_db_dir, 'TOOLS', folder)

		for file in os.listdir(source_dir):
			shutil.copyfile(os.path.join(source_dir, file), os.path.join(target_dir, file))

	logging.info('Finish copying template files.')


def _copy_db_raw_files(from_db_dir, to_db_dir):
	logging.info('Start copying db raw files (XML)...')

	for folder in ('TABLE', 'VIEW', 'PACKAGE', 'PROCEDURE', 'FUNCTION', 'TYPE', 'TRIGGER', 'SEQUENCE', 'SYNONYM'):
		source_dir = os.path.join(from_db_dir, folder)
		target_dir = os.path.join(to_db_dir, folder)

		if not os.path.exists(source_dir): continue
		if not os.path.exists(target_dir): os.mkdir(target_dir)

		for file in os.listdir(source_dir):
			logging.debug('Copying %s' % os.path.join(source_dir, file))
			shutil.copyfile(os.path.join(source_dir, file), os.path.join(target_dir, file))

	logging.info('Finish copying db raw files (XML).')


def _generate_tables(source_db_dir, target_db_dir):
	"""
	Generate table SQL files by parsing the table XML files
	"""

	logging.info('Start generating table SQL file...')

	src_table_folder = os.path.join(source_db_dir, 'TABLE')
	target_table_folder = os.path.join(target_db_dir, 'TABLE')
	target_init_table_folder = os.path.join(target_db_dir, 'INIT_TABLE')

	db_objects_dat_file = os.path.join(target_init_table_folder, 'DB_OBJECTS.DAT')
	db_table_columns_dat_file = os.path.join(target_init_table_folder, 'DB_TABLE_COLUMNS.DAT')

	db_objects = None
	db_table_columns = None

	try:
		db_objects = open(db_objects_dat_file, 'a')
		db_table_columns = open(db_table_columns_dat_file, 'a')

		table_db_objects = xmlparser.parse_table(os.path.join(src_table_folder, 'DB_OBJECTS.XML'))
		table_db_table_columns = xmlparser.parse_table(os.path.join(src_table_folder, 'DB_TABLE_COLUMNS.XML'))
		dbmeta.set_db_objects_table(table_db_objects)
		dbmeta.set_db_table_columns_table(table_db_table_columns)
		with open(os.path.join(target_init_table_folder, 'DB_OBJECTS.CTL'), 'w') as t:
			t.write(table_db_objects.table_ctl_file())
		with open(os.path.join(target_init_table_folder, 'DB_TABLE_COLUMNS.CTL'), 'w') as t:
			t.write(table_db_table_columns.table_ctl_file())

		table_db_objects_upgrade = xmlparser.parse_table(os.path.join(src_table_folder, 'DB_OBJECTS_UPGRADE.XML'))
		table_db_table_columns_upgrade = xmlparser.parse_table(os.path.join(src_table_folder, 'DB_TABLE_COLUMNS_UPGRADE.XML'))
		with open(os.path.join(target_init_table_folder, 'DB_OBJECTS_UPGRADE.CTL'), 'w') as t:
			t.write(table_db_objects_upgrade.table_ctl_file())
		with open(os.path.join(target_init_table_folder, 'DB_TABLE_COLUMNS_UPGRADE.CTL'), 'w') as t:
			t.write(table_db_table_columns_upgrade.table_ctl_file())


		for file in os.listdir(src_table_folder):
			if not file.upper().endswith('.XML'): continue

			table = xmlparser.parse_table(os.path.join(src_table_folder, file), _enable_snapshot)
			table_sql = os.path.join(target_table_folder, table.name + '.SQL')
			#table_ctl = os.path.join(tgt_init_table_folder, table.name + '.CTL')

			with open(table_sql, 'w') as t: t.write(table.table_ddl())

			db_table_columns.write(table.table_column_metadata())
			db_objects.write(table.table_metadata())

			if table.indexes:
				table_idx_sql = os.path.join(target_table_folder, table.name + '.IDX.SQL')
				with open(table_idx_sql, 'w') as t: t.write(table.index_ddl())
				db_objects.write(table.table_index_metadata())
	finally:
		db_objects and db_objects.close()
		db_table_columns and db_table_columns.close()

	logging.info('Finish generating table SQL file.')


def _process_plsql_object(source_db_dir, target_db_dir):
	"""
	Process PLSQL object by processing xml files to get the metatdata stored in db_objects
	"""

	logging.info('Start processing plsql object...')

	src_table_folder = os.path.join(source_db_dir, 'TABLE')
	target_init_table_folder = os.path.join(target_db_dir, 'INIT_TABLE')

	db_objects_dat_file = os.path.join(target_init_table_folder, 'DB_OBJECTS.DAT')
	db_objects = None

	try:
		db_objects = open(db_objects_dat_file, 'a')
		table_db_objects = xmlparser.parse_table(os.path.join(src_table_folder, 'DB_OBJECTS.XML'))
		dbmeta.set_db_objects_table(table_db_objects)

		for object in ('PACKAGE', 'PROCEDURE', 'FUNCTION', 'TYPE', 'TRIGGER', 'SEQUENCE'):
			src_object_folder = os.path.join(source_db_dir, object)
			tgt_object_folder = os.path.join(target_db_dir, object)

			for file in os.listdir(src_object_folder):
				if not file.upper().endswith('.XML'): continue

				obj = xmlparser.parse_plsql(os.path.join(src_object_folder, file))
				db_objects.write(obj.metadata())

				if obj.object_type == 'PACKAGE':
					obj_file = file.replace('XML', 'PKS')
					shutil.copyfile(os.path.join(src_object_folder, obj_file), os.path.join(tgt_object_folder, obj_file))
					obj_file = file.replace('XML', 'PKB')
					shutil.copyfile(os.path.join(src_object_folder, obj_file), os.path.join(tgt_object_folder, obj_file))
				else:
					obj_file = file.replace('XML', 'SQL')
					shutil.copyfile(os.path.join(src_object_folder, obj_file), os.path.join(tgt_object_folder, obj_file))

	finally:
		db_objects and db_objects.close()

	logging.info('Finish processing plsql object.')

def _clone_db_metadata(target_dir):
	"""
	Copy DAT file for DB_OBJECTS_UPGRADE and DB_TABLE_COLUMNS_UPGRADE
	"""

	logging.info('Start cloning db metatdata...')

	init_table_folder = os.path.join(target_dir, 'INIT_TABLE')
	shutil.copyfile(os.path.join(init_table_folder, 'DB_OBJECTS.DAT'), os.path.join(init_table_folder, 'DB_OBJECTS_UPGRADE.DAT'))
	shutil.copyfile(os.path.join(init_table_folder, 'DB_TABLE_COLUMNS.DAT'), os.path.join(init_table_folder, 'DB_TABLE_COLUMNS_UPGRADE.DAT'))

	logging.info('Finish cloning db metadata.')

def _generate_db_tgz(target_dir):
	import tarfile
	logging.info('Start generating db zip package...')

	os.chdir(target_dir)
	with tarfile.open('DB.tgz', 'w|gz') as tar:
		tar.add('DB')

	logging.info('Finish generating db zip package.')

def _generate_release_file(target_dir, release_number):
	"""
	Generate file RELEASE.TXT
	"""
	with open(os.path.join(target_dir, 'RELEASE.TXT'), 'w') as f:
		f.write(release_number)

def _remove_db_staging_folder(target_dir):
	for _ in ('DB', 'DB_STAGING'):
		folder = os.path.join(target_dir, _)
		if os.path.exists(folder):
			shutil.rmtree(folder, ignore_errors=False)

def compile_db(common_db_dir, source_db_dir, target_dir, release_number):
	logging.info('------------ B E G I N ------------')

	_create_db_package_structure(target_dir, 'DB', True)
	_create_db_package_structure(target_dir, 'DB_STAGING', True)

	target_db_dir = os.path.join(target_dir, 'DB')
	staging_db_dir = os.path.join(target_dir, 'DB_STAGING')

	_copy_db_raw_files(common_db_dir, staging_db_dir)
	_copy_db_raw_files(source_db_dir, staging_db_dir)

	_generate_tables(staging_db_dir, target_db_dir)
	_process_plsql_object(staging_db_dir, target_db_dir)
	_clone_db_metadata(target_db_dir)
	_generate_install_script(target_db_dir, release_number)
	_copy_template_files(common_db_dir, target_db_dir)
	_generate_release_file(target_db_dir, release_number)
	_generate_db_tgz(target_dir)
	_remove_db_staging_folder(target_dir)

	logging.info('------------ E N D ------------')


