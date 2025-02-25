# Copyright 2015-2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import itest_utils
from behave import then
from behave import when
from marathon import MarathonApp

from paasta_tools.utils import _run
from paasta_tools.utils import remove_ansi_escape_sequences

CONTAINER = {"type": "DOCKER", "docker": {"network": "BRIDGE", "image": "busybox"}}


@when("all zookeepers are unavailable")
def all_zookeepers_unavailable(context):
    pass


@when("all mesos masters are unavailable")
def all_mesos_masters_unavailable(context):
    pass


@when('an app with id "{app_id}" using high memory is launched')
def run_paasta_metastatus_high_mem(context, app_id):
    context.marathon_clients.current[0].create_app(
        app_id,
        MarathonApp(cmd="/bin/sleep 100000", mem=490, instances=3, container=CONTAINER),
    )


@when('an app with id "{app_id}" using high disk is launched')
def run_paasta_metastatus_high_disk(context, app_id):
    context.marathon_clients.current[0].create_app(
        app_id,
        MarathonApp(cmd="/bin/sleep 100000", disk=95, instances=3, container=CONTAINER),
    )


@when('an app with id "{app_id}" using high cpu is launched')
def run_paasta_metastatus_high_cpu(context, app_id):
    context.marathon_clients.current[0].create_app(
        app_id,
        MarathonApp(
            cmd="/bin/sleep 100000", cpus=9.1, instances=3, container=CONTAINER
        ),
    )


@when('a task belonging to the app with id "{app_id}" is in the task list')
def marathon_task_is_ready(context, app_id):
    """Wait for a task with a matching task name to be ready. time out in 60 seconds"""
    marathon_tasks_are_ready(context, 1, app_id)


@when('{num:d} tasks belonging to the app with id "{app_id}" are in the task list')
def marathon_tasks_are_ready(context, num, app_id):
    """Wait for the specified number of  tasks with matching task names to be ready. time out in 60 seconds"""
    itest_utils.wait_for_app_to_launch_tasks(
        context.marathon_clients.current[0], app_id, num
    )


@then(
    'paasta_metastatus{flags} exits with return code "{expected_return_code}" and output "{expected_output}"'
)
def check_metastatus_return_code_with_flags(
    context, flags, expected_return_code, expected_output
):
    # We don't want to invoke the "paasta metastatus" wrapper because by
    # default it will check every cluster. This is also the way sensu invokes
    # this check.
    cmd = "python -m paasta_tools.paasta_metastatus%s" % flags
    print("Running cmd %s" % (cmd))
    exit_code, output = _run(cmd)

    # we don't care about the colouring here, so remove any ansi escape sequences
    escaped_output = remove_ansi_escape_sequences(output)
    print(f"Got exitcode {exit_code} with output:\n{output}")
    print()

    assert exit_code == int(expected_return_code)
    assert expected_output in escaped_output


@then(
    'paasta_metastatus exits with return code "{expected_return_code}" and output "{expected_output}"'
)
def check_metastatus_return_code_no_flags(
    context, expected_return_code, expected_output
):
    check_metastatus_return_code_with_flags(
        context=context,
        flags="",
        expected_return_code=expected_return_code,
        expected_output=expected_output,
    )
