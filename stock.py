# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import Model, ModelSQL, fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['Lot', 'Configuration', 'CompanyConfiguration']
__metaclass__ = PoolMeta


class CompanyConfiguration(ModelSQL):
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
    __name__ = 'stock.configuration'

    lot_sequence = fields.Function(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('code', '=', 'stock.lot'),
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ], required=True),
        'get_configuration', setter='set_configuration')

    @classmethod
    def get_configuration(cls, configs, names):
        pool = Pool()
        CompanyConfig = pool.get('stock.configuration.company')

        company_id = Transaction().context.get('company')
        company_configs = CompanyConfig.search([
                ('company', '=', company_id),
                ])

        res = {}
        for fname in names:
            res[fname] = {}.fromkeys([c.id for c in configs], None)
            if company_configs:
                val = getattr(company_configs[0], fname)
                if isinstance(val, Model):
                    val = val.id
                res[fname][configs[0].id] = val
        return res

    @classmethod
    def set_configuration(cls, configs, name, value):
        pool = Pool()
        CompanyConfig = pool.get('stock.configuration.company')

        company_id = Transaction().context.get('company')
        company_configs = CompanyConfig.search([
                ('company', '=', company_id),
                ])
        if company_configs:
            company_config = company_configs[0]
        else:
            company_config = CompanyConfig(company=company_id)
        setattr(company_config, name, value)
        company_config.save()


class Lot:
    __name__ = 'stock.lot'

    @classmethod
    def __setup__(cls):
        super(Lot, cls).__setup__()
        if cls.number.required:
            cls.number.required = False
        cls._error_messages.update({
                'no_sequence':  ('No sequence defined for lot. You must '
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
        if 'number' not in default:
            default['number'] = ''
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
