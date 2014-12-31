__author__ = 'yufa'

import logging
import dbmeta
from column import Column, col_snapshot
from index import Index
from ezdb.common.constants import const
from ezdb.common.exception import EzDBError


def _is_true(value):
	if str(value).upper() in const.TRUTH_VALUE:
		return True
	else:
		return False


class Table(object):
	"""
	Table class, model the table object created from SaveDB xml files.

	>>> table = Table()
	>>> column = Column()
	>>> column.name = 'id'
	>>> column.data_type = 'number'
	>>> table.name = 'LO_TEST_TABLE'
	>>> table.story
	'US138139'
	>>> table.add_column(column)
	>>> print table.table_ddl()
	CREATE TABLE "LO_TEST_TABLE" (
	"ID" NUMBER
	);

	>>> table.init_on_install='N'
	>>> print table.table_ctl_file()
	None

	>>> table.table_metadata()
	>>> table.table_column_metadata()

	"""

	def __init__(self, enable_snapshot=False):
		self.__name = None
		self.__documentation = ''
		self.__story = const.DEFAULT_STORY_NUMBER
		self.__products_formula = const.DEFAULT_PRODUCT_CODE
		self.__release = const.DEFAULT_RELEASE_NUMBER
		self.__type = const.DEFAULT_TABLE_TYPE
		self.__logging = 'N'
		self.__init_on_install = 'N'
		self.__init_on_upgrade = 'N'
		self.__init_on_demand = 'N'
		self.__standard_or_custom = 'S'
		self.__init_trans = 1
		self.__columns = {}
		self.__indexes = {}
		self.__enable_snapshot = enable_snapshot


	@property
	def name(self):
		if self.__name:
			return self.__name
		else:
			raise EzDBError('Table name is not set!')

	@name.setter
	def name(self, value):
		if len(value) > 30:
			raise EzDBError('Table name length can not exceed 30!')
		self.__name = value.upper()

	@property
	def documentation(self):
		return self.__documentation

	@documentation.setter
	def documentation(self, value):
		self.__documentation = value or ''

	@property
	def story(self):
		return self.__story

	@story.setter
	def story(self, value):
		self.__story = value.upper() if value else const.DEFAULT_STORY_NUMBER

	@property
	def products_formula(self):
		return self.__products_formula

	@products_formula.setter
	def products_formula(self, value):
		self.__products_formula = value or const.DEFAULT_PRODUCT_CODE

	@property
	def release(self):
		return self.__release

	@release.setter
	def release(self, value):
		self.__release = value or const.DEFAULT_RELEASE_NUMBER

	@property
	def type(self):
		return self.__type

	@type.setter
	def type(self, value):
		self.__type = value.upper() if value else const.DEFAULT_TABLE_TYPE

	@property
	def standard_or_custom(self):
		return self.__standard_or_custom

	@standard_or_custom.setter
	def standard_or_custom(self, value):
		if value.upper() in ('S','STANDARD'):
			self.__standard_or_custom = 'S'
		else:
			self.__standard_or_custom = 'C'

	@property
	def logging(self):
		return self.__logging

	@logging.setter
	def logging(self, value):
		self.__logging = 'Y' if _is_true(value) else 'N'

	@property
	def init_trans(self):
		return self.__init_trans

	@init_trans.setter
	def init_trans(self, value):
		self.__init_trans = value or ''

	@property
	def init_on_install(self):
		return self.__init_on_install

	@init_on_install.setter
	def init_on_install(self, value):
		self.__init_on_install = 'Y' if _is_true(value) else 'N'

	@property
	def init_on_upgrade(self):
		return self.__init_on_upgrade

	@init_on_upgrade.setter
	def init_on_upgrade(self, value):
		self.__init_on_upgrade = 'Y' if _is_true(value) else 'N'

	@property
	def init_on_demand(self):
		return self.__init_on_demand

	@init_on_demand.setter
	def init_on_demand(self, value):
		self.__init_on_demand = 'Y' if _is_true(value) else 'N'

	@property
	def columns(self):
		return self.__columns

	def add_column(self, column):
		if isinstance(column, Column):
			self.__columns[column.name] = column

	@property
	def indexes(self):
		return self.__indexes

	def add_index(self, index):
		if not isinstance(index, Index): return

		try:
			_ = index.name
		except EzDBError:
			# if index name is not explicitly set
			index.update_name(self.name, len(self.indexes))
			logging.warning('Table %s has index not specified in the xml file, generate it automatically - %s.' %
			                (self.name, index.name))

		index.table_name = self.name
		index.enable_snapshot = self.__enable_snapshot

		self.__indexes[index.name] = index

	def sorted_columns(self):
		"""
		Return the columns in the sequence of their creation. i.e. when the column is added to the table.
		SNAPSHOT column will be the first column if snapshot function is enabled.
		"""

		columns = []
		if self.name not in const.DICTIONARY_OBJECTS and self.__enable_snapshot:
			columns.append(col_snapshot())

		temp = [column for column in self.__columns.values() if not column.name == const.COLUMN_SNAPSHOT_ID]
		temp.sort(key=lambda item:item.order)
		columns.extend(temp)

		return columns

	def table_ddl(self):
		"""
		Return the table creation SQL statement.
		"""

		ddl = ['CREATE TABLE "{0}" ('.format(self.name)]
		ddl.extend([column.column_ddl() for column in self.sorted_columns()])
		ddl[-1] = ddl[-1].rstrip(',')
		ddl.append(')')
		ddl.append('ENABLE ROW MOVEMENT TABLESPACE &1;')

		ddl_stmt = '\n'.join(ddl)

		logging.debug('Table [%s]: - SQL:\n%s' % (self.name, ddl_stmt))
		return ddl_stmt

	def index_ddl(self):
		"""
		Return all the index creation statements for the table.
		"""

		ddl = [index.index_ddl() for index in self.indexes.values()]
		ddl_stmt = '\n'.join(ddl)

		logging.debug('Table [%s] - Indexes:\n%s' % (self.name, ddl_stmt))
		return ddl_stmt

	def update(self, mapping):
		for key, value in mapping.items():
			if key in self.__class__.__dict__ and \
					isinstance(self.__class__.__dict__[key], property):
				self.__setattr__(key, value)

	def table_metadata(self):
		"""
		Return the table metadata to be stored in the table DB_OBJECTS
		"""
		metadata = dbmeta.db_objects_metadata(
			table_name = self.name,
			table_type = self.type,
			object_type = 'TABLE',
			standard_custom = self.standard_or_custom,
			description = self.documentation,
			release = self.release,
			relevant_for = self.products_formula,
			story_id = self.story,
			init_on_install = self.init_on_install,
			init_on_upgrade = self.init_on_upgrade,
			init_on_demand = self.init_on_demand,
			ini_trans = self.init_trans,
			logging = self.logging
		)

		logging.debug('Table [%s] metadata in table DB_OBJECTS:\n%s' % (self.name, metadata))
		return metadata

	def table_column_metadata(self):
		"""
		Return the table's columns metadata data to be stored in the table DB_TABLE_COLUMNS.
		"""

		metadata = dbmeta.db_table_columns_metadata(self.name, self.sorted_columns())
		logging.debug('Table [%s] metadata in table DB_TABLE_COLUMNS:\n%s' % (self.name, metadata))
		return metadata

	def table_index_metadata(self):
		"""
		Return the table's index metadata to be stored in the table DB_OBJECTS.
		"""

		metadata = ''.join(
			[dbmeta.db_objects_metadata(
				table_name=index.name,
				table_type=index.type,
			    hist_table_name=self.name,
			    parameter = index.columns,
				object_type='INDEX',
				standard_custom=self.standard_or_custom,
				release=index.release,
				relevant_for=self.products_formula,
				story_id=index.story) for index in self.indexes.values()]
		)

		logging.debug("Table [%s]'s index metadata in table DB_TABLE_COLUMNS:\n%s" % (self.name, metadata))
		return metadata

	def table_ctl_file(self):
		"""
		Return the table control file to be used in sql*loader
		"""

		if not (self.init_on_install == 'Y' or self.init_on_upgrade == 'Y'): return

		use_direct = 'TRUE'
		for column in self.__columns.values():
			if column.data_type in ('CLOB', 'BLOB', 'LONG'):
				use_direct = 'FALSE'
				break

		ctl_header = ('OPTIONS (SILENT=(HEADER, FEEDBACK), DIRECT={is_direct})\n'
		              'LOAD DATA\n'
		              'CHARACTERSET UTF8\n'
		              'LENGTH SEMANTICS CHAR\n'
		              'BYTEORDERMARK CHECK\n'
		              r'''INFILE '{table_name}.DAT' "STR '#$EOR$#\r\n'"'''
		              '\nAPPEND\n'
		              'INTO TABLE {table_name}\n'
		              'FIELDS TERMINATED BY \',\' OPTIONALLY ENCLOSED BY \'"\' AND \'"\'\n'
		              'TRAILING NULLCOLS\n'
		              '(\n').format(is_direct=use_direct, table_name=self.name)

		column_ctrls = [column.column_ctl_str() for column in self.sorted_columns()]
		column_ctrls[0] = column_ctrls[0].strip(',')
		column_ctrls.append(')')
		ctl_source = '%s%s' % (ctl_header, '\n'.join(column_ctrls))

		logging.debug("Table [%s]'s control file:\n%s" % (self.name, ctl_source))
		return ctl_source

	def table_dat_file(self):
		raise NotImplementedError('Not implemented.')

	def checksum(self):
		raise NotImplementedError('Not implemented.')



if __name__ == '__main__':
	import doctest
	doctest.testmod()

	#column = Column()
	#column.name = 'id'
	#column.data_type = 'number'
	#print column.order
	#
	#column2 = Column()
	#column2.name = 'name2'
	#column2.data_type = 'varchar2(10)'
	#print column2.order
	#
	#table = Table()
	#table.name = 'Test'
	#table.add_column(column)
	#table.add_column(column2)
	#print table.table_metadata()
	#
	#print Table.__dict__['init_on_install'].__class__
