#!/bin/bash
# 本地/生产 API 冒烟。用法：BASE=http://127.0.0.1:8000 ./qa/smoke_api.sh
set -euo pipefail
BASE="${BASE:-http://127.0.0.1:8000}"
JAR="$(mktemp)"
trap 'rm -f "$JAR"' EXIT

jget() { python3 -c "import json,sys; d=json.load(sys.stdin); print(eval(sys.argv[1]))" "$1"; }
pass=0; fail=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then echo "PASS $1 ($3)"; pass=$((pass+1)); else echo "FAIL $1 expected=$2 actual=$3"; fail=$((fail+1)); fi
}
code() { curl -s -o /dev/null -w "%{http_code}" -b "$JAR" -c "$JAR" "$@"; }

check "home api" 200 "$(code "$BASE/api/articles/")"
check "hot" 200 "$(code "$BASE/api/articles/hot/")"
check "columns" 200 "$(code "$BASE/api/columns/")"
check "tags" 200 "$(code "$BASE/api/tags/")"

curl -s -b "$JAR" -c "$JAR" "$BASE/api/auth/csrf/" >/dev/null
CSRF=$(awk '$6=="csrftoken" {print $7}' "$JAR")
[ -n "$CSRF" ] && echo "PASS csrf cookie" && pass=$((pass+1)) || { echo "FAIL csrf cookie"; fail=$((fail+1)); }

LOGIN=$(curl -s -b "$JAR" -c "$JAR" -H "Content-Type: application/json" -H "X-CSRFToken: $CSRF" -H "Referer: $BASE/" \
  -d '{"username":"demo","password":"demo12345"}' "$BASE/api/auth/login/")
USER=$(echo "$LOGIN" | jget "d['user']['username']" 2>/dev/null || echo none)
check "login demo" demo "$USER"

# Django 在 login 后会轮换 CSRF token，重新取一次
curl -s -b "$JAR" -c "$JAR" "$BASE/api/auth/csrf/" >/dev/null
CSRF=$(awk '$6=="csrftoken" {print $7}' "$JAR")

SLUG=$(curl -s "$BASE/api/articles/" | jget "d['results'][0]['slug']")
check "article detail" 200 "$(code "$BASE/api/articles/$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$SLUG")/")"
check "article comments" 200 "$(code "$BASE/api/articles/$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$SLUG")/comments/")"

TITLE="QA $(date +%s)"
CREATE=$(curl -s -b "$JAR" -c "$JAR" -H "Content-Type: application/json" -H "X-CSRFToken: $CSRF" -H "Referer: $BASE/" \
  -d "{\"title\":\"$TITLE\",\"body\":\"# $TITLE\\n\\n冒烟测试\",\"tags\":[\"QA\"]}" "$BASE/api/articles/")
NEW_SLUG=$(echo "$CREATE" | jget "d['slug']" 2>/dev/null || echo none)
[ "$NEW_SLUG" != none ] && echo "PASS create article" && pass=$((pass+1)) || { echo "FAIL create article: $CREATE"; fail=$((fail+1)); }
NEW_PATH="$BASE/api/articles/$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$NEW_SLUG")"
check "patch article" 200 "$(code -X PATCH -H "Content-Type: application/json" -H "X-CSRFToken: $CSRF" -H "Referer: $BASE/" -d '{"title":"QA patched"}' "$NEW_PATH/")"
check "like 1" 200 "$(code -X POST -H "X-CSRFToken: $CSRF" -H "Referer: $BASE/" "$NEW_PATH/like/")"
check "like 2" 200 "$(code -X POST -H "X-CSRFToken: $CSRF" -H "Referer: $BASE/" "$NEW_PATH/like/")"
check "comment create" 201 "$(code -X POST -H "Content-Type: application/json" -H "X-CSRFToken: $CSRF" -H "Referer: $BASE/" -d '{"body":"QA 评论"}' "$NEW_PATH/comments/")"
check "delete article" 204 "$(code -X DELETE -H "X-CSRFToken: $CSRF" -H "Referer: $BASE/" "$NEW_PATH/")"
check "search" 200 "$(code "$BASE/api/articles/?search=QA")"
check "notifications" 200 "$(code "$BASE/api/notifications/")"
check "me" 200 "$(code "$BASE/api/auth/me/")"

echo "----"
echo "PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ]
