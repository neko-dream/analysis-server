#!/bin/bash

login_aws() {
  aws sts get-caller-identity --profile $AWS_PROFILE &>/dev/null || aws sso login --profile $AWS_PROFILE &>/dev/null
  if [ -z "$1" ]; then
      echo "AWS profile name is required" >&2
      return 1
  fi

  ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text --profile $1)
  if [ -z "$ACCOUNT_ID" ]; then
      echo "Failed to get AWS account ID" >&2
      return 1
  fi
  echo $ACCOUNT_ID
}
