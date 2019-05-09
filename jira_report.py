from jira import JIRA
from prettytable import PrettyTable
from jira.client import GreenHopper
from github import Github

import json
import argparse
import sys
import datetime
from datetime import timedelta
import pprint

VERBOSE = None

# TODO: add Server and API key to YAML file.
options = {'server': 'https://socotra.atlassian.net',}
jira = JIRA(options, basic_auth=('prashant.dhamdhere@socotra.com', '<Enter API Key>'))
#jgh = GreenHopper(options, basic_auth=('prashant.dhamdhere@socotra.com', '<Enter API Key>'))
gh = Github("<Enter GitHub API Key>")

def main():
    args = parse_args()
    if not args:
        sys.exit(1)

    VERBOSE = args.verbose
    # now all set. Execute !
    if args.func(args) is not None:
        sys.exit(1)
    sys.exit(0)


def get_jira_fields():
    resp=jira.fields()
    fmap = { }
    for i in resp:
        field_name=i[u'name'].encode('ascii','ignore')
        field_id=i[u'id'].encode('ascii','ignore')
        fmap[field_name]=field_id
    pprint.pprint(fmap)

def sprint_user_stats(args):
    if not args.bid:
        board_id = 20
    sprint_id = args.sid
    
    sprint_summary(args)

    cur_sprint = jira.sprint_info(board_id, sprint_id)
    start = datetime.datetime.strptime(cur_sprint['isoStartDate'], '%Y-%m-%dT%H:%M:%S-%f')
    end = datetime.datetime.strptime(cur_sprint['isoCompleteDate'], '%Y-%m-%dT%H:%M:%S-%f')

    user_report = PrettyTable()
    user_report.field_names = ["User Name", "Story Points"]

    # Get completed issues from Jira Dashboard
    completed_issues = jira.completed_issues(board_id, sprint_id)

    done_points = 0
    closed_points = 0
    user_dict = {}
    story_sum = 0
    for issue in completed_issues:
        try:
            points = issue['currentEstimateStatistic']['statFieldValue']['value']
            if issue['statusName'] == "Closed":
                closed_points = closed_points + points
            elif not issue['assignee'] in user_dict:
                user_dict[issue['assignee']] = points
                done_points = done_points + points
            else:
                user_dict[issue['assignee']] = user_dict[issue['assignee']] + points
                done_points = done_points + points
        except KeyError: 
            if VERBOSE:
                print "Error: No story points assigned to " + issue['key']
                pass
    
    for key, value in user_dict.items():
        user_report.add_row([key, value])

    user_report.reversesort = False
    print user_report
    print "\nDone Points: " + str(done_points) + " Closed Points: " + str(closed_points) + " Total: " + str(done_points + closed_points) + "\n"

def sprint_summary(args):
    if not args.bid:
        board_id = 20
    sprint_id = args.sid

    cur_sprint = jira.sprint_info(board_id, sprint_id)
    print "\n++++ " + cur_sprint['name'] + " ++++"
    print "Sprint Start Date:       " + cur_sprint['startDate']
    print "Sprint Complted Date:    " + cur_sprint['completeDate']
    print "Sprint State:            " + cur_sprint['state']
    print "++++++++++++\n"

def sprint_stats(args):
    if not args.bid:
        board_id = 20
    sprint_id = args.sid

    #sprint_summary(args)
    sprint_user_stats(args)

    committed = jira.committedIssuesAtStart(board_id, sprint_id)
    completed = jira.completedIssuesEstimateSum(board_id, sprint_id)
    incomplete = jira.issuesNotCompletedEstimateSum(board_id, sprint_id)
    removed = jira.removedIssuesEstimateSum(board_id, sprint_id)

    added_issues = jira.added_issues(board_id, sprint_id)
    added = 0
    for tmp in added_issues:
        issue = jira.issue(tmp)
        try:
            #print user + issue.key
            if issue.fields.customfield_10005 is not None:
                added = added + issue.fields.customfield_10005
        except AttributeError:
            if VERBOSE:
                print "Error: Story points missing " + user + issue.key
            continue

    sprint_report = PrettyTable()
    sprint_report.field_names = ["Description", "Total"]


    sprint_report.add_row(["Points Committed", str(committed)])
    sprint_report.add_row(["Points Completed", str(completed)])
    sprint_report.add_row(["Not Completed", str(incomplete)])
    sprint_report.add_row(["Points Added", str(added)])
    sprint_report.add_row(["Points Removed", str(removed)])

    print sprint_report


def commands():
    def more_info():
    # This function only keeps info about how to define new commands.
    # It is defined as function so you can collapse it in editors.
    # Borrowed from https://github.com/vmware/vsphere-storage-for-docker/blob/master/esx_service/cli/vmdkops_admin.py

        """
        This function returns a dictionary representation of a CLI specification that is used to
        generate a CLI parser. The dictionary is recursively walked in the `add_subparser()` function
        and appropriate calls are made to the `argparse` module to create a CLI parser that fits the
        specification.
        Each key in the top level of the dictionary is a command string. Each command may contain the
        following keys:
        * func - The callback function to be called when the command is issued. This key is always
                present unless there are subcommands, denoted by a 'cmds' key.
        * help - The help string that is printed when the `-h` or `--help` parameters are given without
                reference to a given command. (i.e. `./vmdkops_admin.py -h`). All top level help
                strings are printed in this instance.
        * args - A dictionary of any positional or optional arguments allowed for the given command. The
                args dictionary may contain the following keys:
                * help - The help for a given option which is displayed when the `-h` flag is given
                        with mention to a given command. (i.e. `./vmdkops_admin.py volume ls -h`). Help for
                        all options are shown for the command.
                * action - The action to take when the option is given. This is directly passed to
                            argparse. Note that `store_true` just means pass the option to the callback
                            as a boolean `True` value and don't require option parameters.
                            (i.e. `./vmdkops_admin.py volume ls -l`). Other options for the action value can be
                            found in the argparse documentation.
                            https://docs.python.org/3/library/argparse.html#action
                * metavar - A way to refer to each expected argument in help documentation. This is
                            directly passed to argparse.
                            See https://docs.python.org/3/library/argparse.html#metavar
                * required - Whether or not the argument is required. This is directly passed to
                            argparse.
                * type - A type conversion function that takes the option parameter and converts it
                        to a given type before passing it to the func callback. It prints an error and
                        exits if the given argument cannot be converted.
                        See https://docs.python.org/3/library/argparse.html#type
                * choices - A list of choices that can be provided for the given option. This list is
                            not directly passed to argparse. Instead a type conversion function is
                            created that only allows one or more of the choices as a comma separated
                            list to be supplied. An error identical to the one presented when using the
                            'choices' option in argparse is printed if an invalid choice is given. The
                            rationale for not directly using the argparse choices option is that
                            argparse requires space separated arguments of the form: `-l a b c`, rather
                            than the defacto single argument, comma separated form: `-l a,b,c`, common
                            to most unix programs.
        * cmds - A dictionary of subcommands where the key is the next word in the command line string.
                For example, in `vmdkops_admin.py tenant create`, `tenant` is the command, and `create` is
                the subcommand. Subcommands can have further subcommands, but currently there is only
                one level of subcommands in this specification. Each subcommand can contain the same
                attributes as top level commands: (func, help, args, cmds). These attributes have
                identical usage to the top-level keys, except they only apply when the subcommand is
                part of the command. For example the `--vm-list` argument only applies to `tenant
                create` or `tenant set` commands. It will be invalid in any other context.
                Note that the last subcommand in a chain is the one where the callback function is
                defined. For example, `tenant create` has a callback, but if a user runs the program
                like: `./vmdkops_admin.py tenant` they will get the following error:
                ```
                usage: vmdkops_admin.py tenant [-h] {rm,create,volume,get} ...
                vmdkops_admin.py tenant: error: too few arguments
                ```
        """

    return {
        'sprint' : {
            'help' : 'Sprint Ops',
            'cmds' : {
                'velocity' : {
                    'func' : sprint_user_stats,
                    'help' : 'Sprint Velocity/User',
                    'args' : {
                        '--sid' : {
                            'help' : 'Sprint ID',
                            'required': True,
                        },
                        '--bid' : {
                            'help': "Board ID",
                        }
                    }
                },
                'stats' : {
                    'func' : sprint_stats,
                    'help' : 'Sprint Summary',
                    'args' : {
                        '--sid' : {
                            'help' : 'Sprint ID',
                            'required': True,
                        },
                        '--bid' : {
                            'help': "Board ID",
                        }
                    }
                },
            }
        }
    }

def create_parser():
    """ Create a CLI parser via argparse based on the dictionary returned from commands() """
    parser = argparse.ArgumentParser(description='Manager Ops')
    parser.add_argument('-v', '--verbose', action='store_false')
    add_subparser(parser, commands(), title='Manager Ops CLI')
    return parser


def add_subparser(parser, cmds_dict, title="", description=""):
    """ Recursively add subcommand parsers based on a dictionary of commands """
    subparsers = parser.add_subparsers(title=title, description=description, help="action")
    for cmd, attributes in cmds_dict.items():
        subparser = subparsers.add_parser(cmd, help=attributes['help'])
        if 'func' in attributes:
            subparser.set_defaults(func=attributes['func'])
        if 'args' in attributes:
            for arg, opts in attributes['args'].items():
                opts = build_argparse_opts(opts)
                subparser.add_argument(arg, **opts)
        if 'cmds' in attributes:
            add_subparser(subparser, attributes['cmds'], title=attributes['help'])

def build_argparse_opts(opts):
    if 'choices' in opts:
        opts['type'] = make_list_of_values(opts['choices'])
        help_opts = opts['help']
        opts['help'] = '{0}: Choices = {1}'.format(help_opts, opts['choices'])
        del opts['choices']
    return opts

def parse_args():
    parser = create_parser()
    args = parser.parse_args()
    opts = vars(args)
    if args != argparse.Namespace() and 'func' in opts.keys():
        return args
    parser.print_help()
    return 0

def make_list_of_values(allowed):
    """
    Take a list of allowed values for an option and return a function that can be
    used to typecheck a string of given values and ensure they match the allowed
    values.  This is required to support options that take comma separated lists
    such as --rights=create,delete,mount
    """

    def list_of_values(string):
        given = string.split(',')
        for var in given:
            if var not in allowed:
                msg = (
                    'invalid choices: {0} (choices must be a comma separated list of '
                    'only the following words \n {1}. '
                    'No spaces are allowed between choices.)'
                    ).format(var, repr(allowed).replace(' ', ''))
                raise argparse.ArgumentTypeError(msg)
        return given

    return list_of_values

if __name__ == "__main__":
    main()



