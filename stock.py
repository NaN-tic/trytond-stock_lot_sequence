# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.modules.company.model import CompanyValueMixin

__all__ = ['Lot', 'Configuration', 'CompanyConfiguration']


class CompanyConfiguration(ModelSQL, CompanyValueMixin):
    'Stock Company Configuration'
    __name__ = 'stock.configuration.company'

    company = fields.Many2One('company.company', 'Company', required=True,
        ondelete='CASCADE', select=True)
    lot_sequence = fields.Many2One('ir.sequence', 'Lot Sequence', domain=[
            ('code', '=', 'stock.lot'),
            ('company', 'in',
                [Eval('context', {}).get('company', -1), None]),
            ])

    @staticmethod
    def default_company():
        return Transaction().context.get('company')


class Configuration:
    __metaclass__ = PoolMeta
    __name__ = 'stock.configuration'

    lot_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('code', '=', 'stock.lot'),
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ], required=True))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'lot_sequence':
            return pool.get('stock.configuration.company')
        return super(Configuration, cls).multivalue_model(field)


class Lot:
    __metaclass__ = PoolMeta
    __name__ = 'stock.lot'

    @classmethod
    def __setup__(cls):
        super(Lot, cls).__setup__()
        if cls.number.required:
            cls.number.required = False
        cls._error_messages.update({
                'no_sequence': ('No sequence defined for lot. You must '
                    'define a sequence or enter lot\'s number.'),
                })

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
        Sequence = pool.get('ir.sequence')
        Config = pool.get('stock.configuration')

        config = Config(1)
        if product.lot_sequence:
            sequence_id = product.lot_sequence.id
        else:
            for category in product.categories:
                if category.lot_sequence:
                    sequence_id = category.lot_sequence.id
                    break
            else:
                if not config.lot_sequence:
                    cls.raise_user_error('no_sequence')
                sequence_id = config.lot_sequence.id
        return Sequence.get_id(sequence_id)
