# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    get_enum_type,
    # get_location_type,
    get_resource_name_completion_list,
    resource_group_name_type,
    tags_type)

# from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.command_modules.lbs.validators import validate_account_name
from azure.mgmt.locationbasedservices.models.client_enums import KeyType


def load_arguments(self, _):
    # Argument Definition
    lbs_name_type = CLIArgumentType(options_list=['--account-name', '-n'],
                                    completer=get_resource_name_completion_list(
                                        'Microsoft.LocationBasedServices/accounts'),
                                    help='The name of the Location Based Services Account',
                                    validator=validate_account_name)

    # Parameter Registration
    with self.argument_context('lbs') as c:
        c.argument('resource_group_name',
                   arg_type=resource_group_name_type,
                   help='Resource group name',
                   required=True)
        c.argument('account_name',
                   arg_type=lbs_name_type,
                   required=True)

    with self.argument_context('lbs account create') as c:
        c.argument('sku_name',
                   options_list=['--sku'],
                   help='The name of the SKU, in standard format (such as S0).')
        # c.argument('location',
        #           arg_type=get_location_type(self.cli_ctx),
        #           validator=get_default_location_from_resource_group,
        #           help='The location of the resource')
        c.argument('tags',
                   arg_type=tags_type)

    with self.argument_context('lbs account key regenerate') as c:
        c.argument('key_type',
                   options_list=['--type', '-t'],
                   arg_type=get_enum_type(KeyType),
                   choices=['primary', 'secondary'])
