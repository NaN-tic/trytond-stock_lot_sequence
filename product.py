# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from trytond import backend
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)

__all__ = ['CategoryCompany', 'Category', 'TemplateCompany', 'Template']


class CategoryCompany(ModelSQL, CompanyValueMixin):
    'Category per Company'
    __name__ = 'product.category.lot_sequence'

    category = fields.Many2One('product.category', 'Category', required=True,
        ondelete='CASCADE', select=True)
    lot_sequence = fields.Many2One(
        'ir.sequence', 'Lot Sequence',
        select=True,
        domain=[
            ('code', '=', 'stock.lot'),
            ('company', 'in', [Eval('company', -1), None]),
            ],
        depends=['company'])

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        exist = TableHandler.table_exist('product_category_company')

        if exist:
            TableHandler.table_rename('product_category_company', cls._table)
        super(CategoryCompany, cls).__register__(module_name)


class Category(CompanyMultiValueMixin, metaclass=PoolMeta):
    __name__ = 'product.category'

    lot_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('code', '=', 'stock.lot'),
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
        ondelete='CASCADE', select=True)
    lot_sequence = fields.Many2One(
        'ir.sequence', 'Lot Sequence',
        domain=[
            ('code', '=', 'stock.lot'),
            ('company', 'in', [Eval('company', -1), None]),
            ],
        select=True,
        depends=['company'])

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        exist = TableHandler.table_exist('product_template_company')

        if exist:
            TableHandler.table_rename('product_template_company', cls._table)
        super(TemplateCompany, cls).__register__(module_name)


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'

    lot_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('code', '=', 'stock.lot'),
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ],
            states={
                'invisible': ~Eval('context', {}).get('company'),
                }))

    lot_sequences = fields.One2Many('product.template.lot_sequence',
        'template', 'Lot Sequences')
