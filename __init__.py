# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import product
from . import stock


def register():
    Pool.register(
        product.Configuration,
        product.ConfigurationDefaultLotSequence,
        product.CategoryCompany,
        product.Category,
        product.TemplateCompany,
        product.Template,
        product.Product,
        stock.Lot,
        module='stock_lot_sequence', type_='model')
