__author__ = 'yufa'

from ezdb.common.exception import EzDBError
from ezdb.common.constants import const


class Index(object):
	"""
	Index class. Used in Table to model indexes created on the table.

	>>> index = Index()
	>>> index.name = 'PK_LO_TEST'
	>>> index.type = 'PRIMARY'
	>>> index.index_ddl(table_name='LO_TEST')
	''
	>>> index.columns='name'
	>>> index.index_ddl(table_name='LO_TEST', enable_snapshot=True)
	'ALTER TABLE LO_TEST ADD CONSTRAINT PK_LO_TEST PRIMARY KEY(SNAPSHOT_ID,name);'

	"""

	def __init__(self, name=None, table_name=None, type=None, story=None, release=None, columns=None, enable_snapshot=False):
		if name:
			self.name = name
		else:
			self.__name = None

		if type:
			self.type = type
		else:
			self.__type = 'NON-UNIQUE'

		if columns:
			self.columns = columns
		else:
			self.__columns = None

		if table_name:
			self.table_name = table_name
		else:
			self.__table_name = None

		self.story = story
		self.release = release
		self.enable_snapshot = enable_snapshot

	@property
	def name(self):
		if not self.__name:
			raise EzDBError('Index name is not set')
		return self.__name

	@name.setter
	def name(self, value):
		if not value:
			raise EzDBError('Index name cannot be None.')
		if len(value) > 30:
			raise EzDBError('Index name cannot exceed 30 bytes.')
		self.__name = value.upper()

	@property
	def type(self):
		if not self.__type:
			raise EzDBError('Index type is not set.')
		return self.__type

	@type.setter
	def type(self, value):
		if not value:
			raise EzDBError('Index type cannot be None.')
		if not value.upper() in ('PRIMARY', 'UNIQUE', 'NON-UNIQUE'):
			raise EzDBError('Index type can only be "PRIMARY", "UNIQUE" and "NON-UNIQUE".')
		self.__type = value.upper()

	@property
	def story(self):
		return self.__story

	@story.setter
	def story(self, value):
		self.__story = value.upper() if value else const.DEFAULT_STORY_NUMBER

	@property
	def release(self):
		return self.__release

	@release.setter
	def release(self, value):
		self.__release = value if value else const.DEFAULT_RELEASE_NUMBER

	@property
	def columns(self):
		if self.type == 'PRIMARY' and self.enable_snapshot \
			and not const.COLUMN_SNAPSHOT_ID in self.__columns.upper()\
			and not self.table_name in const.DICTIONARY_OBJECTS:
			return '%s,%s' % (const.COLUMN_SNAPSHOT_ID, self.__columns)

		return self.__columns

	@columns.setter
	def columns(self, value):
		if not value: raise EzDBError('Index should have columns defined.')
		self.__columns = value

	@property
	def table_name(self):
		return self.__table_name

	@table_name.setter
	def table_name(self, value):
		if not value: raise EzDBError('Index should has table name defined.')
		self.__table_name = value.upper()

	@property
	def enable_snapshot(self):
		return self.__enable_snapshot

	@enable_snapshot.setter
	def enable_snapshot(self, value):
		self.__enable_snapshot = value or False

	def index_ddl(self):
		if not (self.table_name or self.columns): return ''

		if self.type == 'PRIMARY':
			return 'ALTER TABLE {table_name} ADD CONSTRAINT {index_name} PRIMARY KEY({columns}) USING INDEX TABLESPACE &1;'.format(
				table_name=self.table_name, index_name=self.name, columns=self.columns
			)

		if self.type == 'UNIQUE':
			return 'ALTER TABLE {table_name} ADD CONSTRAINT {index_name} UNIQUE ({columns}) USING INDEX TABLESPACE &1;'.format(
				index_name=self.name, table_name=self.table_name, columns=self.columns
			)

		return 'CREATE INDEX {index_name} ON {table_name} ({columns}) TABLESPACE &1;'.format(
			index_name=self.name, table_name=self.table_name, columns=self.columns
		)

	def update(self, mapping):
		for key, value in mapping.items():
			if key.lower() == 'old_name':  # in the table xml file, index name is called "old name"
				self.name = value
			else:
				if key in self.__class__.__dict__ and \
						isinstance(self.__class__.__dict__[key], property):
					self.__setattr__(key, value)

	def update_name(self, table_name, seq):
		"""
		If the index name is not specified in the table xml file, call this method to generate the index name.
		"""

		if self.type == 'PRIMARY':
			self.name = 'PK_{table_name}'.format(table_name=table_name)
		else:
			self.name = 'I{0}_{1}'.format(seq, table_name)


if __name__ == '__main__':
	import doctest
	doctest.testmod()
	#index = Index()
	#index.type = 'PRIMARY'
	#index.name = 'PK_LO_TEST'
	#print index.index_ddl('LO_TEST')
	#
	#index.columns = 'NAME, DESC'
	#print index.index_ddl('LO_TEST')

