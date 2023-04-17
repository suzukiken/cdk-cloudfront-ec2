import { Stack, StackProps, Fn, CfnOutput } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as route53 from 'aws-cdk-lib/aws-route53';
import * as targets from 'aws-cdk-lib/aws-route53-targets';

export class CdkCloudfrontEc2Stack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const domain = this.node.tryGetContext('domain')
    const subdomain = this.node.tryGetContext('subdomain')
    const acmarn = Fn.importValue(this.node.tryGetContext('useast1_acmarn_exportname'))
    const http_origin_host = this.node.tryGetContext('http_origin_host')
    const port = this.node.tryGetContext('port')

    const certificate = acm.Certificate.fromCertificateArn(this, 'certificate', acmarn)
    
    const distribution = new cloudfront.Distribution(this, 'distribution', {
      defaultBehavior: { 
        origin: new origins.HttpOrigin(http_origin_host, {
          httpPort: port,
          protocolPolicy: cloudfront.OriginProtocolPolicy.HTTP_ONLY
        }),
        cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
      },
      domainNames: [Fn.join(".", [subdomain, domain])],
      certificate: certificate,
      errorResponses: [
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html'
        },
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html'
        },
      ]
    })
    
    const zone = route53.HostedZone.fromLookup(this, "zone", {
      domainName: domain,
    })
    
    const record = new route53.ARecord(this, "record", {
      recordName: subdomain,
      target: route53.RecordTarget.fromAlias(
        new targets.CloudFrontTarget(distribution)
      ),
      zone: zone,
    })
    
    new CfnOutput(this, 'DomainName', { 
      value: record.domainName,
      description: "route53 record domain name"
    })
    
    new CfnOutput(this, 'ZoneName', { 
      value: zone.zoneName,
      description: "route53 zone name"
    })
    
    new CfnOutput(this, 'Distribution', { 
      value: distribution.distributionId,
      description: "CloudFront distribution id",
      exportName: "cloud9-web-distribution-id"
    })

  }
}


