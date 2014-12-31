__author__ = 'yufa'

import logging
from ezdb.common.exception import EzDBError
from ezdb.common.constants import const


class Column(object):
	"""
	Column class, used in Table.

	>>> column = Column()
	>>> column.name
	Traceback (most recent call last):
	...
	EzDBError: Column name is not set!

	>>> column = Column()
	>>> column.name = 'id'
	>>> column['name']
	'ID'
	>>> column['data_type'] = 'number'
	>>> column.data_type
	'NUMBER'
	>>> column['not_exit'] = 'not_exist'
	>>> column.data_type = 'number'
	>>> column.nullable = 'True'
	>>> column.default_value = 1
	>>> column.column_ddl()
	'"ID" NUMBER DEFAULT 1,'

	>>> d = {'name': 'code'}
	>>> column.update(d)
	>>> column.column_ddl()
	'"CODE" NUMBER DEFAULT 1,'

	"""


	_order = 0

	def __init__(self, name=None, data_type=None, nullable='Y', default_value=None,
	             documentation=None, story=None, release=None, products='W',
	             sql_loader_ctl_expression=None, deprecated_release=None, sequence_name=None):

		self.__attrs = {}

		if name:
			self.name = name
		else:
			self.__name = None

		if data_type:
			self.data_type = data_type
		else:
			self.__data_type = None

		self.nullable = nullable
		self.default_value = default_value
		self.documentation = documentation
		self.story = story
		self.release = release
		self.products = products
		self.sql_loader_ctl_expression = sql_loader_ctl_expression
		self.deprecated_release = deprecated_release
		self.sequence_name = sequence_name

		self.__order = Column._order

		Column._order += 1


	@property
	def order(self):
		return self.__order

	@property
	def name(self):
		if self.__name:
			return self.__name
		else:
			raise EzDBError('Column name is not set!')

	@name.setter
	def name(self, value):
		if len(value) > 30:
			raise EzDBError('Column name length can not exceed 30!')
		self.__name = self.__attrs['column_name'] = value.upper()

	@property
	def data_type(self):
		if self.__data_type:
			return self.__data_type
		else:
			raise EzDBError('Column data type is not set!')

	@data_type.setter
	def data_type(self, value):
		if not value:
			raise EzDBError('Column data type cannot be None!')
		self.__data_type = self.__attrs['data_type'] = value.upper()

	@property
	def nullable(self):
		return self.__nullable

	@nullable.setter
	def nullable(self, value):
		if str(value).upper() in const.TRUTH_VALUE:
			self.__nullable = 'Y'
		else:
			self.__nullable = 'N'

		self.__attrs['nullable'] = self.__nullable

	@property
	def documentation(self):
		return self.__documentation

	@documentation.setter
	def documentation(self, value):
		self.__documentation = self.__attrs['column_desc'] = value or ''

	@property
	def default_value(self):
		return self.__default_value

	@default_value.setter
	def default_value(self, value):
		self.__attrs['default_value'] = self.__default_value = value or ''

	@property
	def story(self):
		return self.__story

	@story.setter
	def story(self, value):
		self.__story = self.__attrs['story_id'] = value.upper() if value else const.DEFAULT_STORY_NUMBER

	@property
	def products(self):
		return self.__products

	@products.setter
	def products(self, value):
		self.__products = self.__attrs['products'] = value or const.DEFAULT_PRODUCT_CODE

	@property
	def release(self):
		return self.__release

	@release.setter
	def release(self, value):
		self.__release = self.__attrs['release'] = value or const.DEFAULT_RELEASE_NUMBER

	@property
	def sql_loader_ctl_expression(self):
		return self.__sql_loader_ctl_expression

	@sql_loader_ctl_expression.setter
	def sql_loader_ctl_expression(self, value):
		self.__sql_loader_ctl_expression = value

	@property
	def deprecated_release(self):
		return self.__deprecated_release

	@deprecated_release.setter
	def deprecated_release(self, value):
		self.__deprecated_release = self.__attrs['deprecated_release'] = value or ''

	@property
	def sequence_name(self):
		return self.__sequence_name

	@sequence_name.setter
	def sequence_name(self, value):
		self.__sequence_name = self.__attrs['sequence_name'] = value or ''

	def __eq__(self, other):
		if isinstance(other, Column):
			return self.name == other.name
		else:
			return False

	def __getitem__(self, item):
		if item in self.__class__.__dict__ and \
				isinstance(self.__class__.__dict__[item], property):
			return getattr(self, item)

	def __setitem__(self, item, value):
		if item in self.__class__.__dict__ and \
				isinstance(self.__class__.__dict__[item], property):
			setattr(self, item, value)


	def as_dict(self):
		return self.__attrs
		#a = {(k, getattr(self, k)) for k, v in self.__class__.__dict__.iteritems() \
		#     if isinstance(v, property) and not k == 'sql_loader_ctl_expression'}
		#return a


	def column_ddl(self):
		l = [self.name, self.data_type]
		if self.default_value:
			l.append('DEFAULT %s' % self.default_value)
		if self.nullable == 'N':
			l.append('NOT NULL')
		if len(l) == 2: return '"{0}" {1},'.format(*l)
		if len(l) == 3: return '"{0}" {1} {2},'.format(*l)
		if len(l) == 4: return '"{0}" {1} {2} {3},'.format(*l)

	def __str__(self):
		return '[name: %s, data_type: %s]' % (self.name, self.data_type)

	def update(self, mapping):
		for key, value in mapping.items():
			if key in self.__class__.__dict__ and \
					isinstance(self.__class__.__dict__[key], property):
				self.__setattr__(key, value)

	def column_ctl_str(self):
		"""
		Return the string used in the table sql*loader control file

		For example:
		name varchar2(20)  ->  ,NAME CHAR(20) "TO_CHAR(:NAME)"

		>>> column = Column()
		>>> column.name = 'name'
		>>> column.data_type = 'varchar2(20)'
		>>> column.column_ctl_str()
		',NAME CHAR(20) "TO_CHAR(:NAME)"'

		>>> column.data_type = 'varchar2(4000)'
		>>> column.column_ctl_str()
		',NAME CHAR(4000) "TO_CHAR(SUBSTR(:NAME,1,2000))||TO_CHAR(SUBSTR(:NAME,2001))"'

		"""

		import re

		if self.sql_loader_ctl_expression:
			return ',{0} {1}'.format(self.name, self.sql_loader_ctl_expression)

		char_pattern = re.compile(r'(CHAR|VARCHAR|VARCHAR2|NVARCHAR|NVARCHAR2)\s*\(\s*(?P<size>\d+)\s*\)')
		result = char_pattern.match(self.data_type)
		if result:
			len = result.group('size')
			if int(len) > 2000:
				return ',{0} CHAR({1}) "TO_CHAR(SUBSTR(:{2},1,2000))||TO_CHAR(SUBSTR(:{3},2001))"'.format(
					self.name, len, self.name, self.name)
			else:
				return ',{0} CHAR({1}) "TO_CHAR(:{2})"'.format(self.name, len, self.name)

		number_pattern = re.compile(r'(NUMBER|INTEGER|DECIMAL|FLOAT)')
		result = number_pattern.match(self.data_type)
		if result: return ',{0} "TO_NUMBER(:{1})"'.format(self.name, self.name)

		if self.data_type == 'DATE':
			return ',{0} DATE "YYYY-MM-DD HH24:MI:SS"'.format(self.name)

		if self.data_type.startswith('TIMESTAMP'):
			return ',{0} TIMESTAMP "YYYY-MM-DD HH24:MI:SS:FF3"'.format(self.name)

		if self.data_type in ('CLOB', 'LONG', 'XMLTYPE'):
			return ", {0}# FILTER CHAR\n,{1} CHAR(1048576) ENCLOSED BY '<start_lob>' AND '<end_lob>' NULLIF {2}#='Y'".format(
				self.name[0:29], self.name, self.name[0:29]
			)

		if self.data_type in ('ROWID', 'UROWID'):
			return ',{0} CHAR(30) "TO_CHAR(:1)"'.format(self.name, self.name)

		raw_pattern = re.compile(r'RAW\s*\(\s*(?P<size>\d+)\s*\)')
		result = raw_pattern.match(self.data_type)
		if result:
			return ',{0} "HEXTORAW(:{1})"'.format(self.name, self.name)

		msg = 'Unknown column data type: %s' % str(self)
		logging.error(msg)
		raise EzDBError(msg)


_snapshot_id_column = None
def col_snapshot():
	"""
	Return the column SNAPSHOT_ID used in snapshot database.

	>>> column = col_snapshot()
	>>> column.name
	'SNAPSHOT_ID'
	"""

	global _snapshot_id_column

	if _snapshot_id_column and isinstance(_snapshot_id_column, Column):
		return _snapshot_id_column
	else:
		snapshot_id = Column()
		snapshot_id.name = const.COLUMN_SNAPSHOT_ID
		snapshot_id.data_type = 'NUMBER'
		snapshot_id.nullable = 'FALSE'
		snapshot_id.story = 'US138139'
		snapshot_id.release = 'RO4.0'
		snapshot_id.products = 'W'
		snapshot_id.documentation = 'Snapshot id, used to identify which snapshot the data was created from.'
		_snapshot_id_column = snapshot_id
		return _snapshot_id_column


if __name__ == '__main__':
	import doctest
	doctest.testmod()