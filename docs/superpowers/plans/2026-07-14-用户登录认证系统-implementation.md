# 用户登录认证系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于 Streamlit + MySQL + bcrypt 构建内部工具用户认证系统，包含注册、登录、登出和登录态守卫。

**Architecture:** 三层结构 — `database.py`（数据访问层）封装 MySQL CRUD，`auth.py`（业务逻辑层）处理 bcrypt 哈希与登录注册逻辑，`main.py`（表示层）负责 Streamlit UI 与登录态守卫。所有模块通过明确的函数签名接口通信。

**Tech Stack:** Streamlit 1.59.1, MySQL + PyMySQL 1.2.0, bcrypt 5.0.0, pytest

## Global Constraints

- 密码使用 bcrypt 哈希，禁止明文或 SHA-256 存储
- 登录失败统一提示 "用户名或密码错误"，不区分用户不存在/密码错误
- 数据库连接每次操作新建，try/except/finally 中 commit/rollback/close
- 不使用连接池（单用户模式）
- 第一版不做日志文件持久化，异常 print 到 stderr
- 独立测试数据库 `app_auth_test`，每个用例前后清理数据
- 测试不依赖 Streamlit session，直接调用 `auth.py` 函数

---

### Task 1: 数据库初始化脚本

**Files:**
- Create: `auth_app/__init__.py`
- Create: `auth_app/init_db.sql`

**Interfaces:**
- Consumes: nothing
- Produces: SQL 脚本，其他任务手动执行或通过 database.py 引用

- [ ] **Step 1: 创建 auth_app 包目录和 init_db.sql**

创建 `auth_app/` 目录，放入 `__init__.py`（空文件）和 `init_db.sql`：

```sql
-- auth_app/init_db.sql
-- 用户认证系统 - 数据库初始化

CREATE DATABASE IF NOT EXISTS `app_auth`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `app_auth`;

CREATE TABLE IF NOT EXISTS `users` (
    id          INT AUTO_INCREMENT PRIMARY KEY   COMMENT '主键ID',
    username    VARCHAR(50)  NOT NULL UNIQUE     COMMENT '用户名',
    password    VARCHAR(255) NOT NULL             COMMENT 'bcrypt密码哈希',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    last_login  DATETIME     DEFAULT NULL         COMMENT '最后登录时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

- [ ] **Step 2: 执行 SQL 脚本验证**

```bash
mysql -u root -p < auth_app/init_db.sql
```

验证：

```bash
mysql -u root -p -e "DESCRIBE app_auth.users;"
```

预期输出 5 个字段：id, username, password, created_at, last_login

- [ ] **Step 3: 提交**

```bash
git add auth_app/__init__.py auth_app/init_db.sql
git commit -m "feat: 添加用户认证数据库初始化脚本"
```

---

### Task 2: database.py — 数据访问层

**Files:**
- Create: `auth_app/database.py`
- Test file will be created in Task 6

**Interfaces:**
- Consumes: MySQL 数据库 `app_auth`（通过 Task 1 脚本创建）
- Produces:
  - `get_conn() -> pymysql.Connection` — 获取数据库连接
  - `find_user(username: str) -> dict | None` — 按用户名查询，返回包含 id, username, password, created_at, last_login 的字典
  - `insert_user(username: str, password_hash: str) -> None` — 插入新用户，用户名重复时抛出 pymysql.IntegrityError
  - `update_last_login(username: str) -> None` — 更新 last_login 为 NOW()

- [ ] **Step 1: 创建 auth_app/database.py**

```python
# auth_app/database.py
"""用户认证系统 - 数据访问层"""
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Liyizhang_10",
    "database": "app_auth",
    "charset": "utf8mb4",
}


def get_conn():
    """获取 MySQL 数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def find_user(username: str) -> dict | None:
    """按用户名查询用户，返回用户记录字典；不存在则返回 None"""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, created_at, last_login "
            "FROM users WHERE username = %(username)s",
            {"username": username},
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "password": row[2],
            "created_at": row[3],
            "last_login": row[4],
        }
    finally:
        conn.close()


def insert_user(username: str, password_hash: str) -> None:
    """插入新用户，用户名重复时抛出 pymysql.IntegrityError"""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%(username)s, %(password)s)",
            {"username": username, "password": password_hash},
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_last_login(username: str) -> None:
    """更新指定用户的最后登录时间为当前时间"""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = NOW() WHERE username = %(username)s",
            {"username": username},
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

- [ ] **Step 2: 手动验证导入**

```bash
cd auth_app && python -c "from database import get_conn; conn = get_conn(); print('OK:', conn); conn.close()"
```

预期输出：OK: <pymysql.connections.Connection object at ...>

- [ ] **Step 3: 提交**

```bash
git add auth_app/database.py
git commit -m "feat: 添加数据访问层 database.py"
```

---

### Task 3: auth.py — 认证逻辑层

**Files:**
- Create: `auth_app/auth.py`

**Interfaces:**
- Consumes: `auth_app/database.py` 的 `find_user`, `insert_user`, `update_last_login`
- Produces:
  - `hash_password(password: str) -> str` — bcrypt 哈希，返回字符串
  - `verify_password(password: str, password_hash: str) -> bool` — 验证明文与哈希是否匹配
  - `register(username: str, password: str) -> tuple[bool, str]` — 注册逻辑
  - `login(username: str, password: str) -> tuple[bool, str]` — 登录逻辑，成功时设置 `st.session_state["user"]`
  - `logout() -> None` — 清除 `st.session_state["user"]`
  - `get_current_user() -> str | None` — 从 session 获取当前用户名

- [ ] **Step 1: 创建 auth_app/auth.py**

```python
# auth_app/auth.py
"""用户认证系统 - 业务逻辑层"""
import bcrypt
import pymysql
import streamlit as st

from database import find_user, insert_user, update_last_login


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希"""
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """验证明文密码与 bcrypt 哈希是否匹配"""
    return bcrypt.checkpw(
        password.encode("utf-8"), password_hash.encode("utf-8")
    )


def register(username: str, password: str) -> tuple[bool, str]:
    """注册新用户，返回 (成功与否, 提示消息)"""
    # 校验非空
    if not username or not password:
        return False, "用户名和密码不能为空"
    # 校验密码长度
    if len(password) < 6:
        return False, "密码至少需要 6 位"
    # 校验用户名不重复
    if find_user(username) is not None:
        return False, "该用户名已被注册"
    # bcrypt 哈希并写入
    try:
        hashed = hash_password(password)
        insert_user(username, hashed)
        return True, "注册成功！请登录"
    except pymysql.IntegrityError:
        return False, "该用户名已被注册"
    except Exception:
        return False, "系统错误，请联系管理员"


def login(username: str, password: str) -> tuple[bool, str]:
    """验证用户登录，成功时写入 session，返回 (成功与否, 提示消息)"""
    # 校验非空
    if not username or not password:
        return False, "用户名和密码不能为空"
    # 查用户
    user = find_user(username)
    if user is None:
        return False, "用户名或密码错误"
    # 验证密码
    if not verify_password(password, user["password"]):
        return False, "用户名或密码错误"
    # 登录成功
    st.session_state["user"] = username
    try:
        update_last_login(username)
    except Exception:
        pass  # 更新登录时间失败不影响正常登录
    return True, "登录成功"


def logout() -> None:
    """清除登录会话"""
    st.session_state.pop("user", None)


def get_current_user() -> str | None:
    """获取当前登录用户名，未登录返回 None"""
    return st.session_state.get("user", None)
```

- [ ] **Step 2: 手动验证导入**

```bash
cd auth_app && python -c "from auth import hash_password, verify_password; h = hash_password('test'); print('hash:', h); print('verify:', verify_password('test', h))"
```

预期输出：hash: $2b$12$... verify: True

- [ ] **Step 3: 提交**

```bash
git add auth_app/auth.py
git commit -m "feat: 添加认证逻辑层 auth.py"
```

---

### Task 4: main.py — Streamlit 入口与页面路由

**Files:**
- Create: `auth_app/main.py`

**Interfaces:**
- Consumes: `auth_app/auth.py` 的 `login`, `register`, `logout`, `get_current_user`
- Produces: Streamlit 应用入口，streamlit run 直接启动

- [ ] **Step 1: 创建 auth_app/main.py**

```python
# auth_app/main.py
"""用户认证系统 - Streamlit 入口与页面路由"""
import streamlit as st

from auth import login, register, logout, get_current_user

st.set_page_config(
    page_title="内部工具用户认证",
    page_icon="🔐",
    layout="centered",
)

# ====== 登录态守卫 ======
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"]:
    # ====== 已登录：显示主功能页面 ======
    with st.sidebar:
        st.write(f"👤 当前登录：**{st.session_state['user']}**")
        st.divider()
        if st.button("🚪 登出", use_container_width=True):
            logout()
            st.rerun()

    st.title("🏠 主功能页面")
    st.success(f"欢迎，**{st.session_state['user']}**！")
    st.write("在此处添加业务功能内容。")

else:
    # ====== 未登录：显示登录 / 注册 Tab ======
    st.title("🔐 内部工具用户认证")

    tab_login, tab_register = st.tabs(["登录", "注册"])

    with tab_login:
        st.subheader("用户登录")
        login_username = st.text_input("用户名", key="login_username")
        login_password = st.text_input(
            "密码", type="password", key="login_password"
        )

        if st.button("登  录", type="primary", use_container_width=True):
            ok, msg = login(login_username, login_password)
            if ok:
                st.rerun()
            else:
                st.error(msg)

    with tab_register:
        st.subheader("用户注册")
        reg_username = st.text_input("用户名", key="reg_username")
        reg_password = st.text_input(
            "密码", type="password", key="reg_password",
            help="至少 6 位"
        )
        reg_confirm = st.text_input(
            "确认密码", type="password", key="reg_confirm",
        )

        if st.button("注  册", type="primary", use_container_width=True):
            if reg_password != reg_confirm:
                st.error("两次输入的密码不一致")
            else:
                ok, msg = register(reg_username, reg_password)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
```

- [ ] **Step 2: 启动应用验证**

```bash
cd auth_app && streamlit run main.py
```

验证内容：
- 登录 Tab 默认显示，用户名密码输入框和登录按钮可见
- 切换到注册 Tab，注册表单可见
- 注册一个测试用户（如 testuser / abc123），提示"注册成功！请登录"
- 切换回登录 Tab，用刚注册的账号登录，成功跳转到主功能页面
- 侧边栏显示用户名，点击"登出"按钮能正常退出回到登录页

- [ ] **Step 3: 提交**

```bash
git add auth_app/main.py
git commit -m "feat: 添加 Streamlit 入口与页面路由 main.py"
```

---

### Task 5: 测试 - hash_password 与 verify_password 单元测试

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_auth.py`

**Interfaces:**
- Consumes: `auth_app/auth.py` 的 `hash_password`, `verify_password`
- Produces: pytest 测试用例 UT-01 ~ UT-04

- [ ] **Step 1: 创建测试目录和测试文件**

```bash
mkdir -p tests
```

创建 `tests/__init__.py`（空文件）。

创建 `tests/test_auth.py`：

```python
# tests/test_auth.py
"""auth.py 单元测试 - hash_password & verify_password"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "auth_app"))

from auth import hash_password, verify_password


class TestHashPassword:
    """UT-01, UT-04"""

    def test_hash_password_returns_bcrypt_string(self):
        """UT-01: hash_password 返回 60 字符 bcrypt 哈希"""
        result = hash_password("abc123")
        assert isinstance(result, str)
        assert result.startswith("$2b$")
        assert len(result) == 60

    def test_hash_password_is_salted(self):
        """UT-04: 两次哈希同一密码产生不同结果（随机盐）"""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2
        # 但验证都通过
        assert verify_password("same", h1) is True
        assert verify_password("same", h2) is True


class TestVerifyPassword:
    """UT-02, UT-03"""

    def test_verify_correct_password_returns_true(self):
        """UT-02: 正确密码验证返回 True"""
        h = hash_password("abc123")
        assert verify_password("abc123", h) is True

    def test_verify_wrong_password_returns_false(self):
        """UT-03: 错误密码验证返回 False"""
        h = hash_password("abc123")
        assert verify_password("wrong", h) is False
```

- [ ] **Step 2: 运行测试验证通过**

```bash
pytest tests/test_auth.py -v
```

预期：4 passed

- [ ] **Step 3: 提交**

```bash
git add tests/__init__.py tests/test_auth.py
git commit -m "test: 添加 hash_password 与 verify_password 单元测试"
```

---

### Task 6: 测试 - database.py 单元测试

**Files:**
- Create: `tests/test_database.py`
- Create: `tests/conftest.py`

**Interfaces:**
- Consumes: `auth_app/database.py` 的 `get_conn`, `find_user`, `insert_user`, `update_last_login`
- Produces: pytest 测试用例 UT-05 ~ UT-08

- [ ] **Step 1: 创建测试数据库**

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS app_auth_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "
USE app_auth_test;
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"
```

- [ ] **Step 2: 创建 tests/conftest.py**

```python
# tests/conftest.py
"""pytest 配置 - 测试数据库使用 app_auth_test"""
import sys
import os

# 确保 auth_app 在 path 中，且使用测试数据库
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "auth_app"))

import database

# 切换到测试数据库
database.DB_CONFIG["database"] = "app_auth_test"


def clean_users():
    """清空测试用户表"""
    conn = database.get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        conn.commit()
    finally:
        conn.close()
```

- [ ] **Step 3: 创建 tests/test_database.py**

```python
# tests/test_database.py
"""database.py 单元测试 - find_user, insert_user, update_last_login"""
import pytest
import pymysql
from conftest import clean_users
from database import find_user, insert_user, update_last_login


TEST_HASH = "$2b$12$LJ3m4ys3GZfnYMz8kVsKaOTSxGxhLBtsFOeMKP1N3YPRjvDsJUq6q"


class TestInsertAndFindUser:
    """UT-05, UT-06"""

    def setup_method(self):
        clean_users()

    def teardown_method(self):
        clean_users()

    def test_insert_and_find_user(self):
        """UT-05: 插入后查询返回正确记录"""
        insert_user("test", TEST_HASH)
        user = find_user("test")
        assert user is not None
        assert user["username"] == "test"
        assert user["password"] == TEST_HASH
        assert user["last_login"] is None

    def test_insert_duplicate_raises_error(self):
        """UT-06: 重复用户名抛出 IntegrityError"""
        insert_user("test", TEST_HASH)
        with pytest.raises(pymysql.IntegrityError):
            insert_user("test", TEST_HASH)


class TestFindUser:
    """UT-07"""

    def setup_method(self):
        clean_users()

    def teardown_method(self):
        clean_users()

    def test_find_nonexistent_user_returns_none(self):
        """UT-07: 查找不存在的用户返回 None"""
        result = find_user("nonexist")
        assert result is None


class TestUpdateLastLogin:
    """UT-08"""

    def setup_method(self):
        clean_users()

    def teardown_method(self):
        clean_users()

    def test_update_last_login(self):
        """UT-08: 更新最后登录时间"""
        insert_user("test", TEST_HASH)
        update_last_login("test")
        user = find_user("test")
        assert user is not None
        assert user["last_login"] is not None
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_database.py -v
```

预期：4 passed

- [ ] **Step 5: 提交**

```bash
git add tests/conftest.py tests/test_database.py
git commit -m "test: 添加 database.py 数据访问层单元测试"
```

---

### Task 7: 测试 - auth.py 注册与登录集成测试

**Files:**
- Modify: `tests/test_auth.py`（追加注册和登录测试类）

**Interfaces:**
- Consumes: `auth_app/auth.py` 的 `register`, `login`, `logout`, `get_current_user`；`tests/conftest.py` 的 `clean_users`
- Produces: pytest 测试用例 IT-01 ~ IT-09

- [ ] **Step 1: 在 tests/test_auth.py 末尾追加测试类**

```python
# 追加到 tests/test_auth.py 末尾

from conftest import clean_users
from auth import register, login, get_current_user
import streamlit as st


class TestRegister:
    """IT-01 ~ IT-05"""

    def setup_method(self):
        clean_users()
        # 清空 session
        st.session_state.pop("user", None)

    def teardown_method(self):
        clean_users()
        st.session_state.pop("user", None)

    def test_register_success(self):
        """IT-01: 正常注册成功"""
        ok, msg = register("newuser", "abc123")
        assert ok is True
        assert msg == "注册成功！请登录"
        # 确认数据库有记录
        from database import find_user
        user = find_user("newuser")
        assert user is not None
        assert user["username"] == "newuser"

    def test_register_duplicate_username(self):
        """IT-02: 用户名已存在"""
        register("existing", "abc123")
        ok, msg = register("existing", "xyz456")
        assert ok is False
        assert msg == "该用户名已被注册"

    def test_register_password_too_short(self):
        """IT-03: 密码不足 6 位"""
        ok, msg = register("user", "abc")
        assert ok is False
        assert msg == "密码至少需要 6 位"

    def test_register_empty_username(self):
        """IT-04: 用户名为空"""
        ok, msg = register("", "abc123")
        assert ok is False
        assert msg == "用户名和密码不能为空"

    def test_register_empty_password(self):
        """IT-05: 密码为空"""
        ok, msg = register("user", "")
        assert ok is False
        assert msg == "用户名和密码不能为空"


class TestLogin:
    """IT-06 ~ IT-09"""

    def setup_method(self):
        clean_users()
        st.session_state.pop("user", None)
        # 预先注册一个用户
        register("testuser", "abc123")

    def teardown_method(self):
        clean_users()
        st.session_state.pop("user", None)

    def test_login_success(self):
        """IT-06: 正确用户名 + 正确密码"""
        ok, msg = login("testuser", "abc123")
        assert ok is True
        assert msg == "登录成功"
        assert get_current_user() == "testuser"

    def test_login_wrong_password(self):
        """IT-07: 正确用户名 + 错误密码"""
        ok, msg = login("testuser", "wrongpass")
        assert ok is False
        assert msg == "用户名或密码错误"
        assert get_current_user() is None

    def test_login_nonexistent_user(self):
        """IT-08: 不存在的用户名"""
        ok, msg = login("ghost", "abc123")
        assert ok is False
        assert msg == "用户名或密码错误"
        assert get_current_user() is None

    def test_login_empty_input(self):
        """IT-09: 空用户名或空密码"""
        ok, msg = login("", "")
        assert ok is False
        assert msg == "用户名和密码不能为空"
        assert get_current_user() is None
```

- [ ] **Step 2: 运行全部测试验证通过**

```bash
pytest tests/ -v
```

预期：17 passed（4 + 4 + 9）

- [ ] **Step 3: 提交**

```bash
git add tests/test_auth.py
git commit -m "test: 添加注册与登录集成测试"
```

---

### Task 8: 最终手工验证与清理

**Files:**
- 不新建文件，对现有文件做验证

- [ ] **Step 1: 确认测试数据库使用生产配置**

确认 `auth_app/database.py` 中 `DB_CONFIG["database"]` 是 `"app_auth"`（生产库），而非 `"app_auth_test"`。

- [ ] **Step 2: 执行生产数据库建表**

```bash
mysql -u root -p < auth_app/init_db.sql
```

- [ ] **Step 3: 运行全部自动化测试**

```bash
pytest tests/ -v
```

预期：17 passed

- [ ] **Step 4: 启动应用手工验证完整流程**

```bash
cd auth_app && streamlit run main.py
```

验证清单：
- [ ] 打开浏览器，看到登录页面，默认是"登录"Tab
- [ ] 切换到"注册"Tab，输入新用户名和密码，点击注册，提示"注册成功！请登录"
- [ ] 切换回"登录"Tab，输入刚注册的账号，点击登录，成功跳转主功能页面
- [ ] 侧边栏显示当前用户名
- [ ] 点击"登出"按钮，回到登录页
- [ ] 输入错误密码，提示"用户名或密码错误"
- [ ] 输入不存在用户名，提示"用户名或密码错误"（不区分）
- [ ] 空输入点击登录，提示"用户名和密码不能为空"

- [ ] **Step 5: 测试服务重启后 session 失效**

关闭并重新运行 `streamlit run main.py`，确认需要重新登录（session 已清空）。

- [ ] **Step 6: 最终提交**

```bash
git add -A
git commit -m "chore: 最终验证完成，用户认证系统就绪"
```