data "aws_iam_policy_document" "valhub_worker_assume_role_policy" {
  version = "2012-10-17"

  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sqs.amazonaws.com", "s3.amazonaws.com", "secretsmanager.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# TODO: Update the policy to restrict access to specific SQS queues, S3 buckets, and Secrets Manager secrets as needed.
data "aws_iam_policy_document" "valhub_worker_policy_document" {
  version = "2012-10-17"

  statement {
    effect = "Allow"

    actions = [
      "sqs:SendMessage",
      "s3:GetObject",
      "secretsmanager:GetSecretValue"
    ]

    resources = [
      "*"
    ]
  }
}

resource "aws_iam_role_policy_attachment" "valhub_worker_policy_attachment" {
  policy_arn = aws_iam_policy.valhub_worker_policy.arn
  role       = aws_iam_role.valhub_worker_role.name
}

resource "aws_iam_policy" "valhub_worker_policy" {
  name        = "valhub-worker-policy"
  description = "Policy for ValHub worker role"

  policy = data.aws_iam_policy_document.valhub_worker_policy_document.json
}


resource "aws_iam_role" "valhub_worker_role" {
  name = "valhub-worker-role"

  assume_role_policy = data.aws_iam_policy_document.valhub_worker_assume_role_policy.json

  tags = {
    Name = "valhub-worker-role"
  }
}
