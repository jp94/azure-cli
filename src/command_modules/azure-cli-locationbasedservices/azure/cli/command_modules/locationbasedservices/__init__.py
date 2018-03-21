# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azure.cli.command_modules.locationbasedservices._help  # pylint: disable=unused-import
from azure.cli.command_modules.locationbasedservices._client_factory import cf_accounts


class LocationBasedServicesCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(
            operations_tmpl='azure.cli.command_modules.locationbasedservices.custom#{}',
            client_factory=cf_accounts)
        super(LocationBasedServicesCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                                  custom_command_type=custom_type)

    def load_command_table(self, args):
        from azure.cli.command_modules.locationbasedservices.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azure.cli.command_modules.locationbasedservices._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = LocationBasedServicesCommandsLoader