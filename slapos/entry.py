# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import sys
from register.register import main as node_register


def main():
  if len(sys.argv) < 3:
    print "Usage: slapos node register NODE_NAME [options]"
    print "%s: error: Incorrect number of arguments" % sys.argv[0] 
    return 0
  "Run default configuration."
  if sys.argv[1] == "node" and sys.argv[2] == "register":
    sys.argv=sys.argv[2:]
    node_register()
  else :
    print "Usage: slapos node register NODE_NAME [options]"
    print "%s: error: Incorrect arguments" % sys.argv[0] 