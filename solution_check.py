import itertools
import json
from pathlib import Path


def round_result(result):
    distr = result['distribution']
    for key in distr:
        distr[key] = round(distr[key], 7)


def results_match(result1, result2) -> bool:
    for r in result1 + result2:
        round_result(r)
    for r in result1:
        if r not in result2:
            return False
    for r in result2:
        if r not in result1:
            return False
    return True


def compare_directories(dir1: Path, dir2: Path):
    filenames = {path.name for path in itertools.chain(
        dir1.glob('*.json'), dir2.glob('*.json'))}
    correct: int = 0
    for filename in sorted(filenames):
        if filename == 'solution-h-00.json':
            print('bad solutions')
        if not (p1 := dir1 / filename).is_file():
            print(f'{filename} does not exist in {dir1}')
        elif not (p2 := dir2 / filename).is_file():
            print(f'{filename} does not exist in {dir2}')
        else:
            with open(p1) as fp1, open(p2) as fp2:
                if results_match(json.load(fp1), json.load(fp2)):
                    correct += 1
                else:
                    print(f'The solutions in {filename} do not match')
    print(f'{correct} solutions match')


if __name__ == '__main__':
    import sys

    compare_directories(Path('my_solutions'), Path('example-solutions'))

