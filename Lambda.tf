resource "aws_iam_role" "awsvianatgw" {
  name = "${var.name}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "awsvianatgw" {
  name = "${var.name}"
  role = "${aws_iam_role.awsvianatgw.name}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents", 
                "ec2:Describe*",
	        "ec2:CreateRoute",
                "ec2:DeleteRoute"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_lambda_function" "awsvianatgw" {
  filename         = "${path.module}/awsvianatgw.zip"
  source_code_hash = "${base64sha256(file("${path.module}/awsvianatgw.zip"))}"
  function_name    = "${var.name}"
  description      = "Lambda Function to add static routes for specified AWS services within provided regions"
  role             = "${aws_iam_role.awsvianatgw.arn}"
  memory_size	   = "${var.aws_lambda_function_memory_size}"
  timeout      	   = "${var.aws_lambda_function_timeout}"
  handler          = "awsvianatgw.lambda_handler"
  runtime          = "python3.7"

  environment {
    variables = {
      AWSregions     = "${var.AWSregions}"
      AWSvpcids      = "${var.AWSvpcids}"
      AWSservices    = "${var.AWSservices}"
      AWSRouteLimit  = "${var.AWSRouteLimit}"
      IgnoreRoutes   = "${var.IgnoreRoutes}"
    }
  }

  tags = "${var.tags}"
}

resource "aws_lambda_permission" "allow_cloudwatch_events" {
  statement_id   = "AllowExecutionFromCloudWatchEvents"
  action         = "lambda:InvokeFunction"
  function_name  = "${aws_lambda_function.awsvianatgw.function_name}"
  principal      = "events.amazonaws.com"
  source_arn     = "${aws_cloudwatch_event_rule.awsvianatgw.arn}"
}

resource "aws_cloudwatch_event_rule" "awsvianatgw" {
  name        = "${var.name}"
  description = "This is a rule for triggering our lambdas every five minutes."
  schedule_expression = "${var.schedule_expression}"
}
  
resource "aws_cloudwatch_event_target" "awsvianatgw" {
  rule      = "${aws_cloudwatch_event_rule.awsvianatgw.name}"
  arn       = "${aws_lambda_function.awsvianatgw.arn}"
}
