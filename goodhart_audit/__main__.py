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
    unique = commands.add_parser('plan-unique', help='Plan distinct queries for an anytime audit')
    unique.add_argument('--pool', required=True)
    unique.add_argument('--out', required=True)
    unique.add_argument('--budgets', required=True)
    unique.add_argument('--labels', required=True, type=int)
    unique.add_argument('--seed', required=True, type=int)
    unique.add_argument('--method', default='envelope',
                        choices=['uniform', 'budget_mixture', 'dyadic_mixture', 'max_uniform', 'envelope'])
    unique.add_argument('--delta', type=float, default=0.05)
    unique_report = commands.add_parser('report-unique', help='Analyze any labeled query prefix')
    unique_report.add_argument('--pool', required=True)
    unique_report.add_argument('--audit', required=True)
    unique_report.add_argument('--out', required=True)
    unique_report.add_argument('--threshold', type=float, default=0.1)
    unique_report.add_argument('--rule', choices=['interval', 'upper-test'], default='interval')
    args = parser.parse_args(argv)
    try:
        pool = load_pool(args.pool)
        if args.command == 'plan':
            result = make_plan(pool, [int(n) for n in args.budgets.split(',')], args.draws, args.seed)
            message = f"Planned {result['draw_count']} draws / {len(result['queries'])} unique labels. Fill queries[].loss."
        elif args.command == 'report':
            with open(args.audit, encoding='utf-8-sig') as stream:
                audit = json.load(stream)
            result = audit_report(pool, audit, args.delta, args.threshold)
            message = f"Finite-pool report: {result['unique_labels']} labels; certified budgets {result['certified_budgets']}."
        elif args.command == 'plan-unique':
            from .unique_io import make_unique_plan
            result = make_unique_plan(pool, [int(n) for n in args.budgets.split(',')], args.labels,
                                      args.seed, args.method, args.delta)
            message = f"Planned {len(result['queries'])} distinct queries. Label a contiguous prefix in order."
        else:
            from .unique_io import unique_report as report_prefix
            with open(args.audit, encoding='utf-8-sig') as stream:
                audit = json.load(stream)
            result = report_prefix(pool, audit, args.threshold, args.rule)
            message = f"Anytime finite-pool report: {result['unique_labels']} unique labels; certified budgets {result['certified_budgets']}."
        write_json(args.out, result)
        print(message)
    except (ValueError, OSError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
