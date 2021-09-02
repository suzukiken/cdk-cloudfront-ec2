import * as cdk from '@aws-cdk/core';
import * as acm from "@aws-cdk/aws-certificatemanager";
import * as cloudfront from '@aws-cdk/aws-cloudfront';
import * as origins from '@aws-cdk/aws-cloudfront-origins';
import * as route53 from '@aws-cdk/aws-route53';
import * as targets from "@aws-cdk/aws-route53-targets/lib";

export class CdkCloudfrontEc2Stack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const domain = this.node.tryGetContext('domain')
    const subdomain = this.node.tryGetContext('subdomain')
    const acmarn = cdk.Fn.importValue(this.node.tryGetContext('useast1_acmarn_exportname'))
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
      domainNames: [cdk.Fn.join(".", [subdomain, domain])],
      certificate: certificate,
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

  }
}
