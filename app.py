#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from account_foundation_setup.account_foundation_setup_stack import SetupStack

app = cdk.App()
SetupStack(app, "AccountFoundationSetupStack")

app.synth()
