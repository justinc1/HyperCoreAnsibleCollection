#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_export

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Plugin handles export of the virtual machine.
description:
  - Plugin enables export of the virtual machine, to a specified location.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  vm_name:
    description:
      - Virtual machine name.
      - Used to identify selected virtual machine by name.
    type: str
    required: true
  smb:
    description:
      - SMB server, access and location data.
      - Destination, username, password
    type: dict
    required: true
    suboptions:
      server:
        type: str
        description:
          - Specified SMB server, where the selected virtual machine is to be exported to.
          - Has to be IP or DNS name.
        required: true
      path:
        type: str
        description:
          - Specified location on the SMB server, where the exported virtual machine is to be exported to.
        required: true
      username:
        type: str
        description:
          - Username.
        required: true
      password:
        type: str
        description:
          - Password.
        required: true
"""

EXAMPLES = r"""
- name: Export VM to SMB
  scale_computing.hypercore.vm_export:
    vm_name: demo-vm
    smb:
      server: IP-or-DNS-name-of-SMB-server
      path: /share/path/to/vms/demo-vm-exported-v0
      username: user
      password: pass
  register: output
"""

RETURN = r"""
msg:
  description:
    - Return message.
  returned: success
  type: str
  sample: Virtual machine - VM-TEST - export complete to - SMB-TEST
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.task_tag import TaskTag


def run(module, rest_client):
    virtual_machine_obj = VM.get_or_fail(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )[0]
    task = virtual_machine_obj.export_vm(rest_client, module.params)
    TaskTag.wait_task(rest_client, task)
    return True, "Virtual machine - {0} - export complete to - {1}".format(
        module.params["vm_name"], module.params["smb"]["server"]
    )


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            smb=dict(
                type="dict",
                required=True,
                options=dict(
                    server=dict(
                        type="str",
                        required=True,
                    ),
                    path=dict(
                        type="str",
                        required=True,
                    ),
                    username=dict(
                        type="str",
                        required=True,
                    ),
                    password=dict(
                        type="str",
                        no_log=True,
                        required=True,
                    ),
                ),
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        rest_client = RestClient(client=client)
        changed, msg = run(module, rest_client)
        module.exit_json(changed=changed, msg=msg)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
