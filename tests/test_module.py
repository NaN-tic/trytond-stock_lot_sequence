
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from decimal import Decimal
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool

from trytond.modules.company.tests import (CompanyTestMixin, create_company,
    set_company)


class StockLotSequenceTestCase(CompanyTestMixin, ModuleTestCase):
    'Test StockLotSequence module'
    module = 'stock_lot_sequence'

    @with_transaction()
    def test_lot_sequence(self):
        'Test lot sequence'
        pool = Pool()
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        Category = pool.get('product.category')
        Uom = pool.get('product.uom')
        Sequence = pool.get('ir.sequence')
        SequenceType = pool.get('ir.sequence.type')
        Lot = pool.get('stock.lot')
        ModelData = pool.get('ir.model.data')

        company = create_company()
        with set_company(company):
            category = Category(name='Category')
            category.save()
            self.assertEqual(category.lot_sequence, None)

            unit, = Uom.search([
                    ('name', '=', 'Unit'),
                    ])

            template = Template(
                name='Test Lot Sequence',
                list_price=Decimal(10),
                cost_price=Decimal(3),
                default_uom=unit,
                categories=[category],
                lot_sequence=None,
                )
            template.save()
            product = Product(template=template)
            product.save()
            self.assertEqual(template.lot_sequence, None)

            lot, = Lot.create([{'product': product.id}])

            sequence_type = SequenceType(ModelData.get_id('stock_lot',
                    'sequence_type_stock_lot'))
            cat_sequence = Sequence(sequence_type=sequence_type,
                name='Category Sequence')
            cat_sequence.save()
            sequence_type = SequenceType(ModelData.get_id('stock_lot',
                    'sequence_type_stock_lot'))
            tem_sequence = Sequence(sequence_type=sequence_type,
                name='Template Sequence')
            tem_sequence.save()

            lots = Lot.create([
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    ])
            self.assertEqual([l.number for l in lots], [str(x) for x
                    in range(2, 7)])

            # Set number manualy
            lot = Lot(product=product, number='M1')
            lot.save()
            self.assertEqual(lot.number, 'M1')

            # category + not category sequence
            lots = Lot.create([
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    ])
            self.assertEqual([l.number for l in lots], [str(x) for x
                    in range(7, 12)])

            # category + category sequence
            category.lot_sequence = cat_sequence
            category.save()
            # It should use the category sequence
            lots = Lot.create([
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    ])
            self.assertEqual([l.number for l in lots], [str(x) for x
                    in range(1, 6)])

            # not category sequence + template sequence
            template.lot_sequence = tem_sequence
            template.save()
            # It should use the template sequence
            lots = Lot.create([
                    {'product': product.id},
                    {'product': product.id},
                    {'product': product.id},
                    ])
            self.assertEqual([l.number for l in lots], [str(x) for x
                    in range(1, 4)])


del ModuleTestCase
