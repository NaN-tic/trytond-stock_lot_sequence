# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta


class Lot(metaclass=PoolMeta):
    __name__ = 'stock.lot'

    @classmethod
    def preprocess_values(cls, mode, values):
        values = values.copy()
        if mode == 'create' and not values.get('number'):
            product_id = values.get('product')
            if product_id is not None:
                Product = Pool().get('product.product')
                # Resolve category and configuration fallbacks before the core
                # generates a number from the product sequence.
                number = cls.calc_number(
                    Product(product_id), lot_values=values)
                if number:
                    values['number'] = number
        return super().preprocess_values(mode, values)

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
                sequence = config.default_lot_sequence
        return sequence.get() if sequence else None
