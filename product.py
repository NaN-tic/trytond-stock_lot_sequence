# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval, Id
from trytond import backend
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)

def default_func(field_name):
    @classmethod
    def default(cls, **pattern):
        return getattr(
            cls.multivalue_model(field_name),
            'default_%s' % field_name, lambda: None)()
    return default


class Configuration(metaclass=PoolMeta):
    __name__ = 'product.configuration'
    default_default_lot_sequence = default_func('default_lot_sequence')


class ConfigurationDefaultLotSequence(metaclass=PoolMeta):
    __name__ = 'product.configuration.default_lot_sequence'

    @classmethod
    def default_default_lot_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('stock_lot_sequence', 'sequence_lot')
        except KeyError:
            return None


class CategoryCompany(ModelSQL, CompanyValueMixin):
    'Category per Company'
    __name__ = 'product.category.lot_sequence'
    category = fields.Many2One('product.category', 'Category', required=True,
        ondelete='CASCADE', context={
            'company': Eval('company', -1),
            },
        depends=['company'])
    lot_sequence = fields.Many2One(
        'ir.sequence', 'Lot Sequence',
        domain=[
            ('sequence_type', '=', Id('stock_lot',
                    'sequence_type_stock_lot')),
            ('company', 'in', [Eval('company', -1), None]),
            ])

    @classmethod
    def __register__(cls, module_name):
        exist = backend.TableHandler.table_exist('product_category_company')

        if exist:
            backend.TableHandler.table_rename('product_category_company', cls._table)
        super(CategoryCompany, cls).__register__(module_name)


class Category(CompanyMultiValueMixin, metaclass=PoolMeta):
    __name__ = 'product.category'
    lot_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('sequence_type', '=', Id('stock_lot',
                        'sequence_type_stock_lot')),
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ],
            states={
                'invisible': ~Eval('context', {}).get('company'),
                }))

    lot_sequences = fields.One2Many('product.category.lot_sequence',
        'category', 'Lot Sequences')


class TemplateCompany(ModelSQL, CompanyValueMixin):
    'Template per Company'
    __name__ = 'product.template.lot_sequence'
    template = fields.Many2One('product.template', 'Template', required=True,
        ondelete='CASCADE', context={
            'company': Eval('company', -1),
            },
        depends=['company'])
    lot_sequence = fields.Many2One(
        'ir.sequence', 'Lot Sequence',
        domain=[
            ('sequence_type', '=', Id('stock_lot',
                    'sequence_type_stock_lot')),
            ('company', 'in', [Eval('company', -1), None]),
            ])

    @classmethod
    def __register__(cls, module_name):
        exist = backend.TableHandler.table_exist('product_template_company')

        if exist:
            backend.TableHandler.table_rename('product_template_company',
                cls._table)
        super(TemplateCompany, cls).__register__(module_name)


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    lot_sequences = fields.One2Many('product.template.lot_sequence',
        'template', 'Lot Sequences')

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        # replace m2o field from stock_lot to MultiValue
        cls.lot_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
                'Lot Sequence', domain=[
                    ('sequence_type', '=', Id('stock_lot',
                            'sequence_type_stock_lot')),
                    ('company', 'in',
                        [Eval('context', {}).get('company', -1), None]),
                    ],
                states={
                    'invisible': ~Eval('context', {}).get('company'),
                    }))


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'
