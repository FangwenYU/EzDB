__author__ = 'yufa'

import logging

from ezdb.common.exception import EzDBError
from table import Table



# Table DB_OBJECTS
_global_db_objects_table = None
# Table DB_TABLE_COLUMNS
_global_db_table_columns_table = None

_global_db_objects_meta_template = None
_global_db_table_columns_meta_template = None

def _set_dict_table(table, table_name):
	logging.info('Initializing table {0}.'.format(table_name))

	if not isinstance(table, Table):
		msg = 'The given object is not a valid Table object!'
		logging.error(msg)
		raise EzDBError(msg)

	if table_name == table.name == 'DB_OBJECTS':
		global _global_db_objects_table
		_global_db_objects_table = table
	elif table_name == table.name == 'DB_TABLE_COLUMNS':
		global _global_db_table_columns_table
		_global_db_table_columns_table = table
	else:
		msg = 'Failed to initialize table {0}, as the given table is not {1}!'.format(table_name, table_name)
		logging.error(msg)
		raise EzDBError(msg)

	logging.info('Finish initializing table {0}.'.format(table_name))

def set_db_objects_table(table):
	_set_dict_table(table, 'DB_OBJECTS')

def set_db_table_columns_table(table):
	_set_dict_table(table, 'DB_TABLE_COLUMNS')

def _table_metadata_template(table):
	meta_template = ['"{%s}"' % item.name.lower() for item in table.sorted_columns()]
	return ','.join(meta_template) + '#$EOR$#\n'

def _db_objects_meta_template():
	global _global_db_objects_meta_template
	if not _global_db_objects_meta_template:
		_global_db_objects_meta_template = _table_metadata_template(_global_db_objects_table)
	return _global_db_objects_meta_template

def _db_table_columns_meta_template():
	global _global_db_table_columns_meta_template
	if not _global_db_table_columns_meta_template:
		_global_db_table_columns_meta_template = _table_metadata_template(_global_db_table_columns_table)
	return _global_db_table_columns_meta_template

def _escape_character(params):
	for k, v in params.iteritems():
			if isinstance(v, str):
				v = v.replace('"', '""') #escape quota(") used in sql*loader
				#v = v.strip("'") # Remove the single quota(') (maybe set by default value) to be used in sql*loader
				params[k] = v
	return params

def _escape_default_value(value):
	# Remove the single quota(')
	# For example, if one table column is VARCHAR2(1) and the default value is set to 'Y'.
	# But using the sql*loader, it should be set to "Y", not "'Y'", otherwise, it will exceed the column length constraint
	return value.strip("'")


def db_table_columns_metadata(table_name, sorted_columns):
	"""
	All the table columns' metadata will be saved in db dict table - DB_TABLE_COLUMNS, and this kind data
	will be generated in the format of a sql*loader DAT file.
	This method is used to generate metadata for each table column in the format of DAT file
	"""

	if not _global_db_table_columns_table:
		raise EzDBError('Table DB_TABLE_COLUMNS is not created!')

	table_column = []
	for idx, column in enumerate(sorted_columns):
		col_dict = column.as_dict()
		col_dict['table_name'] = table_name
		col_dict['column_id'] = idx + 1

		params = {}
		for k, v in _global_db_table_columns_table.columns.iteritems():
			k = k.lower()
			if k not in col_dict:
				params[k] = _escape_default_value(v.default_value)
		params.update(col_dict)
		params = _escape_character(params)
		table_column.append(_db_table_columns_meta_template().format(**params))
	return ''.join(table_column)

def db_objects_metadata(**kwargs):
	"""
	All the db objects' metadata will be saved in db dict table - DB_OBJECTS, and this kind data
	will be generated in the format of a sql*loader DAT file.
	This method is used to generate metadata for each object in the format of DAT file
	"""

	if not _global_db_objects_table:
		raise EzDBError('Table DB_OBJECTS is not created!')

	params = {}
	for k, v in _global_db_objects_table.columns.iteritems():
		k = k.lower()
		if k not in kwargs:
			params[k] = _escape_default_value(v.default_value)
	params.update(kwargs)
	params = _escape_character(params)

	return _db_objects_meta_template().format(**params)

