data "archive_file" "allocate" {
  type        = "zip"
  source_dir  = "${path.root}/lambda/"
  output_path = "${path.root}/allocate.zip"
}

resource "aws_lambda_function" "function_allocate" {
  function_name    = "allocate"
  description      = "lambda function to allocate subnet"
  role             = "${aws_iam_role.iam_role_for_lambda.arn}"
  memory_size      = "${var.memory_size}"
  runtime          = "${var.runtime}"
  timeout          = "${var.timeout}"
  reserved_concurrent_executions = 1
  handler          = "allocate.lambda_handler"
  filename         = "${path.root}/allocate.zip"
  source_code_hash = "${data.archive_file.allocate.output_base64sha256}"
}

resource "aws_iam_role" "iam_role_for_lambda" {
  name = "lambda_role"

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

resource "aws_iam_role_policy_attachment" "AWSLambdaExecute-attach" {
  role       = "${aws_iam_role.iam_role_for_lambda.name}"
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}


resource "aws_iam_role_policy_attachment" "AWSLambdaDynamoDbRead-attach" {
  role       = "${aws_iam_role.iam_role_for_lambda.name}"
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaInvocation-DynamoDB"
}

resource "aws_iam_role_policy_attachment" "AmazonDynamoDBFullAccess" {
  role       = "${aws_iam_role.iam_role_for_lambda.name}"
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_dynamodb_table" "lambda-allocation-requests" {
  name = "lambda-allocation-requests"
  hash_key = "id"
  billing_mode = "${var.billing_mode}"
  attribute {
    name = "id"
    type = "S"
  }
  stream_enabled = "${var.stream_enabled}"
  stream_view_type = "${var.stream_view_type}"
}

resource "aws_dynamodb_table" "account_allocations" {
  name = "account_allocations"
  hash_key = "id"
  range_key = "time_allocated"
  billing_mode = "${var.billing_mode}"
  attribute {
    name = "id"
    type = "S"
  }
  attribute {
    name = "time_allocated"
    type = "S"
  }
}

resource "aws_lambda_event_source_mapping" "lambda_allocation_stream" {
  event_source_arn  = "${aws_dynamodb_table.lambda-allocation-requests.stream_arn}"
  function_name     = "${aws_lambda_function.function_allocate.function_name}"
  starting_position = "LATEST"
}