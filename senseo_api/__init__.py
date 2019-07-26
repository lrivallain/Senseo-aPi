"""Senseo coffee machine API.

.. moduleauthor:: Ludovic Rivallain <ludovic.rivallain+senseo -> gmail.com>

"""

import sys

if sys.version_info < (3, 6):
    raise Exception('Senseo coffee machine API requires Python versions 3.6 or later.')

__all__ = [
    'pisenseo',
    'utils',
]
