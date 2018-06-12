# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval
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


class Template:
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
