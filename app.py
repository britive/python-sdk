from britive import Britive
import json


def main():
    britive = Britive()
    print(json.dumps(britive.users.list(), indent=2, default=str))


if __name__ == '__main__':
    main()
