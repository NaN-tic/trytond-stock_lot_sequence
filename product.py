# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)

__all__ = ['CategoryCompany', 'Category', 'TemplateCompany', 'Template',
    'Product']


class CategoryCompany(ModelSQL, CompanyValueMixin):
    'Category per Company'
    __name__ = 'product.category.company'

    category = fields.Many2One('product.category', 'Category', required=True,
        ondelete='CASCADE', select=True)
    lot_sequence = fields.Many2One(
        'ir.sequence', 'Lot Sequence',
        domain=[
            ('code', '=', 'stock.lot'),
            ('company', 'in', [Eval('company', -1), None]),
            ],
        depends=['company'])


class Category(CompanyMultiValueMixin):
    __name__ = 'product.category'
    __metaclass__ = PoolMeta

    lot_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('code', '=', 'stock.lot'),
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ],
            states={
                'invisible': ~Eval('context', {}).get('company'),
                }))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'lot_sequence':
            return pool.get('product.category.company')
        return super(Category, cls).multivalue_model(field)


class TemplateCompany(ModelSQL, CompanyValueMixin):
    'Template per Company'
    __name__ = 'product.template.company'

    template = fields.Many2One('product.template', 'Template', required=True,
        ondelete='CASCADE', select=True)
    lot_sequence = fields.Many2One(
        'ir.sequence', 'Lot Sequence',
        domain=[
            ('code', '=', 'stock.lot'),
            ('company', 'in', [Eval('company', -1), None]),
            ],
        depends=['company'])


class Template(CompanyMultiValueMixin):
    __name__ = 'product.template'
    __metaclass__ = PoolMeta

    lot_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('code', '=', 'stock.lot'),
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ],
            states={
                'invisible': ~Eval('context', {}).get('company'),
                }))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'lot_sequence':
            return pool.get('product.template.company')
        return super(Template, cls).multivalue_model(field)


class Product:
    __metaclass__ = PoolMeta
    __name__ = 'product.product'
