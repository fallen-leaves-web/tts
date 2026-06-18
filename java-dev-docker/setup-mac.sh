#!/bin/bash
# Mac 一键创建 docker-compose.yml、.env 等文件
set -e

DIR="${1:-$HOME/dev/java-dev-docker}"
mkdir -p "$DIR/init-sql"

cat > "$DIR/docker-compose.yml" << 'EOF'
services:
  mysql:
    image: mysql:8.0
    container_name: java-mysql
    restart: unless-stopped
    ports:
      - "${MYSQL_PORT:-3306}:3306"
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-dev123456}
      MYSQL_DATABASE: ${MYSQL_DATABASE:-app_db}
      TZ: Asia/Shanghai
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init-sql:/docker-entrypoint-initdb.d:ro
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci

  redis:
    image: redis:7-alpine
    container_name: java-redis
    restart: unless-stopped
    ports:
      - "${REDIS_PORT:-6379}:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD:-dev123456}
    volumes:
      - redis_data:/data

volumes:
  mysql_data:
  redis_data:
EOF

cat > "$DIR/.env" << 'EOF'
MYSQL_ROOT_PASSWORD=dev123456
MYSQL_DATABASE=app_db
MYSQL_PORT=3306
REDIS_PASSWORD=dev123456
REDIS_PORT=6379
EOF

cat > "$DIR/init-sql/01-init.sql" << 'EOF'
CREATE DATABASE IF NOT EXISTS app_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

echo "✅ 已创建："
echo "   $DIR/docker-compose.yml"
echo "   $DIR/.env"
echo "   $DIR/init-sql/01-init.sql"
echo ""
echo "启动命令："
echo "   cd $DIR && docker compose up -d"
