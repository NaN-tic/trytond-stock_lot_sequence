# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.i18n import gettext
from trytond.exceptions import UserError


class Lot(metaclass=PoolMeta):
    __name__ = 'stock.lot'

    @classmethod
    def __setup__(cls):
        super(Lot, cls).__setup__()
        if cls.number.required:
            cls.number.required = False

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Product = pool.get('product.product')
        for values in vlist:
            if values.get('number') and len(values['number']) > 0:
                continue
            values['number'] = cls.calc_number(Product(values['product']),
                lot_values=values)
        return super(Lot, cls).create(vlist)

    @classmethod
    def copy(cls, lots, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('number')
        return super(Lot, cls).copy(lots, default=default)

    @classmethod
    def calc_number(cls, product, lot_values=None):
        pool = Pool()
        Config = pool.get('product.configuration')

        config = Config(1)
        if product.template.lot_sequence:
            sequence = product.template.lot_sequence
        else:
            for category in product.categories:
                if category.lot_sequence:
                    sequence = category.lot_sequence
                    break
            else:
                if not config.default_lot_sequence:
                    raise UserError(gettext('stock_lot_sequence.no_sequence'))
                sequence = config.default_lot_sequence
        return sequence.get()
