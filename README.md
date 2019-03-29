AWS Services via NAT Gateway
=============

This module deploys a Lambda function to add static routes to routing tables within specificed VPCs for AWS Services such as S3.
This is useful when the default gateway is provided over a direct connect circuit but you want cross region AWS Services such as S3 to communicate over a NAT Gateway.


Example
------------
```
module "awsvianatgw" {
  source = "git::https://stash.aws.dnb.com/scm/netops/awsvianatgw.git"
  AWSregions = "us-west-2"
  AWSvpcids = "vpc-20c7b12478a923d47"
  AWSservices = "S3"
  tags = { 
    ProjectName    = "Infrastructure"
    Environment    = "Development"
    Classification = "Infrastructure"
  }
}
```
Information
------------
1. The number of static routes is limited to 50. To avoid overloading the routing table the default limit of this function is 25.
2. All routes pointing to a NAT Gateway that do not match the routes provided by the JSON filter will be deleted unless they are specified in the IgnoreRoutes parameter.
3. When first initializing this, one route must be pointing to the NAT Gateway. This is how the function determines the NAT Gateway to use for any routes it adds. This can be any dummy route and will be deleted when the Lambda function kicks off.

Argument Reference
------------
* **Settings**
   * **AWSregions** - Required : Space delimited list of regions for filtering the JSON, for example: us-east-1 us-west-2
   * **AWSvpcids** - Required : Space delimited list of VPC IDs the Lambda should update, for example: vpc-12468abc36 vpc-23468abc37
   * **IgnoreRoutes** - Optional : Space delimited list of CIDRs to ignore in routing tables. These CIDRs will not be deleted by the update function. For example: 123.123.123.0/24. The default is an empty string.
   * **AWSservices** - Optional : Space delimited list of AWS Services for filtering the JSON. These services must match those available in https://ip-ranges.amazonaws.com/ip-ranges.json and are case sensitive. The default is S3.
   * **tags** - Optional : A map of tags to assign to the resource.  
   * **aws_lambda_function_memory_size** - Optional : Amount of memory in MB your Lambda Function can use at runtime. Defaults to 128.
   * **aws_lambda_function_timeout** - Optional : The amount of time your Lambda Function has to run in seconds. Defaults to 300.
   * **name** - Optional : The name parameter is used to name various components within the module. The default is awsvianatgw.
   * **schedule_expression** - Optional : The scheduling expression. For example, cron(0 20 * * ? *). The default is rate(5 minutes).
   * **AWSRouteLimit** - Optional : Limit on the number of routes to ingest into the routing table. The default is 25.
