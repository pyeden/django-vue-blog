#!/bin/bash
# 在 Mac mini 上执行：安装依赖、迁移、收集静态、切 current、重启 gunicorn
set -euo pipefail
REL="${1:?release name required}"
BASE="/Users/mac/djangovueblog-releases/$REL"
DATA="/Users/mac/djangovueblog-data"
RUNTIME="/Users/mac/djangovueblog-runtime"
PY="$HOME/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12"

mkdir -p "$DATA/logs" "$DATA/media" "$RUNTIME"

if [ ! -x "$RUNTIME/venv/bin/python" ]; then
  echo "==> create venv"
  "$PY" -m venv "$RUNTIME/venv"
fi

echo "==> pip install"
# macOS 系统代理可能指向已失效的端口；安装依赖时强制直连
export no_proxy='*' NO_PROXY='*'
export HTTP_PROXY='' HTTPS_PROXY='' ALL_PROXY=''

"$RUNTIME/venv/bin/pip" install -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip >/dev/null
"$RUNTIME/venv/bin/pip" install -i https://mirrors.aliyun.com/pypi/simple/ -r "$BASE/backend/requirements.txt"

if [ ! -f "$DATA/env" ]; then
  echo "==> create env file"
  SECRET="$("$RUNTIME/venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(50))')"
  cat > "$DATA/env" <<ENV
DJANGO_SETTINGS_MODULE=config.settings
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=$SECRET
DJANGO_ALLOWED_HOSTS=seres-ai.com,127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=https://seres-ai.com
DJANGO_DB_PATH=$DATA/db.sqlite3
DJANGO_MEDIA_ROOT=$DATA/media
DJANGO_STATIC_ROOT=$BASE/staticfiles
DJANGO_STATIC_URL=/djangovueblog/static/
DJANGO_MEDIA_URL=/djangovueblog/media/
PYTHONUNBUFFERED=1
ENV
  chmod 600 "$DATA/env"
fi
# 每个 release 的 static root 不同，更新
sed -i '' "s#^DJANGO_STATIC_ROOT=.*#DJANGO_STATIC_ROOT=$BASE/staticfiles#" "$DATA/env"

echo "==> migrate + collectstatic"
cd "$BASE/backend"
set -a; source "$DATA/env"; set +a
"$RUNTIME/venv/bin/python" manage.py migrate --noinput

if [ ! -f "$DATA/.seeded" ]; then
  echo "==> seed demo data"
  ADMIN_PASS="$("$RUNTIME/venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(18))')"
  printf '%s\n' "$ADMIN_PASS" > "$DATA/admin_password.txt"
  chmod 600 "$DATA/admin_password.txt"
  DJANGO_ADMIN_PASSWORD="$ADMIN_PASS" "$RUNTIME/venv/bin/python" manage.py seed_demo
  touch "$DATA/.seeded"
fi

"$RUNTIME/venv/bin/python" manage.py collectstatic --noinput

echo "==> switch current"
ln -sfn "$BASE" /Users/mac/djangovueblog-releases/current

echo "==> install launcher"
cp "$BASE/deploy/run.sh" "$RUNTIME/run.sh"
chmod +x "$RUNTIME/run.sh"
cp "$BASE/deploy/com.seres.djangovueblog.plist" "$HOME/Library/LaunchAgents/com.seres.djangovueblog.plist"
launchctl bootout "gui/$(id -u)/com.seres.djangovueblog" 2>/dev/null || true
sleep 1
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.seres.djangovueblog.plist" 2>/dev/null || {
  sleep 2
  launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.seres.djangovueblog.plist"
}
launchctl kickstart -k "gui/$(id -u)/com.seres.djangovueblog"

# 目录可读：nginx worker 以 nobody 运行
chmod -R a+rX /Users/mac/djangovueblog-releases "$DATA/media" 2>/dev/null || true

echo "==> health"
for i in $(seq 1 20); do
  if curl --noproxy '*' -fsS http://127.0.0.1:8899/api/health/ >/dev/null; then
    echo "OK http://127.0.0.1:8899/api/health/"
    exit 0
  fi
  sleep 1
done
echo "health check failed" >&2
tail -30 "$DATA/logs/error.log" >&2 || true
exit 1
