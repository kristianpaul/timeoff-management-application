from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_efs as efs,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_ecs_patterns as ecs_patterns,
    core,
)

import os.path
dirname = os.path.dirname(__file__)

class InfraStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=3,
        )

        cluster = ecs.Cluster(
            self, 'Ec2Cluster',
            vpc=vpc
        )

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "FargateService",
            cluster=cluster,
            cpu=256,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(os.path.join(dirname, "..", "image")),
                container_port=3000),
            memory_limit_mib=512,
            public_load_balancer=True,
            listener_port=80)

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )

        fargate_service.target_group.configure_health_check(
            path="/login")
        
        distribution = cloudfront.Distribution(self, "myDist",
            default_behavior={
                "origin": origins.LoadBalancerV2Origin(fargate_service.load_balancer, protocol_policy=cloudfront.OriginProtocolPolicy("HTTP_ONLY"))}
        )
        
        core.CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name
        )

        core.CfnOutput(
            self, "CloudFrontDistributionDNS",
            value=distribution.domain_name

        )