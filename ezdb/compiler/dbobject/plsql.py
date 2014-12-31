__author__ = 'yufa'

from ezdb.common.exception import EzDBError
from ezdb.common.constants import const
import dbmeta
import logging


class PLSQL(object):
	"""
	PLSQL object class, including type, package, procedure, function, sequence, trigger

	>>> t = PLSQL(const.PLSQL_TYPE)
	>>> t.name = 'T_CHAR_TABLE'

	"""

	def __init__(self, object_type, name=None, story=None, release=None, products_formula=None,
	             documentation=None, install_order=None):
		if name:
			self.name = name
		else:
			self.__name = None

		self.object_type = object_type
		self.story = story
		self.release = release
		self.products_formula = products_formula
		self.documentation = documentation
		self.install_order = install_order

	@property
	def object_type(self):
		return self.__object_type

	@object_type.setter
	def object_type(self, value):
		if not value in (
			const.PLSQL_PACKAGE, const.PLSQL_FUNCTION, const.PLSQL_PROCEDURE,
			const.PLSQL_TYPE, const.PLSQL_TRIGGER, const.PLSQL_SEQUENCE
		):
			raise EzDBError('Unknown object type: %s!' % value)

		self.__object_type = value

	@property
	def name(self):
		if not self.__name:
			raise EzDBError('Type name is not set')
		return self.__name

	@name.setter
	def name(self, value):
		if not value:
			raise EzDBError('Type name cannot be None.')
		if len(value) > 30:
			raise EzDBError('Type name cannot exceed 30 bytes.')
		self.__name = value.upper()

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
	def products_formula(self):
		return self.__products_formula

	@products_formula.setter
	def products_formula(self, value):
		self.__products_formula = value or const.DEFAULT_PRODUCT_CODE

	@property
	def documentation(self):
		return self.__documentation

	@documentation.setter
	def documentation(self, value):
		self.__documentation = value or ''

	@property
	def install_order(self):
		return self.__install_order

	@install_order.setter
	def install_order(self, value):
		self.__install_order = int(value) if value else 1

	def update(self, mapping):
		for key, value in mapping.items():
			if key in self.__class__.__dict__ and \
					isinstance(self.__class__.__dict__[key], property):
				self.__setattr__(key, value)

	def metadata(self):
		"""
		Return the metadata to be stored in the table DB_OBJECTS
		"""
		metadata = dbmeta.db_objects_metadata(
			table_name = self.name,
			object_type = self.object_type,
			description = self.documentation,
			release = self.release,
			relevant_for = self.products_formula,
			story_id = self.story,
		    install_order = self.install_order
		)

		logging.debug('[%s] metadata in table DB_OBJECTS:\n%s' % (self.name, metadata))
		return metadata


if __name__ == '__main__':
	import doctest
	doctest.testmod()
