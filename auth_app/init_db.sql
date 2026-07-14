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