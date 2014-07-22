# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['CategoryCompany', 'Category', 'TemplateCompany', 'Template']
__metaclass__ = PoolMeta


class CategoryCompany:
    __name__ = 'product.category.company'

    lot_sequence = fields.Many2One('ir.sequence', 'Lot Sequence', domain=[
            ('code', '=', 'stock.lot'),
            ('company', 'in',
                [Eval('context', {}).get('company', -1), None]),
            ])


class Category:
    __name__ = 'product.category'

    lot_sequence = fields.Function(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('code', '=', 'stock.lot'),
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ],
            states={
                'invisible': ~Eval('context', {}).get('company'),
                }),
        'get_by_company_fields', setter='set_by_company_field')


class TemplateCompany:
    __name__ = 'product.template.company'

    lot_sequence = fields.Many2One('ir.sequence', 'Lot Sequence', domain=[
            ('code', '=', 'stock.lot'),
            ('company', 'in',
                [Eval('context', {}).get('company', -1), None]),
            ])


class Template:
    __name__ = 'product.template'

    lot_sequence = fields.Function(fields.Many2One('ir.sequence',
            'Lot Sequence', domain=[
                ('code', '=', 'stock.lot'),
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ],
            states={
                'invisible': ~Eval('context', {}).get('company'),
                }),
        'get_by_company_fields', setter='set_by_company_field')
