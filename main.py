from TaskGenerator import TaskGenerator
from pathlib import Path


def main():
    tg = TaskGenerator(random_seed=0)
    tg.import_module('math')
    tg.import_module('MyModule')
    json_path = Path('data_file.json')
    json, variables = tg.json_rules_to_str(json_path, root_state='Body')
    print(json)
    print(variables)


if __name__ == '__main__':
    main()
