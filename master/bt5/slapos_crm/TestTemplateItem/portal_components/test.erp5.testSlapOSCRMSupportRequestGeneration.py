# -*- coding:utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2013 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
#
##############################################################################

import transaction
from Products.SlapOS.tests.testSlapOSMixin import \
  testSlapOSMixin
from Products.ERP5Type.tests.utils import createZODBPythonScript
import json
from DateTime import DateTime

class TestSlapOSCloudSupportRequestGeneration(testSlapOSMixin):

  def afterSetUp(self):
    super(TestSlapOSCloudSupportRequestGeneration, self).afterSetUp()
    self.new_id = self.generateNewId()
    self._cancelTestSupportRequestList()
    self.portal.REQUEST.set("support_request_in_progress", None)

  def _cancelTestSupportRequestList(self):
    for support_request in self.portal.portal_catalog(
                        portal_type="Support Request",
                        title="%Test Support Request %",
                        simulation_state=["validated", "suspended"]):
      support_request.invalidate()
    self.tic()
    
  def _updatePersonAssignment(self, person, role='role/member'):
    for assignment in person.contentValues(portal_type="Assignment"):
      assignment.cancel()
    assignment = person.newContent(portal_type='Assignment')
    assignment.setRole(role)
    assignment.setStartDate(DateTime())
    assignment.open()
    return assignment
  
  def _makePerson(self, new_id):
    # Clone computer document
    person = self.portal.person_module.template_member\
         .Base_createCloneDocument(batch_mode=1)
    person.edit(reference='TESTPERSON-%s' % (new_id, ))
    person.immediateReindexObject()
    return person
    
  def _makeSupportRequest(self, new_id):
    
    support_request = self.portal.\
      support_request_module.\
      slapos_crm_support_request_template_for_monitoring.\
       Base_createCloneDocument(batch_mode=1)
    return support_request

  def _makeComputer(self,new_id):
    # Clone computer document
    person = self.portal.person_module.template_member\
         .Base_createCloneDocument(batch_mode=1)
    computer = self.portal.computer_module\
      .template_computer.Base_createCloneDocument(batch_mode=1)
    computer.edit(
      title="computer ticket %s" % (new_id, ),
      reference="TESTCOMPT-%s" % (new_id, ),
      source_administration_value=person
    )
    computer.validate()

    return computer
    
  def _makeComputerPartitions(self,computer):
    for i in range(1, 5):
      id_ = 'partition%s' % (i, )
      p = computer.newContent(portal_type='Computer Partition',
        id=id_,
        title=id_,
        reference=id_,
        default_network_address_ip_address='ip_address_%s' % i,
        default_network_address_netmask='netmask_%s' % i)
      p.markFree()
      p.validate()

  def _makeSoftwareRelease(self, new_id, software_release_url=None):
    software_release = self.portal.software_release_module\
      .template_software_release.Base_createCloneDocument(batch_mode=1)
    software_release.edit(
      url_string=software_release_url or self.generateNewSoftwareReleaseUrl(),
      reference='TESTSOFTRELS-%s' % new_id,
      title='Start requested for %s' % new_id
    )
    software_release.release()

    return software_release

  def _makeSoftwareInstallation(self, new_id, computer, software_release_url):
     software_installation = self.portal\
       .software_installation_module.template_software_installation\
       .Base_createCloneDocument(batch_mode=1)
     software_installation.edit(
       url_string=software_release_url,
       aggregate=computer.getRelativeUrl(),
       reference='TESTSOFTINSTS-%s' % new_id,
       title='Start requested for %s' % computer.getUid()
     )
     software_installation.validate()
     software_installation.requestStart()

     return software_installation

  def _makeHostingSubscription(self, new_id):
    person = self.portal.person_module.template_member\
         .Base_createCloneDocument(batch_mode=1)
    hosting_subscription = self.portal\
      .hosting_subscription_module.template_hosting_subscription\
      .Base_createCloneDocument(batch_mode=1)
    hosting_subscription.validate()
    hosting_subscription.edit(
        title= "Test hosting sub ticket %s" % new_id,
        reference="TESTHST-%s" % new_id,
        destination_section_value=person
    )

    return hosting_subscription

  def _makeSoftwareInstance(self, hosting_subscription, software_url):

    kw = dict(
      software_release=software_url,
      software_type=self.generateNewSoftwareType(),
      instance_xml=self.generateSafeXml(),
      sla_xml=self.generateSafeXml(),
      shared=False,
      software_title=hosting_subscription.getTitle(),
      state='started'
    )
    hosting_subscription.requestStart(**kw)
    hosting_subscription.requestInstance(**kw)

  def test_computer_Base_generateSupportRequestForSlapOS(self):
    self._dropBase_generateSupportRequestForSlapOS()
    title = "Test Support Request %s" % self.new_id
    computer = self._makeComputer(self.new_id)
    support_request = computer.Base_generateSupportRequestForSlapOS(
      title, title, computer.getRelativeUrl()
    )
    self.tic()

    self.assertNotEqual(support_request, None)

    # The support request is added to computer owner.
    self.assertEquals(support_request.getDestinationDecision(),
                      computer.getSourceAdministration())

  def test_software_instance_Base_generateSupportRequestForSlapOS(self):
    host_sub = self._makeHostingSubscription(self.new_id)
    self._makeSoftwareInstance(host_sub,self.generateNewSoftwareReleaseUrl())
    instance = host_sub.getPredecessorValue()

    title = "Test Support Request %s" % self.new_id
    support_request = instance.Base_generateSupportRequestForSlapOS(
      title, title, instance.getRelativeUrl()
    )
    self.tic()

    self.assertNotEqual(support_request, None)

    # The support request is added to computer owner.
    self.assertEquals(support_request.getDestinationDecision(),
                      host_sub.getDestinationSection())
  
  def test_hosting_subscription_Base_generateSupportRequestForSlapOS(self):
    host_sub = self._makeHostingSubscription(self.new_id)

    title = "Test Support Request %s" % self.new_id
    support_request = host_sub.Base_generateSupportRequestForSlapOS(
      title, title, host_sub.getRelativeUrl()
    )
    self.tic()

    self.assertNotEqual(support_request, None)

    # The support request is added to computer owner.
    self.assertEquals(support_request.getDestinationDecision(),
                      host_sub.getDestinationSection())

  def test_Base_generateSupportRequestForSlapOS_do_not_recreate_if_open(self):
    title = "Test Support Request %s" % self.new_id
    computer = self._makeComputer(self.new_id)
    support_request = computer.Base_generateSupportRequestForSlapOS(
      title, title, computer.getRelativeUrl()
    )
    self.tic()
    self.portal.REQUEST.set("support_request_in_progress", None)

    same_support_request = computer.Base_generateSupportRequestForSlapOS(
      title, title, computer.getRelativeUrl()
    )
    
    self.assertEqual(support_request, same_support_request)


  def test_Base_generateSupportRequestForSlapOS_do_not_recreate_if_suspended(self):
    title = "Test Support Request %s" % self.new_id
    computer = self._makeComputer(self.new_id)
    support_request = computer.Base_generateSupportRequestForSlapOS(
      title, title, computer.getRelativeUrl()
    )
    
    support_request.suspend()
    self.tic()
    self.portal.REQUEST.set("support_request_in_progress", None)

    same_support_request = computer.Base_generateSupportRequestForSlapOS(
      title, title, computer.getRelativeUrl()
    )
    
    self.assertEqual(support_request, same_support_request)



  def test_ERP5Site_isSupportRequestCreationClosed(self):
    
    person = self._makePerson(self.new_id)
    other_person = self._makePerson('other-%s' % self.new_id)
    url = person.getRelativeUrl()
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed(url))
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed())

    def newSupportRequest():
      sr = self.portal.support_request_module.newContent(\
                        title="Test Support Request POIUY",
                        destination_decision=url)
      sr.validate()
      sr.immediateReindexObject()

    newSupportRequest()
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed(url))
    newSupportRequest()
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed(url))
    newSupportRequest()
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed(url))
    newSupportRequest()
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed(url))
    newSupportRequest()
    self.assertTrue(self.portal.ERP5Site_isSupportRequestCreationClosed(url))
    
    self.assertTrue(self.portal.ERP5Site_isSupportRequestCreationClosed())
    
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed(
                     other_person.getRelativeUrl()))
  
  def test_ERP5Site_isSupportRequestCreationClosed_submitted_state(self):
    person = self._makePerson(self.new_id)
    url = person.getRelativeUrl()
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed(url))
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed())
    
    def newSupportRequest():
      sr = self.portal.support_request_module.newContent(\
                        title="Test Support Request POIUY",
                        destination_decision=url)
      sr.validate()
      sr.suspend()
      sr.immediateReindexObject()
    # Create five tickets, the limit of ticket creation
    newSupportRequest()
    newSupportRequest()
    newSupportRequest()
    newSupportRequest()
    newSupportRequest()
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed(url))
    self.assertFalse(self.portal.ERP5Site_isSupportRequestCreationClosed())
    

  def test_Base_generateSupportRequestForSlapOS_recreate_if_closed(self):
    title = "Test Support Request %s" % self.new_id
    computer = self._makeComputer(self.new_id)
    support_request = computer.Base_generateSupportRequestForSlapOS(
      title, title, computer.getRelativeUrl()
    )
    self.tic()

    support_request.invalidate()
    self.tic()
    
    self.portal.REQUEST.set("support_request_in_progress", None)

    support_request = computer.Base_generateSupportRequestForSlapOS(
      title, title, computer.getRelativeUrl()
    )
    self.tic()

    self.assertNotEqual(support_request,None)

  def test_Base_generateSupportRequestForSlapOS_recreate(self):
    title = "Test Support Request %s" % self.new_id
    computer = self._makeComputer(self.new_id)
    support_request = computer.Base_generateSupportRequestForSlapOS(
      title, title, computer.getRelativeUrl()
    )

    same_support_request = computer.Base_generateSupportRequestForSlapOS(
      title, title, computer.getRelativeUrl()
    )
    
    self.assertEqual(support_request, same_support_request)

  def _simulateBase_generateSupportRequestForSlapOS(self):
    script_name = 'Base_generateSupportRequestForSlapOS'
    if script_name in self.portal.portal_skins.custom.objectIds():
      raise ValueError('Precondition failed: %s exists in custom' % script_name)
    createZODBPythonScript(self.portal.portal_skins.custom,
      script_name,
      '*args, **kw',
      '# Script body\n'
"""return context.getPortalObject().REQUEST['_simulateBase_generateSupportRequestForSlapOS']""")
    transaction.commit()

  def _dropBase_generateSupportRequestForSlapOS(self):
    script_name = 'Base_generateSupportRequestForSlapOS'
    if script_name in self.portal.portal_skins.custom.objectIds():
      self.portal.portal_skins.custom.manage_delObjects(script_name)
    transaction.commit()
    self.assertFalse(script_name in self.portal.portal_skins.custom.objectIds())

  def test_Computer_checkState(self):
    computer = self._makeComputer(self.new_id)
    memcached_dict = self.portal.portal_memcached.getMemcachedDict(
      key_prefix='slap_tool',
      plugin_path='portal_memcached/default_memcached_plugin')

    memcached_dict[computer.getReference()] = json.dumps(
        {"created_at":"%s" % (DateTime() - 1.1)}
    )
    
    support_request = self._makeSupportRequest(self.new_id)
    self.portal.REQUEST.set('_simulateBase_generateSupportRequestForSlapOS', 
                               support_request)

    self._simulateBase_generateSupportRequestForSlapOS()

    try:
      computer_support_request = computer.Computer_checkState()
    finally:
      self._dropBase_generateSupportRequestForSlapOS()

    self.assertEqual(support_request,
      computer_support_request)

  def test_Computer_checkState_empty_cache(self):
    computer = self._makeComputer(self.new_id)

    support_request = self._makeSupportRequest(self.new_id)
    self.portal.REQUEST.set('_simulateBase_generateSupportRequestForSlapOS', 
                               support_request)

    self._simulateBase_generateSupportRequestForSlapOS()

    try:
      computer_support_request = computer.Computer_checkState()
    finally:
      self._dropBase_generateSupportRequestForSlapOS()

    self.assertEqual(support_request,
      computer_support_request)

  def test_SupportRequest_trySendNotificationMessage(self):
    computer = self._makeComputer(self.new_id)
    person = computer.getSourceAdministrationValue()
    title = "Test Support Request %s" % self.new_id
    text_content='Test NM content<br/>%s<br/>' % self.new_id
    
    support_request = self.portal.support_request_module.newContent(\
            title=title, description=title,
            destination_decision=computer.getSourceAdministration(),
            source_project_value=computer.getRelativeUrl())
    support_request.validate()
    self.tic()
    
    first_event = support_request.SupportRequest_trySendNotificationMessage(
      message_title=title, message=text_content,
      source_relative_url=person.getRelativeUrl()
    )
    self.assertNotEqual(first_event, None)
    
    first_event.edit(start_date=(DateTime() - 1.8))
    self.tic()
    
    event = support_request.SupportRequest_trySendNotificationMessage(
      message_title=title, message=text_content,
      source_relative_url=person.getRelativeUrl()
    )
    self.assertEqual(event, None)
    
    title += "__zz"
    event = support_request.SupportRequest_trySendNotificationMessage(
      message_title=title, message=text_content,
      source_relative_url=person.getRelativeUrl(),
    )
    
    self.assertEqual(event.getTitle(), title)

  def test_SoftwareInstance_hasReportedError(self):
    host_sub = self._makeHostingSubscription(self.new_id)
    self._makeSoftwareInstance(host_sub,self.generateNewSoftwareReleaseUrl())
    instance = host_sub.getPredecessorValue()

    computer = self._makeComputer(self.new_id)
    self._makeComputerPartitions(computer)
    
    memcached_dict = self.portal.portal_memcached.getMemcachedDict(
      key_prefix='slap_tool',
      plugin_path='portal_memcached/default_memcached_plugin')

    error_date = DateTime()
    memcached_dict[instance.getReference()] = json.dumps(
        {"created_at":"%s" % error_date, "text": "#error "}
    )
    
    self.assertEquals(instance.SoftwareInstance_hasReportedError(), None)

    instance.setAggregateValue(computer.partition1)
    
    self.assertEquals(instance.SoftwareInstance_hasReportedError(), error_date)

    memcached_dict[instance.getReference()] = json.dumps(
        {"created_at":"%s" % error_date, "text": "#access "}
    )
    
    self.assertEquals(instance.SoftwareInstance_hasReportedError(), None)


  def test_SoftwareInstallation_hasReportedError(self):
    software_release = self._makeSoftwareRelease(self.new_id)
    computer = self._makeComputer(self.new_id)
    installation = self._makeSoftwareInstallation(
      self.new_id, computer, software_release.getUrlString()
    )

    memcached_dict = self.portal.portal_memcached.getMemcachedDict(
      key_prefix='slap_tool',
      plugin_path='portal_memcached/default_memcached_plugin')

    self.assertEquals(installation.SoftwareInstance_hasReportedError(), None)

    error_date = DateTime()
    memcached_dict[installation.getReference()] = json.dumps(
        {"created_at":"%s" % error_date, "text": "#error "}
    )

    self.assertEquals(installation.SoftwareInstallation_hasReportedError(), error_date)
    
    memcached_dict[installation.getReference()] = json.dumps(
        {"created_at":"%s" % error_date, "text": "#building "}
     )
    
    self.assertEquals(installation.SoftwareInstallation_hasReportedError(), None)
