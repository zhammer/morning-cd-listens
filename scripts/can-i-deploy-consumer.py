import json
import sys
from typing import NoReturn


def main() -> NoReturn:
    """Only fail can-i-deploy if there are consumers that are out of sync. The pact-broker
    can-i-deploy tool also fails for provider issues, which I handle via faaspact-verifier.

    USAGE:
    pact-broker can-i-deploy ... --output json | python can-i-deploy-consumer.py
    """
    can_i_deploy_json = json.load(sys.stdin)
    for row in can_i_deploy_json['matrix']:
        if row['verificationResult'] is None:
            exit(1)
        elif not row['verificationResult']['success']:
            exit(1)
    exit(0)


if __name__ == '__main__':
    main()
