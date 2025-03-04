# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from sql import  Null, Table
from trytond.transaction import Transaction
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
            ('sequence_type', '=', Id('stock_lot', 'sequence_type_stock_lot')),
            ('company', '=', None),
            ])

    @classmethod
    def __register__(cls, module_name):
        exist = backend.TableHandler.table_exist('product_category_company')

        if exist:
            backend.TableHandler.table_rename('product_category_company', cls._table)
        super().__register__(module_name)


class Category(CompanyMultiValueMixin, metaclass=PoolMeta):
    __name__ = 'product.category'
    lot_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
        'Lot Sequence', domain=[
            ('sequence_type', '=', Id('stock_lot', 'sequence_type_stock_lot')),
            ('company', '=', None),
            ]))
    lot_sequences = fields.One2Many('product.category.lot_sequence',
        'category', 'Lot Sequences')


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        Sequence = pool.get('ir.sequence')

        exist = backend.TableHandler.table_exist('product_template_lot_sequence')

        super().__register__(module_name)

        if exist:
            lot_sequence = Table('product_template_lot_sequence')
            template = cls.__table__()
            sequence = Sequence.__table__()
            cursor = Transaction().connection.cursor()

            query = lot_sequence.select(lot_sequence.lot_sequence, lot_sequence.template, where=lot_sequence.lot_sequence != Null)
            cursor.execute(*query)

            sequence_ids = set()
            for row in cursor.fetchall():
                sequence_id = row[0]
                template_id = row[1]
                cursor.execute(*template.update(
                        columns=[template.lot_sequence],
                        values=[sequence_id],
                        where=template.id == template_id))
                sequence_ids.add(sequence_id)

            if sequence_ids:
                cursor.execute(*sequence.update(
                        columns=[sequence.company],
                        values=[Null],
                        where=sequence.id.in_(list(sequence_ids))))

            backend.TableHandler.table_rename('product_template_lot_sequence',
                'product_template_lot_sequence_back')
