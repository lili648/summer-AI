-- ============================================
-- 用户注册系统 - 数据库初始化脚本
-- ============================================

-- 第一步：删除旧数据库
DROP DATABASE IF EXISTS `user_register`;

-- 第二步：新建数据库
CREATE DATABASE `user_register` CHARACTER SET utf8mb4;

-- 第三步：选择数据库
USE `user_register`;

-- 第四步：建表
CREATE TABLE `load_python` (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(20) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(64) NOT NULL COMMENT 'SHA-256密码哈希',
    real_name VARCHAR(50) DEFAULT '未填写' COMMENT '真实姓名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    phone VARCHAR(20) DEFAULT '未填写' COMMENT '手机号',
    gender VARCHAR(10) DEFAULT '保密' COMMENT '性别',
    age_group VARCHAR(20) DEFAULT '' COMMENT '年龄段',
    occupation VARCHAR(20) DEFAULT '请选择' COMMENT '职业',
    interests TEXT COMMENT '兴趣爱好',
    register_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户注册表';
