# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
from Products.SlapOS.tests.testSlapOSMixin import \
  testSlapOSMixin
import transaction

class TestSlapOSAccountingInteractionWorkflow(testSlapOSMixin):
  def beforeTearDown(self):
    transaction.abort()

  def test_SlaveInstance_changePromise(self):
    new_id = self.generateNewId()
    instance = self.portal.software_instance_module.newContent(
      portal_type='Slave Instance',
      title="Instance %s" % new_id,
      reference="TESTINST-%s" % new_id,
      destination_reference="TESTINST-%s" % new_id,
      )
    instance.validate()

    self.assertEqual(instance.getCausalityState(), 'diverged')

    request_kw = dict(
      software_release='http://example.org',
      software_type='http://example.org',
      instance_xml=self.generateSafeXml(),
      sla_xml=self.generateSafeXml(),
      shared=True,
    )

    instance.converge()
    self.assertEqual(instance.getCausalityState(), 'solved')
    instance.requestStop(**request_kw)
    self.assertEqual(instance.getCausalityState(), 'diverged')

    instance.converge()
    self.assertEqual(instance.getCausalityState(), 'solved')
    instance.requestStart(**request_kw)
    self.assertEqual(instance.getCausalityState(), 'diverged')

    instance.converge()
    self.assertEqual(instance.getCausalityState(), 'solved')
    instance.bang(comment='Test bang interaction', bang_tree=False)
    self.assertEqual(instance.getCausalityState(), 'diverged')

    instance.converge()
    self.assertEqual(instance.getCausalityState(), 'solved')
    instance.requestDestroy(**request_kw)
    self.assertEqual(instance.getCausalityState(), 'diverged')

  def test_SlaveInstance_changePromiseInDivergeState(self):
    new_id = self.generateNewId()
    instance = self.portal.software_instance_module.newContent(
      portal_type='Slave Instance',
      title="Instance %s" % new_id,
      reference="TESTINST-%s" % new_id,
      destination_reference="TESTINST-%s" % new_id,
      )
    instance.validate()

    self.assertEqual(instance.getCausalityState(), 'diverged')

    request_kw = dict(
      software_release='http://example.org',
      software_type='http://example.org',
      instance_xml=self.generateSafeXml(),
      sla_xml=self.generateSafeXml(),
      shared=True,
    )

    instance.requestStop(**request_kw)
    self.assertEqual(instance.getCausalityState(), 'diverged')

  def test_SoftwareInstance_changePromise(self):
    new_id = self.generateNewId()
    instance = self.portal.software_instance_module.newContent(
      portal_type='Software Instance',
      title="Instance %s" % new_id,
      reference="TESTINST-%s" % new_id,
      destination_reference="TESTINST-%s" % new_id,
      ssl_certificate="foo",
      ssl_key="bar",
      )
    instance.validate()

    self.assertEqual(instance.getCausalityState(), 'diverged')

    request_kw = dict(
      software_release='http://example.org',
      software_type='http://example.org',
      instance_xml=self.generateSafeXml(),
      sla_xml=self.generateSafeXml(),
      shared=False,
    )

    instance.converge()
    self.assertEqual(instance.getCausalityState(), 'solved')
    instance.requestStop(**request_kw)
    self.assertEqual(instance.getCausalityState(), 'diverged')

    instance.converge()
    self.assertEqual(instance.getCausalityState(), 'solved')
    instance.requestStart(**request_kw)
    self.assertEqual(instance.getCausalityState(), 'diverged')

    instance.converge()
    self.assertEqual(instance.getCausalityState(), 'solved')
    instance.bang(comment='Test bang interaction', bang_tree=False)
    self.assertEqual(instance.getCausalityState(), 'diverged')

    instance.converge()
    self.assertEqual(instance.getCausalityState(), 'solved')
    instance.requestDestroy(**request_kw)
    self.assertEqual(instance.getCausalityState(), 'diverged')

  def test_SoftwareInstance_changePromiseInDivergedState(self):
    new_id = self.generateNewId()
    instance = self.portal.software_instance_module.newContent(
      portal_type='Software Instance',
      title="Instance %s" % new_id,
      reference="TESTINST-%s" % new_id,
      destination_reference="TESTINST-%s" % new_id,
      ssl_certificate="foo",
      ssl_key="bar",
      )
    instance.validate()

    self.assertEqual(instance.getCausalityState(), 'diverged')

    request_kw = dict(
      software_release='http://example.org',
      software_type='http://example.org',
      instance_xml=self.generateSafeXml(),
      sla_xml=self.generateSafeXml(),
      shared=False,
    )

    instance.requestStop(**request_kw)
    self.assertEqual(instance.getCausalityState(), 'diverged')