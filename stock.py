# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pyson import Eval, Id
from trytond.pool import Pool, PoolMeta
from trytond.modules.company.model import CompanyValueMixin
from trytond.i18n import gettext
from trytond.exceptions import UserError


def default_func(field_name):
    @classmethod
    def default(cls, **pattern):
        return getattr(
            cls.multivalue_model(field_name),
            'default_%s' % field_name, lambda: None)()
    return default


class Configuration(metaclass=PoolMeta):
    __name__ = 'stock.configuration'
    lot_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('sequence_type', '=', Id('stock_lot_sequence',
                        'sequence_type_lot')),
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ], required=True))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'lot_sequence':
            return pool.get('stock.configuration.company')
        return super(Configuration, cls).multivalue_model(field)

    default_lot_sequence = default_func('lot_sequence')


class CompanyConfiguration(ModelSQL, CompanyValueMixin):
    'Stock Company Configuration'
    __name__ = 'stock.configuration.company'
    lot_sequence = fields.Many2One('ir.sequence', 'Lot Sequence', domain=[
            ('sequence_type', '=', Id('stock_lot_sequence',
                    'sequence_type_lot')),
            ('company', 'in',
                [Eval('context', {}).get('company', -1), None]),
            ])

    @classmethod
    def default_lot_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('stock_lot_sequence', 'sequence_lot')
        except KeyError:
            return None


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
            if 'number' in values and len(values['number']) > 0:
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
        Config = pool.get('stock.configuration')

        config = Config(1)
        if product.template.lot_sequence:
            sequence = product.template.lot_sequence
        else:
            for category in product.categories:
                if category.lot_sequence:
                    sequence = category.lot_sequence
                    break
            else:
                if not config.lot_sequence:
                    raise UserError(gettext('stock_lot_sequence.no_sequence'))
                sequence = config.lot_sequence
        return sequence.get()
