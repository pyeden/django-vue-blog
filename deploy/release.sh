#!/bin/bash
# 在 MacBook 上执行：构建前端 + 打包后端 + 推送到 Mac mini
set -euo pipefail
ROOT="$HOME/work/django-vue-blog"
TS="$(date +%Y%m%d-%H%M%S)"
SHA="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo nogit)"
REL="$TS-$SHA"

echo "==> build frontend ($REL)"
cd "$ROOT/frontend"
VITE_BASE=/djangovueblog/ VITE_API_BASE=/djangovueblog/api npm run build

echo "==> package"
STAGE="/tmp/dvb-$REL"
rm -rf "$STAGE"
mkdir -p "$STAGE/frontend/djangovueblog" "$STAGE/backend" "$STAGE/deploy"
rsync -a --delete "$ROOT/frontend/dist/" "$STAGE/frontend/djangovueblog/"
rsync -a --exclude .venv --exclude db.sqlite3 --exclude '__pycache__' --exclude '*.pyc' --exclude logs --exclude media --exclude staticfiles \
  "$ROOT/backend/" "$STAGE/backend/"
cp "$ROOT/deploy/remote_install.sh" "$ROOT/deploy/run.sh" "$ROOT/deploy/com.seres.djangovueblog.plist" \
  "$ROOT/deploy/nginx-djangovueblog.conf" "$STAGE/deploy/"

echo "==> upload to Mac mini"
ssh codinglog-deploy "mkdir -p /Users/mac/djangovueblog-releases/$REL"
rsync -a "$STAGE/" "codinglog-deploy:/Users/mac/djangovueblog-releases/$REL/"

echo "==> remote install"
ssh codinglog-deploy "bash /Users/mac/djangovueblog-releases/$REL/deploy/remote_install.sh $REL"

echo "==> done: $REL"
