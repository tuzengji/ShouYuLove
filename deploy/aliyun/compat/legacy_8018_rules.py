#!/usr/bin/env python3
"""Manage only this migration's exact IPv4 rules; never flush a chain."""
import argparse
import json
import os
import subprocess

IPTABLES='/usr/sbin/iptables'
DIRECT=['-i','eth0','-p','tcp','--dport','18018','-m','conntrack','!','--ctorigdstport','8018',
        '-m','comment','--comment','syl-migrate-20261015-legacy-18018-direct','-j','REJECT','--reject-with','tcp-reset']
REDIRECT=['-i','eth0','-p','tcp','--dport','8018','-m','addrtype','--dst-type','LOCAL',
          '-m','comment','--comment','syl-migrate-20261015-legacy-8018','-j','REDIRECT','--to-ports','18018']


def command(table,action,chain,rule,insert=False):
    return [IPTABLES,'-w','10','-t',table,action,chain]+(['1'] if insert else [])+rule


def exists(table,chain,rule):
    result=subprocess.run(command(table,'-C',chain,rule),capture_output=True)
    if result.returncode not in (0,1):raise RuntimeError('iptables check failed')
    return result.returncode==0


def ensure(table,chain,rule):
    if not exists(table,chain,rule):
        subprocess.run(command(table,'-I',chain,rule,True),capture_output=True,check=True)


def remove(table,chain,rule):
    if exists(table,chain,rule):
        subprocess.run(command(table,'-D',chain,rule),capture_output=True,check=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['protect','apply','remove','status'])
    args=parser.parse_args()
    if os.geteuid()!=0:raise SystemExit('Root required')
    if args.action in {'protect','apply'}:ensure('filter','INPUT',DIRECT)
    if args.action=='apply':ensure('nat','PREROUTING',REDIRECT)
    if args.action=='remove':
        remove('nat','PREROUTING',REDIRECT)
        remove('filter','INPUT',DIRECT)
    print(json.dumps({'direct_block':exists('filter','INPUT',DIRECT),
                      'redirect':exists('nat','PREROUTING',REDIRECT)}))


if __name__=='__main__':main()
