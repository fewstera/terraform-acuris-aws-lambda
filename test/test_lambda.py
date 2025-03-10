import unittest
import os
from textwrap import dedent
from subprocess import check_call, check_output

cwd = os.getcwd()


class TestCreateTaskdef(unittest.TestCase):

    def setUp(self):
        check_call(['terraform', 'get', 'test/infra'])

    def test_all_resources_to_be_created(self):
        output = check_output([
            'terraform',
            'plan',
            '-no-color',
            'test/infra'
        ]).decode('utf-8')
        assert dedent("""
            Plan: 4 to add, 0 to change, 0 to destroy.
        """).strip() in output

    def test_create_lambda(self):
        output = check_output([
            'terraform',
            'plan',
            '-no-color',
            'test/infra'
        ]).decode('utf-8')
        assert dedent("""
            + module.lambda.aws_lambda_function.lambda_function
                arn:                 "<computed>"
                environment.#:       "1"
                function_name:       "check_lambda_function"
                handler:             "some_handler"
                invoke_arn:          "<computed>"
                last_modified:       "<computed>"
                memory_size:         "128"
                publish:             "false"
                qualified_arn:       "<computed>"
                role:                "${aws_iam_role.iam_for_lambda.arn}"
                runtime:             "python"
                s3_bucket:           "cdflow-lambda-releases"
                s3_key:              "s3key.zip"
                source_code_hash:    "<computed>"
                timeout:             "3"
                version:             "<computed>"
                vpc_config.#:        "1"
                vpc_config.0.vpc_id: "<computed>"
        """).strip() in output

    def test_create_lambda_in_vpc(self):
        output = check_output([
            'terraform',
            'plan',
            '-var', 'subnet_ids=[1,2,3]',
            '-var', 'security_group_ids=[4]',
            '-no-color',
            'test/infra'
        ]).decode('utf-8')
        assert dedent("""
             + module.lambda.aws_lambda_function.lambda_function
                 arn:                                        "<computed>"
                 environment.#:                              "1"
                 function_name:                              "check_lambda_function"
                 handler:                                    "some_handler"
                 invoke_arn:                                 "<computed>"
                 last_modified:                              "<computed>"
                 memory_size:                                "128"
                 publish:                                    "false"
                 qualified_arn:                              "<computed>"
                 role:                                       "${aws_iam_role.iam_for_lambda.arn}"
                 runtime:                                    "python"
                 s3_bucket:                                  "cdflow-lambda-releases"
                 s3_key:                                     "s3key.zip"
                 source_code_hash:                           "<computed>"
                 timeout:                                    "3"
                 version:                                    "<computed>"
                 vpc_config.#:                               "1"
                 vpc_config.0.security_group_ids.#:          "1"
                 vpc_config.0.security_group_ids.4088798008: "4"
                 vpc_config.0.subnet_ids.#:                  "3"
                 vpc_config.0.subnet_ids.1842515611:         "3"
                 vpc_config.0.subnet_ids.2212294583:         "1"
                 vpc_config.0.subnet_ids.450215437:          "2"
                 vpc_config.0.vpc_id:                        "<computed>"
        """).strip() in output

    def test_lambda_in_vpc_gets_correct_execution_role(self):
        output = check_output([
            'terraform',
            'plan',
            '-var', 'subnet_ids=[1,2,3]',
            '-var', 'security_group_ids=[4]',
            '-no-color',
            'test/infra'
        ]).decode('utf-8')
        assert dedent("""
            + module.lambda.aws_iam_role_policy_attachment.vpc_permissions
                policy_arn: "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
                role:       "${aws_iam_role.iam_for_lambda.name}"
        """).strip() in output
