# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils.utils import get_query


class ISO(PayloadMapper):
    # Variables in ISO are written in ansible-native format
    def __init__(
        self,
        name,
        uuid=None,
        size=-1,
        mounts=None,
        ready_for_insert=False,
    ):
        if mounts is None:
            mounts = []
        self.uuid = uuid
        self.name = name
        self.size = size
        # mounts represent list of dicts with vm_uuid and vm_name as keys and their values as values
        self.mounts = mounts
        self.ready_for_insert = ready_for_insert

    @classmethod
    def from_ansible(cls, vm_dict):
        # name is always going to be present when this method is used. The rest of the fields are assigned distinct
        # default values when retrieving values from the vm_dict.
        return ISO(
            name=vm_dict["name"],
            size=vm_dict.get("size", -1),
        )

    @classmethod
    def from_hypercore(cls, vm_dict):
        if not vm_dict:  # In case for get_record, return None if no result is found
            return None
        return ISO(
            uuid=vm_dict["uuid"],
            name=vm_dict["name"],
            size=vm_dict["size"],
            mounts=[
                dict(vm_uuid=mount["vmUUID"], vm_name=mount["vmName"])
                for mount in vm_dict["mounts"]
            ],
            ready_for_insert=vm_dict["readyForInsert"],
        )

    def to_hypercore(self):
        return dict(
            uuid=self.uuid,
            name=self.name,
            size=self.size,
            readyForInsert=self.ready_for_insert,
        )

    def to_ansible(self):
        return dict(
            uuid=self.uuid,
            name=self.name,
            size=self.size,
            mounts=self.mounts,
            ready_for_insert=self.ready_for_insert,
        )

    def __eq__(self, other):
        """
        One ISO is equal to another if it has ALL attributes exactly the same.
        Since uuid, path and mounts are compared too, ISO created from ansible playbook data and
        ISO created from HC3 API response will never be same.
        This method is used only in tests.
        """
        return all(
            (
                self.uuid == other.uuid,
                self.name == other.name,
                self.size == other.size,
                self.mounts == other.mounts,
                self.ready_for_insert == other.ready_for_insert,
            )
        )

    def __str__(self):
        return super().__str__()

    def build_iso_post_paylaod(self):
        return {
            key: value
            for key, value in self.to_hypercore().items()
            if key in ("name", "size", "readyForInsert")
        }

    @classmethod
    def get_by_name(cls, ansible_dict, rest_client):
        """
        With given dict from playbook, finds the existing iso by name from the HyperCore api and constructs object ISO if
        the record exists. If there is no record with such name, None is returned.
        """
        query = get_query(ansible_dict, "name", ansible_hypercore_map=dict(name="name"))
        hypercore_dict = rest_client.get_record("/rest/v1/ISO", query, must_exist=False)
        iso_from_hypercore = ISO.from_hypercore(hypercore_dict)
        return iso_from_hypercore
