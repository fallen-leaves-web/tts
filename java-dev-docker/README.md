# Java 开发环境（Docker）— Mac Apple Silicon

> 适用：MacBook Air M5（ARM64）  
> 思路：**MySQL / Redis / 常用中间件放 Docker**；**Java 项目用本机 IntelliJ IDEA + 本机 JDK** 开发调试。

---

## 一、Mac 上先装 Docker

### 1. 安装 Docker Desktop

1. 打开：https://www.docker.com/products/docker-desktop/  
2. 下载 **Mac with Apple chip** 版本  
3. 安装后打开 Docker Desktop，等状态栏鲸鱼图标显示 **Running**

### 2. 终端验证

```bash
docker --version
docker compose version
docker run --rm hello-world
```

### 3. Mac Air 建议设置（Docker Desktop → Settings）

| 项 | 建议 |
|----|------|
| Resources → Memory | 8GB 机器给 4GB；16GB 给 6～8GB |
| Resources → CPUs | 2～4 核 |
| General | 勾选 Start Docker Desktop when you log in（可选） |

---

## 二、市面上 Java 项目常见组件

| 组件 | 用途 | 本 compose |
|------|------|------------|
| MySQL 8 | 业务库 | ✅ |
| Redis | 缓存、Session、分布式锁 | ✅ |
| Nacos | 注册中心 / 配置中心（微服务） | ✅（可选 profile） |
| RabbitMQ | 消息队列 | ✅（可选 profile） |
| MinIO | 对象存储（文件上传） | ✅（可选 profile） |
| JDK + Maven | 编译运行 | **建议装本机**（IDE 更快） |

微服务项目若不用 Nacos/RabbitMQ，只启 `mysql` + `redis` 即可。

---

## 三、快速启动

```bash
cd java-dev-docker
cp .env.example .env
# 只启 MySQL + Redis（最常用）
docker compose up -d

# 或一次启全部中间件
docker compose --profile full up -d
```

查看状态：

```bash
docker compose ps
```

停止：

```bash
docker compose down
```

数据会保存在 Docker volumes，**down 不会删库**（除非加 `-v`）。

---

## 四、连接信息（默认，可在 .env 修改）

| 服务 | 地址 | 账号 |
|------|------|------|
| MySQL | `localhost:3306` | `root` / `.env` 里 `MYSQL_ROOT_PASSWORD` |
| Redis | `localhost:6379` | 密码见 `REDIS_PASSWORD` |
| Nacos | http://localhost:8848/nacos | `nacos` / `nacos`（profile full） |
| RabbitMQ 管理台 | http://localhost:15672 | `admin` / `.env` 里密码 |
| MinIO 控制台 | http://localhost:9001 | `.env` 里账号 |

### Spring Boot `application-dev.yml` 示例

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/app_db?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai
    username: root
    password: your_mysql_password
  data:
    redis:
      host: localhost
      port: 6379
      password: your_redis_password
```

---

## 五、本机 Java 环境（IDEA）

Docker **不负责写 Java 代码**，本机还需：

```bash
# 用 Homebrew 安装（推荐）
brew install openjdk@17 maven

# 或 SDKMAN
curl -s "https://get.sdkman.io" | bash
sdk install java 17.0.11-tem
sdk install maven
```

- IDE：**IntelliJ IDEA**（Community 或 Ultimate）  
- 新建 Spring Boot 项目，Profile 选 `dev`，数据源指 `localhost`

---

## 六、目录说明

```
java-dev-docker/
├── docker-compose.yml
├── .env.example
├── README.md
└── init-sql/          # MySQL 首次启动自动执行的 SQL
    └── 01-init.sql
```

---

## 七、常见问题（M5 Mac）

| 问题 | 处理 |
|------|------|
| 镜像拉取慢 | Docker Desktop → 配置国内镜像加速（阿里云等） |
| 平台 amd64 警告 | 本 compose 已用 `arm64` 友好镜像；仍报错可加 `platform: linux/amd64`（会慢） |
| 3306 被占用 | `.env` 改 `MYSQL_PORT=3307`，JDBC 端口同步改 |
| Air 风扇响 | 少开服务，只用 `mysql+redis` |
| 连不上 MySQL | 等 `healthy`：`docker compose ps`，或 `docker logs java-mysql` |

---

## 八、和海颐 / 企业项目

入职后问清楚是否还用 **Oracle、达梦、金仓** 等国产库——那些往往不能用这份默认 MySQL compose，需换镜像或连公司 VPN 访问测试库。

---

*下一步：把公司 Java 项目的 `pom.xml`、需要的中间件列表发来，可帮你改成「只启项目需要的服务」的精简版 compose。*
