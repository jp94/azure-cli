# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, record_only
from azure.mgmt.maps.models.maps_management_client_enums import KeyType


class MapsScenarioTests(ScenarioTest):

    @record_only()
    @ResourceGroupPreparer(key='rg')
    @ResourceGroupPreparer(key='rg1')
    def test_create_maps_account(self, resource_group):
        tag_key = self.create_random_name(prefix='key-', length=10)
        tag_value = self.create_random_name(prefix='val-', length=10)

        self.kwargs.update({
            'name': self.create_random_name(prefix='cli-', length=20),
            'name1': self.create_random_name(prefix='cli-', length=20),
            'name2': self.create_random_name(prefix='cli-', length=20),
            'sku': 'S0',
            'tags': tag_key + '=' + tag_value,
            'key_type_primary': KeyType.primary.value,
            'key_type_secondary': KeyType.secondary.value
        })

        # Test 'az maps account create'.
        # Test to create a Maps account.
        account = self.cmd('az maps account create -n {name} -g {rg} --sku {sku}',
                           checks=[
                               self.check('name', '{name}'),
                               self.check('resourceGroup', '{rg}'),
                               self.check('sku.name', '{sku}'),
                               self.check('tags', None)
                           ]).get_output_in_json()

        # Call create again, expect to get the same account.
        account_duplicated = self.cmd(
            'az maps account create -n {name} -g {rg} --sku {sku}').get_output_in_json()
        self.assertEqual(account, account_duplicated)

        # Test 'az maps account update'
        # Test to add a new tag to an existing account.
        self.cmd('az maps account update -n {name} -g {rg} --sku {sku} --tags {tags}',
                 checks=[
                     self.check('id', account['id']),
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('sku.name', '{sku}'),
                     self.check('tags', {tag_key: tag_value})
                 ])

        # Test 'az maps account show'.
        # Test to get information on Maps account.
        self.cmd('az maps account show -n {name} -g {rg}', checks=[
            self.check('id', account['id']),
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('sku.name', '{sku}')
        ])
        # Search by id
        self.cmd('az maps account show --ids ' + account['id'], checks=[
            self.check('id', account['id']),
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('sku.name', '{sku}'),
            self.check('tags', {tag_key: tag_value})
        ])

        # Test 'az maps account list'.
        # Test to list all Maps accounts under a resource group.
        self.cmd('az maps account list -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check('type(@)', 'array'),
            self.check('[0].id', account['id']),
            self.check('[0].name', '{name}'),
            self.check('[0].resourceGroup', '{rg}'),
            self.check('[0].sku.name', '{sku}'),
            self.check('[0].tags', {tag_key: tag_value})
        ])

        # Create two new accounts (One in separate resource group).
        self.cmd('az maps account create -n {name1} -g {rg1} --sku {sku}')
        self.cmd('az maps account create -n {name2} -g {rg} --sku {sku}')
        # Check that list command now shows two accounts in one resource group, and one in another.
        self.cmd('az maps account list -g {rg}', checks=[
            self.check('length(@)', 2),
            self.check('type(@)', 'array'),
            self.check("length([?name == '{name}'])", 1),
            self.check("length([?name == '{name1}'])", 0),
            self.check("length([?name == '{name2}'])", 1),
            self.check("length([?resourceGroup == '{rg}'])", 2),
            self.check("length([?resourceGroup == '{rg1}'])", 0)
        ])
        self.cmd('az maps account list -g {rg1}', checks=[
            self.check('length(@)', 1),
            self.check('type(@)', 'array'),
            self.check("length([?name == '{name}'])", 0),
            self.check("length([?name == '{name1}'])", 1),
            self.check("length([?name == '{name2}'])", 0),
            self.check("length([?resourceGroup == '{rg}'])", 0),
            self.check("length([?resourceGroup == '{rg1}'])", 1)
        ])

        # Test 'az maps account key list'.
        # Test to list keys for a Maps account.
        account_key_list = self.cmd('az maps account keys list -n {name} -g {rg}', checks=[
            self.check('id', account['id']),
            self.check('resourceGroup', '{rg}')
        ]).get_output_in_json()

        # Retrieve primary and secondary keys.
        primary_key_old = account_key_list['primaryKey']
        secondary_key_old = account_key_list['secondaryKey']
        self.assertTrue(re.match('^[a-zA-Z0-9_-]+$', primary_key_old))
        self.assertTrue(re.match('^[a-zA-Z0-9_-]+$', secondary_key_old))

        # Test 'az maps account key regenerate'.
        # Test to change primary and secondary keys for a Maps account.
        key_regenerated = self.cmd(
            'az maps account keys renew -n {name} -g {rg} --key {key_type_primary}', checks=[
                self.check('id', account['id']),
                self.check('resourceGroup', '{rg}')
            ]).get_output_in_json()

        # Only primary key was regenerated. Secondary key should remain same.
        self.assertNotEqual(primary_key_old, key_regenerated['primaryKey'])
        self.assertEqual(secondary_key_old, key_regenerated['secondaryKey'])

        # Save the new primary key, and regenerate the secondary key.
        primary_key_old = key_regenerated['primaryKey']
        key_regenerated = self.cmd(
            'az maps account keys renew -n {name} -g {rg} --key {key_type_secondary}') \
            .get_output_in_json()
        self.assertEqual(primary_key_old, key_regenerated['primaryKey'])
        self.assertNotEqual(secondary_key_old, key_regenerated['secondaryKey'])

        # Test 'az maps account delete'.
        # Test to remove a Maps account.
        self.cmd('az maps account delete -n {name} -g {rg}', checks=self.is_empty())
        self.cmd('az maps account list -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check("length([?name == '{name}'])", 0)
        ])

        # Remove the rest of Maps accounts.
        exit_code = self.cmd('az maps account delete -n {name1} -g {rg1}').exit_code
        self.assertEqual(exit_code, 0)
        self.cmd('az maps account delete -n {name2} -g {rg}')
        self.cmd('az maps account list -g {rg}', checks=self.is_empty())
        self.cmd('az maps account list -g {rg1}', checks=self.is_empty())
