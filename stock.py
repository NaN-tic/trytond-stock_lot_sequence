# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['Lot', 'Configuration', 'CompanyConfiguration']
__metaclass__ = PoolMeta


class CompanyConfiguration(ModelSQL):
    'Stock Company Configuration'
    __name__ = 'stock.configuration.company'

    company = fields.Many2One('company.company', 'Company', required=True)
    lot_sequence = fields.Many2One('ir.sequence', 'Lot Sequence', domain=[
            ('code', '=', 'stock.lot'),
            ('company', 'in',
                [Eval('context', {}).get('company', -1), None]),
            ],
        required=True)

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
                ],
        required=True), 'get_configuration', setter='set_configuration')

    @classmethod
    def get_configuration(self, configs, names):
        pool = Pool()
        CompanyConfig = pool.get('stock.configuration.company')
        res = dict.fromkeys(names, [configs[0].id, None])
        company_configs = CompanyConfig.search([], limit=1)
        if len(company_configs) == 1:
            company_config, = company_configs
            for field_name in set(names):
                value = getattr(company_config, field_name, None)
                if value:
                    res[field_name] = {configs[0].id: value.id}
        return res

    @classmethod
    def set_configuration(self, configs, name, value):
        pool = Pool()
        CompanyConfig = pool.get('stock.configuration.company')
        company_configs = CompanyConfig.search([], limit=1)
        if len(company_configs) == 1:
            company_config, = company_configs
        else:
            company_config = CompanyConfig()
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
                'no_sequence':  'No sequence defined for lot. You must define'
                ' a sequence or enter lot\'s number.',
            })

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Config = pool.get('stock.configuration')

        config = Config(1)
        for values in vlist:
            if 'number' in values and len(values['number']) > 0:
                continue
            if not config.lot_sequence:
                cls.raise_user_error('no_sequence')
            values['number'] = Sequence.get_id(config.lot_sequence.id)
        return super(Lot, cls).create(vlist)
