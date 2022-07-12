from src.britive.britive import  Britive
import json


def main():
    b = Britive()

    response = b.my_access.checkout(
        profile_id='ihc0cg0iq7t266etzhxn',
        environment_id='196226166352',
        include_credentials=True,
        justification='test',
        wait_time=10,
        max_wait_time=60
    )

    if False:
        response = b.my_access.checkout(
            profile_id='q07fqvilt8dv32einf3x',
            environment_id='378563640942',
            include_credentials=True,
            justification='test',
            wait_time=10,
            max_wait_time=60
        )

    print(json.dumps(response, indent=2))


if __name__ == '__main__':
    main()
