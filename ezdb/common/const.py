__author__ = 'yufa'

class _Const(object):
	"""
	Used to simulate const descriptor in other languages
	"""

	class ConstError(TypeError): pass
	class ConstCaseError(ConstError): pass

	def __setattr__(self, key, value):
		if self.__dict__.has_key(key):
			raise self.ConstError("Cannot change constant: %s" % key)
		if not key.isupper():
			raise self.ConstCaseError('Const name %s is not in upper case.' % key)

		self.__dict__[key] = value

import sys
sys.modules[__name__] = _Const()
