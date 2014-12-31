__author__ = 'yufa'


def _create_table_piece(table_name):
	piece = ['set feed on heading on timing on term on',
	         'prompt "&DB_DIR/TABLE/{table_name}.SQL" &TBS_DATA',
	         '@"&DB_DIR/TABLE/{table_name}.SQL" &TBS_DATA',
	         '\n']
	return '\n'.join(piece).format(table_name=table_name)


def _create_index_piece(table_name):
	piece = ['set feed on heading on timing on term on',
	         'prompt "&DB_DIR/TABLE/{table_name}.IDX.SQL" &TBS_INDEX',
	         '@"&DB_DIR/TABLE/{table_name}.IDX.SQL" &TBS_INDEX',
	         '\n']
	return '\n'.join(piece).format(table_name=table_name)


def _create_sqlldr_piece(table_name):
	piece = ['set feed on heading on timing on term on']
	piece.append('prompt Loading {table_name} with SQL*Loader...')
	piece.append("exec EXEC_IMMEDIATE('alter table {table_name} disable all triggers');")
	piece.append('prompt host "&SQLLDR_SCRIPT" {table_name} "&NEW_CENTRAL_CONNECTION" '
	             '"&DB_DIR/INIT_TABLE/{table_name}.DAT" "&DB_DIR/INIT_TABLE/{table_name}.CTL" '
	             '"&OUTPUT_DIR"')
	piece.append('host "&SQLLDR_SCRIPT" {table_name} "&NEW_CENTRAL_CONNECTION" "&DB_DIR/INIT_TABLE/{table_name}.DAT" '
	             '"&DB_DIR/INIT_TABLE/{table_name}.CTL" "&OUTPUT_DIR"')
	piece.append('prompt "&OUTPUT_DIR/LOAD_SQLLDR.RC"')
	piece.append('@"&OUTPUT_DIR/LOAD_SQLLDR.RC"')
	piece.append("exec EXEC_IMMEDIATE('alter table {table_name} enable all triggers');")
	piece.append('\n')

	return '\n'.join(piece).format(table_name=table_name)


def _create_object_piece(object_type, object_name, file_format='SQL'):
	'''
	Object type: TYPE, SEQUENCE, PROCEDURE, FUNCTION, PACKAGE
	'''
	return ('prompt "&DB_DIR/{object_type}/{object_name}.{file_format}"\n'
	        '@"&DB_DIR/{object_type}/{object_name}.{file_format}"\n'
	).format(object_type=object_type, object_name=object_name, file_format=file_format)


def _create_section(section_name):
	return ('-- -------------------------------------------------------------------------------------\n'
	        '-- CREATE {section_name} \n'
	        '-- -------------------------------------------------------------------------------------\n'
	        'prompt --- CREATE {section_name} \n'
	        'set echo off timing off \n').format(section_name=section_name)


def _update_release_number(release_number):
	insert_stmt = "insert into application(product, release_date, release_number)values('{product}', sysdate, '{release}');"

	return '\n'.join([insert_stmt.format(product='Z', release=release_number),
	                  insert_stmt.format(product='W', release=release_number),
	                  'commit;\n'])

def generate_ifs_model_script(db_dir, release_number):
	import time
	import os

	yield '--This script was generated on %s. \n' % time.ctime()

	yield '\n'.join(
		['alter session set NLS_DATE_LANGUAGE=\'AMERICAN\';',
		 'alter session set NLS_NUMERIC_CHARACTERS=\'.,\';',
		 'alter session set NLS_LENGTH_SEMANTICS=&SEMANTIC;',
		 'alter user &CENTRAL_NAME default role none;',
		 'begin',
		 " IF USER <> '&CENTRAL_NAME' THEN",
		 "   RAISE_APPLICATION_ERROR(-20000,'This script must be run when connected as &CENTRAL_NAME');",
		 " END IF;",
		 'end;',
		 '/',
		 'set serveroutput on size unlimited \n'])

	yield _create_section('TYPE')
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'TYPE'))):
		yield _create_object_piece('TYPE', file_name.split('.')[0])

	yield _create_section('TABLE')
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'TABLE'))):
		if not file_name.endswith('.IDX.SQL'):
			yield _create_table_piece(file_name.split('.')[0])

	yield _create_section('SEQUENCE')
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'SEQUENCE'))):
		yield _create_object_piece('SEQUENCE', file_name.split('.')[0])

	yield _create_section('FUNCTION')
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'FUNCTION'))):
		yield _create_object_piece('FUNCTION', file_name.split('.')[0])

	yield _create_section('PROCEDURE')
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'PROCEDURE'))):
		yield _create_object_piece('PROCEDURE', file_name.split('.')[0])

	yield _create_section('PACKAGE_HEADER')
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'PACKAGE'))):
		if file_name.endswith('.PKS'):
			yield _create_object_piece('PACKAGE', file_name.split('.')[0], 'PKS')

	yield _create_section('VIEW')
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'VIEW'))):
		yield _create_object_piece('VIEW', file_name.split('.')[0])

	yield _create_section('PACKAGE_BODY')
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'PACKAGE'))):
		if file_name.endswith('.PKB'):
			yield _create_object_piece('PACKAGE', file_name.split('.')[0], 'PKB')

	yield _create_section('INIT DATA using SQL Loader')
	yield 'DEFINE SQLLDR_SCRIPT="&DB_DIR/TOOLS/COMMON/LOAD_SQLLDR.BAT" \n'
	yield 'prompt SQLLDR_SCRIPT=&SQLLDR_SCRIPT \n'
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'INIT_TABLE'))):
		if file_name.endswith('.DAT'):
			yield _create_sqlldr_piece(file_name.split('.')[0])

	yield _create_section('Load application release table')
	yield _update_release_number(release_number)

	yield _create_section('INDEXES')
	for file_name in sorted(os.listdir(os.path.join(db_dir, 'TABLE'))):
		if file_name.endswith('.IDX.SQL'):
			yield _create_index_piece(file_name.split('.')[0])

	yield '-- -------------------------------------------------------------------------------------\n'
	yield '-- Show errors\n'
	yield '-- -------------------------------------------------------------------------------------\n'
	yield 'select * from user_errors;\n'
	yield ("select 'ORA-20000: [' ||  object_type ||  ' -  ' || table_name || '] is not succesfully installed.' error_msg "
	       "from db_objects where table_name not in (select object_name from user_objects);\n")


if __name__ == '__main__':
	for line in generate_ifs_model_script(r'C:\Users\yufa\Desktop\Document\Study\Python\EzDB\Output\DB'):
		print line