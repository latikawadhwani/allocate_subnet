data "archive_file" "allocate" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/"
  output_path = "${path.module}/lambda/allocate.zip"
}

resource "aws_lambda_function" "function_allocate" {
  function_name    = "allocate"
  description      = "!"
  role             = "${aws_iam_role.iam_role_for_lambda.arn}"
  memory_size      = "${var.memory_size}"
  runtime          = "${var.runtime}"
  timeout          = "${var.timeout}"
  handler          = "test-asdf1234.lambda_handler"
  filename         = "${path.module}/lambda/allocate.zip"
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
