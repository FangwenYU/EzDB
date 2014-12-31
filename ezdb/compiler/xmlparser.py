__author__ = 'yufa'

import xml.etree.ElementTree as etree
import logging
from ezdb.common.exception import EzDBError
from dbobject.column import Column
from dbobject.table import Table
from dbobject.index import Index
from dbobject.plsql import PLSQL


def parse_table(xmlfile, enable_snapshot=False):
	"""
	Parse the given SaveDB table xml file and generate a Table object
	"""

	logging.info('Start processing table file: %s' % xmlfile)

	tree = etree.parse(xmlfile)
	root = tree.getroot()
	if root.tag.lower() != 'table':
		logging.warn('Not a table xml file: %s' % xmlfile)
		return

	table = Table(enable_snapshot)
	table.update(root.attrib)

	documentation = tree.find('./documentation')

	# If use [if document], it will generate the following warning message:
	# FutureWarning: The behavior of this method will change in future versions.
	# Use specific 'len(elem)' or 'elem is not None' test instead.
	if documentation is not None:
		table.documentation = documentation.text

	for item in tree.findall('./columns/column'):
		column = Column()
		column.update(item.attrib)

		# for documentation/default_value/sql_loader_ctl_expression
		for child in item:
			column[child.tag] = child.text

		table.add_column(column)

	for item in tree.findall('./indexes/index'):
		# Function-based index is not covered.
		columns = ','.join([column.attrib['name'].upper() for column in item.findall('./columns/column')])
		if columns:
			index = Index()
			index.update(item.attrib)
			index.columns = columns
			table.add_index(index)

	logging.info('Finish processing table file: %s' % xmlfile)
	return table


def parse_plsql(xmlfile):

	"""
	Parse the given SaveDB plsql xml file and return a PLSQL object
	"""

	logging.info('Start processing xml file: %s' % xmlfile)

	tree = etree.parse(xmlfile)
	root = tree.getroot()
	try:
		plsql = PLSQL(root.tag.upper())
	except EzDBError, e:
		logging.warn('Not a valid xml file: %s; error message: %s' % (xmlfile, e.message))
		return

	plsql.update(root.attrib)

	documentation = tree.find('./documentation')

	# If use [if document], it will generate the following warning message:
	# FutureWarning: The behavior of this method will change in future versions.
	# Use specific 'len(elem)' or 'elem is not None' test instead.
	if documentation is not None:
		plsql.documentation = documentation.text

	logging.info('Finish processing type file: %s' % xmlfile)
	return plsql



if __name__ == '__main__':
	table = parse_table(r'C:\Users\yufa\Desktop\Document\Study\Python\EzDB\RawFile\DB\Table\CD_FDW_STRUCTURE.XML')
	print table.table_ddl()
	print table.index_ddl()
