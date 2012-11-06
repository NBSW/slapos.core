# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#
##############################################################################
from Products.SlapOS.tests.testSlapOSMixin import \
  testSlapOSMixin
import transaction

def getMessageList(o):
  return [str(q.getMessage()) for q in o.checkConsistency()]

class TestSlapOSConstraintMixin(testSlapOSMixin):
  def _test_property_existence(self, property_id, consistency_message):
    self.software_instance.edit(**{property_id:'A'})

    # fetch basic list of consistency messages
    current_message_list = getMessageList(self.software_instance)

    # test the test: no expected message found
    self.assertFalse(consistency_message in current_message_list)


    # required
    self.software_instance.edit(**{property_id:None})
    self.assertTrue(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(**{property_id:''})
    self.assertTrue(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(**{property_id:'A'})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

class TestSlapOSSoftwareInstanceConstraint(TestSlapOSConstraintMixin):
  def afterSetUp(self):
    self.software_instance = self.portal.software_instance_module.newContent(
      portal_type='Software Instance')

  def beforeTearDown(self):
    transaction.abort()

  def test_connection_xml(self):
    # fetch basic list of consistency messages
    current_message_list = getMessageList(self.software_instance)

    consistency_message = "Connection XML is invalid: Start tag expected, '<' not "\
        "found, line 1, column 1"

    # test the test: no expected message found
    self.assertFalse(consistency_message in current_message_list)


    # connection_xml is optional
    self.software_instance.edit(connection_xml=None)
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

    self.software_instance.edit(connection_xml='')
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

    # if available shall be correct XML
    self.software_instance.edit(connection_xml='this is bad xml')
    self.assertTrue(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(connection_xml=self.generateEmptyXml())
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

  def test_property_existence_destination_reference(self):
    self._test_property_existence('destination_reference',
        'Property existence error for property destination_reference, this document'
        ' has no such property or the property has never been set')

  def test_property_existence_source_reference(self):
    property_id = 'source_reference'
    consistency_message = 'Property existence error for property '\
        'source_reference, this document has no such property or the property '\
        'has never been set'
    # not required in draft state
    self.software_instance.edit(**{property_id:None})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(**{property_id:''})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

    self.portal.portal_workflow._jumpToStateFor(self.software_instance,
        'start_requested')
    self._test_property_existence(property_id, consistency_message)

  def test_property_existence_reference(self):
    self._test_property_existence('reference',
        'Property existence error for property reference, this document'
        ' has no such property or the property has never been set')

  def test_property_existence_ssl_certificate(self):
    property_id = 'ssl_certificate'
    consistency_message = 'Property existence error for property '\
        'ssl_certificate, this document has no such property or the property'\
        ' has never been set'
    self._test_property_existence(property_id, consistency_message)
    # not required in destroy_requested state
    self.portal.portal_workflow._jumpToStateFor(self.software_instance,
        'destroy_requested')
    self.software_instance.edit(**{property_id:None})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(**{property_id:''})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

  def test_property_existence_ssl_key(self):
    property_id = 'ssl_key'
    consistency_message = 'Property existence error for property '\
        'ssl_key, this document has no such property or the property'\
        ' has never been set'
    self._test_property_existence(property_id, consistency_message)
    # not required in destroy_requested state
    self.portal.portal_workflow._jumpToStateFor(self.software_instance,
        'destroy_requested')
    self.software_instance.edit(**{property_id:None})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(**{property_id:''})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

  def test_predecessor_related(self):
    software_instance2 = self.portal.software_instance_module.newContent(
      portal_type='Software Instance')
    software_instance3 = self.portal.software_instance_module.newContent(
      portal_type='Software Instance')

    # fetch basic list of consistency messages
    current_message_list = getMessageList(self.software_instance)

    consistency_message = "There is more then one related predecessor"

    # test the test: no expected message found
    self.assertFalse(consistency_message in current_message_list)

    # if too many, it shall cry
    software_instance2.edit(predecessor=self.software_instance.getRelativeUrl())
    software_instance3.edit(predecessor=self.software_instance.getRelativeUrl())
    self.tic()
    self.assertTrue(consistency_message in getMessageList(self.software_instance))

    # one is good
    software_instance2.edit(predecessor=None)
    self.tic()
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

    # none is good
    software_instance3.edit(predecessor=None)
    self.tic()
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

  def test_setup_packing_list(self):
    raise NotImplementedError('It requires not migrated resources')

  def test_sla_xml(self):
    # fetch basic list of consistency messages
    current_message_list = getMessageList(self.software_instance)

    consistency_message = "Sla XML is invalid: Start tag expected, '<' not "\
        "found, line 1, column 1"

    # test the test: no expected message found
    self.assertFalse(consistency_message in current_message_list)


    # sla_xml is optional
    self.software_instance.edit(sla_xml=None)
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

    self.software_instance.edit(sla_xml='')
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

    # if available shall be correct XML
    self.software_instance.edit(sla_xml='this is bad xml')
    self.assertTrue(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(sla_xml=self.generateEmptyXml())
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

  def test_text_content(self):
    # fetch basic list of consistency messages
    current_message_list = getMessageList(self.software_instance)

    consistency_message = "Instance XML is invalid: Start tag expected, '<' not "\
        "found, line 1, column 1"

    # test the test: no expected message found
    self.assertFalse(consistency_message in current_message_list)


    # text_content is optional
    self.software_instance.edit(text_content=None)
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

    self.software_instance.edit(text_content='')
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

    # if available shall be correct XML
    self.software_instance.edit(text_content='this is bad xml')
    self.assertTrue(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(text_content=self.generateEmptyXml())
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

class TestSlapOSSlaveInstanceConstraint(TestSlapOSConstraintMixin):
  def afterSetUp(self):
    self.software_instance = self.portal.software_instance_module.newContent(
      portal_type='Slave Instance')

  def beforeTearDown(self):
    transaction.abort()

  def test_property_existence_source_reference(self):
    consistency_message = 'Property existence error for property '\
        'source_reference, this document has no such property '\
        'or the property has never been set'
    property_id = 'source_reference'
    # not required in draft state
    self.software_instance.edit(**{property_id:None})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(**{property_id:''})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

    self.portal.portal_workflow._jumpToStateFor(self.software_instance,
        'start_requested')
    self._test_property_existence(property_id, consistency_message)

  def test_property_existence_text_content(self):
    consistency_message = 'Property existence error for property '\
        'text_content, this document has no such property '\
        'or the property has never been set'
    property_id = 'text_content'
    # not required in draft state
    self.software_instance.edit(**{property_id:None})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

    self.software_instance.edit(**{property_id:''})
    self.assertFalse(consistency_message in getMessageList(self.software_instance))

    self.portal.portal_workflow._jumpToStateFor(self.software_instance,
        'start_requested')
    self._test_property_existence(property_id, consistency_message)

  def test_property_existence_reference(self):
    self._test_property_existence('reference',
        'Property existence error for property reference, this document'
        ' has no such property or the property has never been set')

  def test_property_existence_destination_reference(self):
    self._test_property_existence('destination_reference',
        'Property existence error for property destination_reference, '
        'this document has no such property or the property has never '
        'been set')

  def test_predecessor_related(self):
    software_instance2 = self.portal.software_instance_module.newContent(
      portal_type='Slave Instance')
    software_instance3 = self.portal.software_instance_module.newContent(
      portal_type='Slave Instance')

    # fetch basic list of consistency messages
    current_message_list = getMessageList(self.software_instance)

    consistency_message = "There is more then one related predecessor"

    # test the test: no expected message found
    self.assertFalse(consistency_message in current_message_list)

    # if too many, it shall cry
    software_instance2.edit(predecessor=self.software_instance.getRelativeUrl())
    software_instance3.edit(predecessor=self.software_instance.getRelativeUrl())
    self.tic()
    self.assertTrue(consistency_message in getMessageList(self.software_instance))

    # one is good
    software_instance2.edit(predecessor=None)
    self.tic()
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

    # none is good
    software_instance3.edit(predecessor=None)
    self.tic()
    self.assertFalse(consistency_message in getMessageList(self.software_instance))
    self.assertSameSet(current_message_list, getMessageList(self.software_instance))

  def test_setup_packing_list(self):
    raise NotImplementedError('It requires not migrated resources')
