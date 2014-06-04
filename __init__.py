# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from stock import *


def register():
    Pool.register(
        CompanyConfiguration,
        Configuration,
        Lot,
        module='stock_lot_sequence', type_='model')
