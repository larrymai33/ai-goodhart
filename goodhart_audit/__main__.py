"""Run with python -m goodhart_audit; no installation or network access."""

import argparse
import json
import sys

from .io import load_pool, make_plan, audit_report, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description='Audit finite-pool best-of-N risk with scarce labels.')
    commands = parser.add_subparsers(dest='command', required=True)
    plan = commands.add_parser('plan', help='Plan IID queries using only IDs and proxy scores')
    plan.add_argument('--pool', required=True)
    plan.add_argument('--out', required=True)
    plan.add_argument('--budgets', required=True, help='Comma-separated integers, e.g. 1,2,4,8')
    plan.add_argument('--draws', required=True, type=int)
    plan.add_argument('--seed', required=True, type=int)
    report = commands.add_parser('report', help='Analyze a plan after its query losses are filled')
    report.add_argument('--pool', required=True)
    report.add_argument('--audit', required=True)
    report.add_argument('--out', required=True)
    report.add_argument('--delta', type=float, default=0.05)
    report.add_argument('--threshold', type=float, default=0.1)
    args = parser.parse_args(argv)
    try:
        pool = load_pool(args.pool)
        if args.command == 'plan':
            result = make_plan(pool, [int(n) for n in args.budgets.split(',')], args.draws, args.seed)
            message = f"Planned {result['draw_count']} draws / {len(result['queries'])} unique labels. Fill queries[].loss."
        else:
            with open(args.audit, encoding='utf-8-sig') as stream:
                audit = json.load(stream)
            result = audit_report(pool, audit, args.delta, args.threshold)
            message = f"Finite-pool report: {result['unique_labels']} labels; certified budgets {result['certified_budgets']}."
        write_json(args.out, result)
        print(message)
    except (ValueError, OSError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
