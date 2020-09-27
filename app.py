#!/usr/bin/env python3

from aws_cdk import core

from infra.infra_stack import InfraStack

env_us = core.Environment(account="632568725601", region="us-west-2")

app = core.App()
InfraStack(app, "infra",env=env_us)

app.synth()
