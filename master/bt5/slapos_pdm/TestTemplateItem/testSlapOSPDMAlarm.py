# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
import transaction
from Products.SlapOS.tests.testSlapOSMixin import \
  testSlapOSMixin
from Products.ERP5Type.tests.utils import createZODBPythonScript

class TestSlapOSUpgradeDecisionProcess(testSlapOSMixin):
  def afterSetUp(self):
    super(TestSlapOSUpgradeDecisionProcess, self).afterSetUp()
    self.new_id = self.generateNewId()

  def generateNewId(self):
     return "%sTEST" % self.portal.portal_ids.generateNewId(
         id_group=('slapos_core_test'))

  def _makeUpgradeDecision(self):
    upgrade_decision = self.portal.\
       upgrade_decision_module.newContent(
         portal_type="Upgrade Decision", 
         title="TESTUPDE-%s" % self.new_id)
    upgrade_decision.confirm()
    return upgrade_decision
  
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
    
  def _simulateUpgradeDecision_upgradeHostingSubscription(self, fake_return="True"):
    self._simulateScript('UpgradeDecision_upgradeHostingSubscription', fake_return)
    
  def _simulateUpgradeDecision_upgradeComputer(self, fake_return="True"):
    self._simulateScript('UpgradeDecision_upgradeComputer', fake_return)

  def _simulateScript(self, script_name, fake_return):
    if script_name in self.portal.portal_skins.custom.objectIds():
      raise ValueError('Precondition failed: %s exists in custom' % script_name)
    createZODBPythonScript(self.portal.portal_skins.custom,
                        script_name,
                        '*args, **kwargs',
                        '# Script body\n'
"""portal_workflow = context.portal_workflow
portal_workflow.doActionFor(context, action='edit_action', comment='Visited by %s') 
return %s
""" % (script_name, fake_return ))
    transaction.commit()

  def _dropUpgradeDecision_upgradeHostingSubscription(self):
    self._dropScript('UpgradeDecision_upgradeHostingSubscription')

  def _dropUpgradeDecision_upgradeComputer(self):
    self._dropScript('UpgradeDecision_upgradeComputer')

  def _dropScript(self, script_name):
    if script_name in self.portal.portal_skins.custom.objectIds():
      self.portal.portal_skins.custom.manage_delObjects(script_name)
    transaction.commit()

  def test_alarm_upgrade_decision_process_hosting_subscription(self):
    upgrade_decision = self._makeUpgradeDecision()
    upgrade_decision.start()
    self.tic()
    
    self._simulateUpgradeDecision_upgradeHostingSubscription()
    try:
      self.portal.portal_alarms.slapos_upgrade_decision_process.activeSense()
      self.tic()
    finally:
      self._dropUpgradeDecision_upgradeHostingSubscription()
    self.assertEqual(
        'Visited by UpgradeDecision_upgradeHostingSubscription', 
        upgrade_decision.workflow_history['edit_workflow'][-1]['comment'])

  def test_alarm_upgrade_decision_process_computer(self):
    upgrade_decision = self._makeUpgradeDecision()
    upgrade_decision.start()
    self.tic()
    
    self._simulateUpgradeDecision_upgradeHostingSubscription("False")
    self._simulateUpgradeDecision_upgradeComputer()
    try:
      self.portal.portal_alarms.slapos_upgrade_decision_process.activeSense()
      self.tic()
    finally:
      self._dropUpgradeDecision_upgradeHostingSubscription()
      self._dropUpgradeDecision_upgradeComputer()
    self.assertEqual(
        'Visited by UpgradeDecision_upgradeComputer', 
        upgrade_decision.workflow_history['edit_workflow'][-1]['comment'])
  
  
  def _simulateComputer_checkAndCreateUpgradeDecision(self):
    script_name = 'Computer_checkAndCreateUpgradeDecision'
    if script_name in self.portal.portal_skins.custom.objectIds():
      raise ValueError('Precondition failed: %s exists in custom' % script_name)
    createZODBPythonScript(self.portal.portal_skins.custom,
      script_name,
      '*args, **kw',
      '# Script body\n'
"""portal_workflow = context.portal_workflow
portal_workflow.doActionFor(context, action='edit_action', comment='%s') """ % \
      'Visited by Computer_checkAndCreateUpgradeDecision')
    transaction.commit()

  def _dropComputer_checkAndCreateUpgradeDecision(self):
    script_name = 'Computer_checkAndCreateUpgradeDecision'
    if script_name in self.portal.portal_skins.custom.objectIds():
      self.portal.portal_skins.custom.manage_delObjects(script_name)
    transaction.commit()
  
  def test_Alarm_computerCheckUpgradeSoftwareRelease(self):
    computer = self._makeComputer(self.new_id)
    computer.edit(allocation_scope = 'open/public')
    computer2 = self._makeComputer(self.generateNewId())
    computer2.edit(allocation_scope = 'open/personal')
    
    self._simulateComputer_checkAndCreateUpgradeDecision()

    try:
      self.portal.portal_alarms.slapos_pdm_computer_create_upgrade_decision.\
        activeSense()
      self.tic()
    finally:
      self._dropComputer_checkAndCreateUpgradeDecision()

    self.assertEqual('Visited by Computer_checkAndCreateUpgradeDecision',
      computer.workflow_history['edit_workflow'][-1]['comment'])
    
    self.assertNotEqual('Visited by Computer_checkAndCreateUpgradeDecision',
      computer2.workflow_history['edit_workflow'][-1]['comment'])
  
  def _simulateComputer_hostingSubscriptionCreateUpgradeDecision(self):
    script_name = 'Computer_hostingSubscriptionCreateUpgradeDecision'
    if script_name in self.portal.portal_skins.custom.objectIds():
      raise ValueError('Precondition failed: %s exists in custom' % script_name)
    createZODBPythonScript(self.portal.portal_skins.custom,
      script_name,
      '*args, **kw',
      '# Script body\n'
"""portal_workflow = context.portal_workflow
portal_workflow.doActionFor(context, action='edit_action', comment='%s') """ % \
      'Visited by Computer_hostingSubscriptionCreateUpgradeDecision')
    transaction.commit()

  def _dropComputer_hostingSubscriptionCreateUpgradeDecision(self):
    script_name = 'Computer_hostingSubscriptionCreateUpgradeDecision'
    if script_name in self.portal.portal_skins.custom.objectIds():
      self.portal.portal_skins.custom.manage_delObjects(script_name)
    transaction.commit()
  
  def test_Alarm_computerCheckUpgradeHostingSubscription(self):
    computer = self._makeComputer(self.new_id)
    computer.edit(allocation_scope = 'open/public')
    computer2 = self._makeComputer(self.generateNewId())
    computer2.edit(allocation_scope = 'open/personal')
    
    self._simulateComputer_hostingSubscriptionCreateUpgradeDecision()

    try:
      self.portal.portal_alarms.slapos_hosting_subscription_create_upgrade_decision.\
        activeSense()
      self.tic()
    finally:
      self._dropComputer_hostingSubscriptionCreateUpgradeDecision()

    self.assertEqual('Visited by Computer_hostingSubscriptionCreateUpgradeDecision',
      computer.workflow_history['edit_workflow'][-1]['comment'])
    
    self.assertNotEqual('Visited by Computer_hostingSubscriptionCreateUpgradeDecision',
      computer2.workflow_history['edit_workflow'][-1]['comment'])
      
      