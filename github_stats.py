#!/usr/bin/env python

from __future__ import print_function
import csv
import json

from github import Github


def get_org_stats():
    """
    Get stats on each contributor in an organization on github.
    """
    #TODO: add settings to YAML
    # username = input('GH Username: ')
    # password = input('GH Password: ')
    # org = input('GH Org: ')
    # g = Github(username, password)
    g = Github("<KEY>") 

    contributors = dict()

    repo =g.get_repo("socotra-stack")
    repo_contributors = repo.get_stats_contributors()
    if not repo_contributors:
        return

    for contributor in repo_contributors:
        login = contributor.author.login
        cont_data = contributors.get(login, dict())
        for stat in ('total_commits', 'additions', 'deletions'):
            cont_data[stat] = cont_data.get(stat, 0)
            cont_data['repos'] = cont_data.get('repos', [])
            cont_data['repos'].append(repo.full_name)
            cont_data['total_commits'] += contributor.total

            for week in contributor.weeks:
                for key, ghkey in (('additions', 'a'), ('deletions', 'd')):
                    cont_data[key] += getattr(week, ghkey)
            contributors[login] = cont_data
    # Dump JSON
    with open('data.json', 'w') as outfile:
        json.dump(contributors, outfile, indent=2)

    # Dump CSV
    user_list = []
    for user in contributors:
        additions = contributors[user]['additions']
        deletions = contributors[user]['deletions']
        user_list.append(
            (
                user,
                contributors[user]['total_commits'],
                additions,
                deletions,
                additions + deletions,
                len(contributors[user]['repos'])
            )
        )
    with open('data.csv', 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(
            [
                'username',
                'commits',
                'additions',
                'deletions',
                'changes',
                'number of repos'
            ]
        )
        for row in user_list:
            csv_writer.writerow(row)

if __name__ == '__main__':
    get_org_stats()
