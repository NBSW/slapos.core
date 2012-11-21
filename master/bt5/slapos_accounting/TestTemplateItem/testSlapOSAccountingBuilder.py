# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#
##############################################################################

from Products.SlapOS.tests.testSlapOSMixin import \
  testSlapOSMixin
from DateTime import DateTime

def convertCategoryList(base, l):
  return ['%s/%s' % (base, q) for q in l]

class TestSlapOSSalePackingListBuilder(testSlapOSMixin):
  def checkSimulationMovement(self, simulation_movement):
    self.assertEqual(1.0, simulation_movement.getDeliveryRatio())
    self.assertEqual(0.0, simulation_movement.getDeliveryError())
    self.assertNotEqual(None, simulation_movement.getDeliveryValue())

  def checkDeliveryLine(self, simulation_movement, delivery_line,
      line_portal_type, cell_portal_type):
    self.assertEqual(line_portal_type, delivery_line.getPortalType())
    self.assertSameSet([
        'resource/service_module/slapos_instance_subscription',
        'use/trade/sale',
        'quantity_unit/unit/piece',
        'base_contribution/base_amount/invoicing/discounted',
        'base_contribution/base_amount/invoicing/taxable'] \
          + convertCategoryList('aggregate',
            simulation_movement.getAggregateList()),
      delivery_line.getCategoryList()
    )
    self.assertEqual(simulation_movement.getQuantity(),
        delivery_line.getQuantity())
    self.assertEqual(simulation_movement.getPrice(),
        delivery_line.getPrice())
    self.assertFalse(delivery_line.hasStartDate())
    self.assertFalse(delivery_line.hasStopDate())
    self.assertEqual([], delivery_line.contentValues(
        portal_type=cell_portal_type))

  def checkDelivery(self, simulation_movement, delivery, delivery_portal_type,
        category_list, simulation_state='delivered'):
    self.assertEqual(delivery_portal_type, delivery.getPortalType())
    self.assertEqual(simulation_state, delivery.getSimulationState())
    self.assertEqual('building', delivery.getCausalityState())
    delivery.updateCausalityState(solve_automatically=False)
    self.assertEqual('solved', delivery.getCausalityState())
    self.assertEqual(simulation_movement.getStartDate(),
      delivery.getStartDate())
    self.assertEqual(simulation_movement.getStopDate(),
      delivery.getStopDate())
    self.assertSameSet([
          'source/organisation_module/slapos',
          'source_section/organisation_module/slapos',
          'price_currency/currency_module/EUR',
          'specialise/sale_trade_condition_module/slapos_trade_condition'] \
            + convertCategoryList('destination',
                simulation_movement.getDestinationList()) \
            + convertCategoryList('destination_section',
                simulation_movement.getDestinationSectionList()) \
            + convertCategoryList('destination_decision',
                simulation_movement.getDestinationDecisionList()) \
            + category_list,
      delivery.getCategoryList())

  def test(self):
    hosting_subscription = self.portal.hosting_subscription_module\
        .template_hosting_subscription.Base_createCloneDocument(batch_mode=1)
    applied_rule = self.portal.portal_simulation.newContent(
      portal_type='Applied Rule',
      causality=hosting_subscription.getRelativeUrl(),
      specialise='portal_rules/slapos_subscription_item_rule'
    )
    person = self.portal.person_module.template_member\
        .Base_createCloneDocument(batch_mode=1)
    simulation_movement_kw = dict(
        portal_type='Simulation Movement',
        aggregate=hosting_subscription.getRelativeUrl(),
        base_contribution=['base_amount/invoicing/discounted',
            'base_amount/invoicing/taxable'],
        causality=['business_process_module/slapos_sale_business_process'
            '/deliver', 'business_process_module/slapos_sale_business_pr'
            'ocess/delivery_path'],
        destination=person.getRelativeUrl(),
        destination_decision=person.getRelativeUrl(),
        destination_section=person.getRelativeUrl(),
        price_currency='currency_module/EUR',
        quantity_unit='unit/piece',
        resource='service_module/slapos_instance_subscription',
        source='organisation_module/slapos',
        source_section='organisation_module/slapos',
        specialise='sale_trade_condition_module/slapos_trade_condition',
        trade_phase='slapos/delivery',
        use='trade/sale',
    )
    simulation_movement_1 = applied_rule.newContent(
        quantity=1.2,
        price=3.4,
        start_date=DateTime('2012/01/01'),
        stop_date=DateTime('2012/02/01'),
        **simulation_movement_kw
    )
    simulation_movement_2 = applied_rule.newContent(
        quantity=5.6,
        price=7.8,
        start_date=DateTime('2012/03/01'),
        stop_date=DateTime('2012/04/01'),
        **simulation_movement_kw
    )

    self.tic()

    self.portal.portal_deliveries.slapos_sale_packing_list_builder.build(
        path='%s/%%' % applied_rule.getPath())
    self.tic()

    self.checkSimulationMovement(simulation_movement_1)
    self.checkSimulationMovement(simulation_movement_2)

    delivery_line_1 = simulation_movement_1.getDeliveryValue()
    delivery_line_2 = simulation_movement_2.getDeliveryValue()
    self.assertNotEqual(delivery_line_1.getRelativeUrl(),
        delivery_line_2.getRelativeUrl())

    line_kw = dict(line_portal_type='Sale Packing List Line',
        cell_portal_type='Sale Packing List Cell')
    self.checkDeliveryLine(simulation_movement_1, delivery_line_1, **line_kw)
    self.checkDeliveryLine(simulation_movement_2, delivery_line_2, **line_kw)

    delivery_1 = delivery_line_1.getParentValue()
    delivery_2 = delivery_line_2.getParentValue()

    self.assertNotEqual(delivery_1.getRelativeUrl(),
        delivery_2.getRelativeUrl())

    delivery_kw = dict(delivery_portal_type='Sale Packing List',
        category_list=convertCategoryList('causality',
          simulation_movement_1.getParentValue().getCausalityList()))
    self.checkDelivery(simulation_movement_1, delivery_1, **delivery_kw)
    self.checkDelivery(simulation_movement_2, delivery_2, **delivery_kw)

class TestSlapOSSaleInvoiceBuilder(TestSlapOSSalePackingListBuilder):
  def test(self):
    hosting_subscription = self.portal.hosting_subscription_module\
        .template_hosting_subscription.Base_createCloneDocument(batch_mode=1)
    applied_rule = self.portal.portal_simulation.newContent(
      portal_type='Applied Rule',
      causality=hosting_subscription.getRelativeUrl(),
      specialise='portal_rules/slapos_subscription_item_rule'
    )
    person = self.portal.person_module.template_member\
        .Base_createCloneDocument(batch_mode=1)
    delivery_kw = dict(
        portal_type='Sale Packing List',
        causality=hosting_subscription.getRelativeUrl(),
        price_currency='currency_module/EUR',
        source='organisation_module/slapos',
        source_section='organisation_module/slapos',
        specialise='sale_trade_condition_module/slapos_trade_condition',
    )
    delivery_line_kw = dict(
        portal_type='Sale Packing List Line',
        resource='service_module/slapos_instance_subscription',
        use='trade/sale',
        quantity_unit='unit/piece',
        base_contribution_list=['base_amount/invoicing/discounted',
            'base_amount/invoicing/taxable'],
        aggregate=hosting_subscription.getRelativeUrl(),
    )
    delivery_1 = self.portal.sale_packing_list_module.newContent(
        destination=person.getRelativeUrl(),
        destination_decision=person.getRelativeUrl(),
        destination_section=person.getRelativeUrl(),
        start_date=DateTime('2012/01/01'),
        stop_date=DateTime('2012/02/01'),
        **delivery_kw
    )
    self.portal.portal_workflow._jumpToStateFor(delivery_1, 'delivered')
    self.portal.portal_workflow._jumpToStateFor(delivery_1, 'calculating')
    delivery_line_1 = delivery_1.newContent(
        quantity=1.2,
        price=3.4,
        **delivery_line_kw
    )
    delivery_2 = self.portal.sale_packing_list_module.newContent(
        destination=person.getRelativeUrl(),
        destination_decision=person.getRelativeUrl(),
        destination_section=person.getRelativeUrl(),
        start_date=DateTime('2012/01/01'),
        stop_date=DateTime('2012/02/01'),
        **delivery_kw
    )
    self.portal.portal_workflow._jumpToStateFor(delivery_2, 'delivered')
    self.portal.portal_workflow._jumpToStateFor(delivery_2, 'calculating')
    delivery_line_2 = delivery_2.newContent(
        quantity=5.6,
        price=7.8,
        **delivery_line_kw
    )
    simulation_movement_kw = dict(
        portal_type='Simulation Movement',
        aggregate=hosting_subscription.getRelativeUrl(),
        base_contribution=['base_amount/invoicing/discounted',
            'base_amount/invoicing/taxable'],
        causality=['business_process_module/slapos_sale_business_process'
            '/deliver', 'business_process_module/slapos_sale_business_pr'
            'ocess/delivery_path'],
        destination=person.getRelativeUrl(),
        destination_decision=person.getRelativeUrl(),
        destination_section=person.getRelativeUrl(),
        price_currency='currency_module/EUR',
        quantity_unit='unit/piece',
        resource='service_module/slapos_instance_subscription',
        source='organisation_module/slapos',
        source_section='organisation_module/slapos',
        specialise='sale_trade_condition_module/slapos_trade_condition',
        trade_phase='slapos/delivery',
        use='trade/sale',
        delivery_ratio=1.0
    )
    simulation_movement_1 = applied_rule.newContent(
        quantity=delivery_line_1.getQuantity(),
        price=delivery_line_1.getPrice(),
        start_date=delivery_1.getStartDate(),
        stop_date=delivery_1.getStopDate(),
        delivery=delivery_line_1.getRelativeUrl(),
        **simulation_movement_kw
    )
    simulation_movement_2 = applied_rule.newContent(
        quantity=delivery_line_2.getQuantity(),
        price=delivery_line_2.getPrice(),
        start_date=delivery_2.getStartDate(),
        stop_date=delivery_2.getStopDate(),
        delivery=delivery_line_2.getRelativeUrl(),
        **simulation_movement_kw
    )

    self.tic()
    delivery_1.updateCausalityState(solve_automatically=False)
    delivery_2.updateCausalityState(solve_automatically=False)
    self.tic()

    # test the test
    self.assertEqual('solved', delivery_1.getCausalityState())
    self.assertEqual('solved', delivery_2.getCausalityState())

    # create new simulation movements
    invoice_movement_kw = simulation_movement_kw.copy()
    invoice_movement_kw.update(
        causality=[
            'business_process_module/slapos_sale_business_process/invoice',
            'business_process_module/slapos_sale_business_process/invoice_path'
        ],
        trade_phase='slapos/invoicing'
    )
    invoice_rule_1 = simulation_movement_1.newContent(
        portal_type='Applied Rule',
        specialise='portal_rules/slapos_invoice_simulation_rule')
    invoice_movement_1 = invoice_rule_1.newContent(
        start_date=delivery_1.getStartDate(),
        stop_date=delivery_1.getStopDate(),
        quantity=delivery_line_1.getQuantity(),
        price=delivery_line_1.getPrice(),
        **invoice_movement_kw)

    invoice_rule_2 = simulation_movement_2.newContent(
        portal_type='Applied Rule',
        specialise='portal_rules/slapos_invoice_simulation_rule')
    invoice_movement_2 = invoice_rule_2.newContent(
        start_date=delivery_2.getStartDate(),
        stop_date=delivery_2.getStopDate(),
        quantity=delivery_line_2.getQuantity(),
        price=delivery_line_2.getPrice(),
        **invoice_movement_kw)
    self.tic()

    self.portal.portal_deliveries.slapos_sale_invoice_builder.build(
        path='%s/%%' % applied_rule.getPath())
    self.tic()

    self.checkSimulationMovement(invoice_movement_1)
    self.checkSimulationMovement(invoice_movement_2)

    invoice_line_1 = invoice_movement_1.getDeliveryValue()
    invoice_line_2 = invoice_movement_2.getDeliveryValue()
    self.assertNotEqual(invoice_line_1.getRelativeUrl(),
        invoice_line_2.getRelativeUrl())

    line_kw = dict(line_portal_type='Invoice Line',
        cell_portal_type='Invoice Cell')
    self.checkDeliveryLine(invoice_movement_1, invoice_line_1, **line_kw)
    self.checkDeliveryLine(invoice_movement_2, invoice_line_2, **line_kw)

    invoice_1 = invoice_line_1.getParentValue()
    invoice_2 = invoice_line_2.getParentValue()

    self.assertNotEqual(invoice_1.getRelativeUrl(),
        invoice_2.getRelativeUrl())

    invoice_kw = dict(delivery_portal_type='Sale Invoice Transaction',
        simulation_state='confirmed')
    category_list = ['resource/currency_module/EUR']
    self.checkDelivery(invoice_movement_1, invoice_1,
        category_list=category_list + convertCategoryList('causality',
          [delivery_1.getRelativeUrl()]), **invoice_kw)
    self.checkDelivery(invoice_movement_2, invoice_2,
        category_list=category_list + convertCategoryList('causality',
          [delivery_2.getRelativeUrl()]), **invoice_kw)

class TestSlapOSSaleInvoiceTransactionBuilder(testSlapOSMixin):
  def test(self):
    raise NotImplementedError

class TestSlapOSSaleInvoiceTransactionTradeModelBuilder(testSlapOSMixin):
  def test(self):
    raise NotImplementedError

class TestSlapOSPaymentTransactionBuilder(testSlapOSMixin):
  def test(self):
    raise NotImplementedError
