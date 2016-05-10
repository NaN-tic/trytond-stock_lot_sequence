#!/usr/bin/env python
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.pool import Pool

from trytond.modules.company.tests import create_company, set_company


class TestCase(ModuleTestCase):
    'Test module'
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
        Config = pool.get('stock.configuration')
        Lot = pool.get('stock.lot')

        company = create_company()
        with set_company(company):
            category = Category(name='Category')
            category.save()

            unit, = Uom.search([
                    ('name', '=', 'Unit'),
                    ])

            template = Template(
                name='Test Lot Sequence',
                list_price=Decimal(10),
                cost_price=Decimal(3),
                default_uom=unit,
                categories=[category],
                )
            template.save()
            product = Product(template=template)
            product.save()

            with self.assertRaises(UserError):
                lot, = Lot.create([{'product': product.id}])

            sequence = Sequence(code='stock.lot', name='Config Sequence')
            sequence.save()
            cat_sequence = Sequence(code='stock.lot', name='Category Sequence')
            cat_sequence.save()
            tem_sequence = Sequence(code='stock.lot', name='Template Sequence')
            tem_sequence.save()
            with Transaction().set_context(company=company.id):
                config = Config()
                config.lot_sequence = sequence
                config.save()
                lots = Lot.create([
                        {'product': product.id},
                        {'product': product.id},
                        {'product': product.id},
                        {'product': product.id},
                        {'product': product.id},
                        ])
                self.assertEqual([l.number for l in lots], [str(x) for x
                        in range(1, 6)])

                # Set number manualy
                lot = Lot(product=product, number='M1')
                lot.save()
                self.assertEqual(lot.number, 'M1')

                lots = Lot.create([
                        {'product': product.id},
                        {'product': product.id},
                        {'product': product.id},
                        {'product': product.id},
                        {'product': product.id},
                        ])
                self.assertEqual([l.number for l in lots], [str(x) for x
                        in range(6, 11)])

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


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCase))
    return suite
