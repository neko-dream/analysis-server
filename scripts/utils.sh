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

urlencode() {
    local string="${1}"
    local strlen=${#string}
    local encoded=""
    local pos c o

    for (( pos=0 ; pos<strlen ; pos++ )); do
        c=${string:$pos:1}
        case "$c" in
            [-_.~a-zA-Z0-9] ) o="${c}" ;;
            * ) printf -v o '%%%02x' "'$c" ;;
        esac
        encoded+="${o}"
    done
    echo "${encoded}"
}
