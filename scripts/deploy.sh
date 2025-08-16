#!/bin/bash

set -eu

if [ $# -eq 0 ]; then
    echo "Usage: $0 <dev|prod>"
    exit 1
fi

ENV=$1
if [ "$ENV" != "dev" ] && [ "$ENV" != "prod" ]; then
    echo "Environment must be 'dev' or 'prod'"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/utils.sh"

PROJECT_ROOT=$(find_project_root)
if [ -z "$PROJECT_ROOT" ]; then
    echo "エラー: .ecspressoディレクトリが見つかりません"
    echo "プロジェクトのルートディレクトリに.ecspressoディレクトリが存在することを確認してください"
    exit 1
fi

ECSPRESSO_CONFIG="${PROJECT_ROOT}/.ecspresso/${ENV}/ecspresso.yml"
# 設定ファイルの存在確認
if [ ! -f "$ECSPRESSO_CONFIG" ]; then
    echo "エラー: ecspresso設定ファイルが見つかりません: $ECSPRESSO_CONFIG"
    exit 1
fi

export ACCOUNT_ID=$(login_aws $AWS_PROFILE)
if [ -z "$ACCOUNT_ID" ]; then
    echo "Failed to get AWS account ID" >&2
    exit 1
fi

aws --profile $AWS_PROFILE ecr get-login-password --region ap-northeast-1 |
docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com

COMMIT_HASH=$(git show --format='%h' --no-patch)
TIMESTAMP=$(date '+%s%3')
export IMAGE_TAG=$COMMIT_HASH$TIMESTAMP

if [ "$ENV" = "prod" ]; then
    ECR_REPO="kotohiro-prd-analysis"
else
    ECR_REPO="kotohiro-dev-analysis"
fi

TAG=$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/$ECR_REPO:$IMAGE_TAG

docker build -f server/Dockerfile . -t $TAG --no-cache
docker push $TAG

ecspresso deploy --config "$ECSPRESSO_CONFIG" --force-new-deployment
