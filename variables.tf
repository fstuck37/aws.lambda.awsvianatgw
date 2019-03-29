variable "AWSregions" {
  description = "Required : Space delimited list of regions for example: us-east-1 us-west-2"
}

variable "AWSvpcids" {
  description = "Required : Space delimited list of VPC IDs in the account & region this should update for example: vpc-12468abc36 vpc-23468abc37"
}

variable "IgnoreRoutes" {
  description = "Optional : Space delimited list of CIDRs to ignore in routing tables. This CIDRs will not be deleted by the update function. For example: 123.123.123.0/24"
  default=""
}

variable "AWSservices" {
  description = "Optional : Space delimited list of AWS Services to add to the routing tables. This services must match those available in https://ip-ranges.amazonaws.com/ip-ranges.json. This defaults to S3."
  default="S3"
}

variable "tags" {
  type = "map" 
  description = "Optional : A map of tags to assign to the resource."  
  default = { }
}

variable "aws_lambda_function_memory_size" {
  description = "Optional : Amount of memory in MB your Lambda Function can use at runtime. Defaults to 128."
  default="128"
}

variable "aws_lambda_function_timeout" {
  description = "Optional : The amount of time your Lambda Function has to run in seconds. Defaults to 300."
  default="300"
}

variable "name" {
  description = "Optional : The name parameter is used to name various components within the module."
  default="awsvianatgw"
}

variable "schedule_expression" {
  description = "Optional : The scheduling expression. For example, cron(0 20 * * ? *). The default is rate(5 minutes)."
  default="rate(5 minutes)"
}


variable "AWSRouteLimit" {
  description = "Optional : Limit on the number of routes to ingest into the routing table. The default is 25."
  default="25"
}


