#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.common.utils import to_list
from ansible.module_utils.network.common.config import NetworkConfig
from ansible.module_utils.network.your_switch_vendor.your_switch_platform import (
    get_switch_connection,
    vlan_config,
)

def main():
    argument_spec = dict(
        vlan_id=dict(type='int', required=True),
        vlan_name=dict(type='str'),
        state=dict(default='present', choices=['present', 'absent']),
        interfaces=dict(type='list', elements='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True  # Add check mode support if possible
    )

    vlan_id = module.params['vlan_id']
    vlan_name = module.params['vlan_name']
    state = module.params['state']
    interfaces = to_list(module.params['interfaces'])  # Ensure it's a list

    connection = get_switch_connection(module)  # Replace with your connection logic

    try:
        config = NetworkConfig(indent=2, contents=connection.get_config())
    except Exception as e:
        module.fail_json(msg=f"Error getting switch config: {e}")

    changes = []
    if state == 'present':
        if not vlan_config(config, vlan_id, vlan_name):
            changes.append('VLAN created')
        if interfaces:
            if not connection.assign_vlan_to_ports(vlan_id, interfaces):
                changes.append('VLAN assigned to interfaces')
    else:
        if vlan_config(config, vlan_id):
            changes.append('VLAN removed')

    results = {'changed': bool(changes), 'changes': changes}

    if changes and not module.check_mode:
        try:
            connection.edit_config(config)
        except Exception as e:
            module.fail_json(msg=f"Error committing changes: {e}")

    module.exit_json(**results)

if __name__ == '__main__':
    main()
