from TaskGenerator import TaskGenerator
from pathlib import Path


def main():
    tg = TaskGenerator(random_seed=0)
    tg.import_module('math')
    tg.import_module('MyModule')
    json_path = Path('data_file.json')
    print(tg.json_rules_to_str(json_path))


if __name__ == '__main__':
    main()
