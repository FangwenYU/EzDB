from distutils.core import setup

setup(
	name='EzDB',
	version='1.0.0.0',
	packages=['ezdb', 'ezdb.common', 'ezdb.compiler', 'ezdb.compiler.dbobject', 'ezdb.generator'],
	url='',
	license='',
	author='yufa',
	author_email='fang.yu@moodys.com',
	description='A toolkit to generate DB package based on SaveDB xml files.'
)
