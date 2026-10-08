#!/usr/bin/env python3
"""Synthetic tax-rate fixture runner. Python 3.9+, standard library only."""
import argparse
import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import re


def field(raw, name, maximum):
    value = raw.strip()
    if not value:
        raise ValueError(name + '_REQUIRED')
    if not re.fullmatch(r'-?[0-9]+(?:\.[0-9]+)?', value):
        raise ValueError(name + '_FORMAT')
    number = Decimal(value)
    if number < 0 or number > maximum:
        raise ValueError(name + '_RANGE')
    if number.as_tuple().exponent < -2:
        raise ValueError(name + '_SCALE')
    return number


def calculate(amount, rate, mutant=False):
    """Replace this function with an adapter to your implementation for real checks."""
    try:
        a = field(amount, 'AMOUNT', Decimal('1000000'))
        r = field(rate, 'RATE', Decimal('100'))
    except ValueError as error:
        return str(error), ''
    tax = a * r if mutant else a * r / Decimal('100')
    return 'OK', format(tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), '.2f')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mutant', action='store_true', help='omit division by 100 deliberately')
    parser.add_argument('--cases', type=Path, default=Path(__file__).with_name('cases.csv'))
    args = parser.parse_args()
    failed = total = 0
    with args.cases.open(encoding='utf-8-sig', newline='') as source:
        for row in csv.DictReader(source):
            total += 1
            actual = calculate(row['amount'], row['rate'], args.mutant)
            expected = (row['expected_status'], row['expected_tax'])
            passed = actual == expected
            failed += not passed
            print(f"{'PASS' if passed else 'FAIL'} {row['id']}: expected={expected}, actual={actual}")
    if not total:
        parser.error('case file must contain at least one case')
    print(f'{total - failed}/{total} passed; {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
