# 2RBAC基础 - 基于角色的访问控制

## 1. 🎯 问题与背景 (The Problem & Context)

> **工程视角:** *"权限管理的噩梦在于：当人员变动或规则调整时，我们是否需要修改代码或逐一调整每个用户的配置？"*

*   **痛点分析:** 
    *   **DAC (自主访问控制) 的混乱:** 早期的系统可能直接将权限赋予用户（User A -> 读文件1, User B -> 读文件1）。
    *   **维护成本爆炸:** 当公司新来一个“财务专员”，你需要手动给他勾选 50 个权限。如果“财务专员”的职责变了，你需要去更新系统里 100 个财务人员的权限。这在企业级应用中是不可接受的。
*   **核心定义:** 
    *   **RBAC (Role-Based Access Control):** 一种通过引入“角色(Role)”作为中间层，将**用户(User)**与**权限(Permission)**解耦的访问控制策略。
    *   **核心公式:** `User <-> Role <-> Permission`。

## 2. 🧩 抽象与心智模型 (The Mental Model)

> **设计视角:** *"角色是职能的抽象，权限是资源的钥匙。"*

*   **生活类比 (公司门禁卡):**
    *   公司不会给每位员工单独设置每个门的开关权限。
    *   公司会定义几种工牌（**角色**）：普通员工卡、经理卡、保洁卡。
    *   **普通员工卡**可以开大门、食堂门（**权限**）。
    *   **保洁卡**可以开大门、清洁间、仓库门（**权限**）。
    *   张三（**用户**）入职时，HR 只需要发给他一张“普通员工卡”（**赋予角色**），他就自动拥有了对应的所有开门权限。
    *   如果以后“普通员工卡”允许进入健身房，只需要修改卡片的定义，所有持卡人自动生效。

*   **抽象设计 (多对多关系):**
    *   这是一个经典的**双向多对多**模型。
    *   一个用户可以拥有多个角色（既是‘项目经理’也是‘技术委员会成员’）。
    *   一个角色可以包含多个权限（‘增’、‘删’、‘改’、‘查’）。
    *   反之亦然。

## 3. 🏗️ 系统架构与设计 (System & Architecture)

> **架构视角:** *"数据模型的设计决定了系统的灵活性。"*

*   **在系统中的位置:** 
    *   **数据层 (Data Layer):** 核心体现为 5 张数据库表的设计。
    *   **业务层 (Service Layer):** 提供“分配角色”、“校验权限”的接口。

*   **关键组件 (RBAC 核心五表模型):**
    这是最经典的 RBAC1 模型设计：

    1.  **用户表 (sys_user):** 存储用户基本信息 (id, username, password)。
    2.  **角色表 (sys_role):** 存储角色定义 (id, role_name, role_code)。
    3.  **权限/菜单表 (sys_menu / sys_permission):** 存储资源和操作 (id, perm_name, url, permission_code)。
        *   *注: 现代设计常将菜单结构与操作权限合并存储，通过 parent_id 维护树形结构。*
    4.  **用户-角色关联表 (sys_user_role):** 映射用户与角色的关系 (user_id, role_id)。
    5.  **角色-权限关联表 (sys_role_menu):** 映射角色与权限的关系 (role_id, menu_id)。

*   **设计模式:**
    *   **组合模式 (Composite Pattern):** 权限/菜单通常是树形结构（一级菜单 -> 二级菜单 -> 按钮），适合用组合模式处理层级。

## 4. 💻 核心实现 (Implementation)

> **落地视角:** *"SQL 是 RBAC 的灵魂。"*

```sql
-- 1. 用户表
CREATE TABLE sys_user (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    -- ...
);

-- 2. 角色表
CREATE TABLE sys_role (
    id BIGINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL, -- 如 "管理员"
    code VARCHAR(50) NOT NULL  -- 如 "ROLE_ADMIN"
);

-- 3. 权限表 (资源)
CREATE TABLE sys_permission (
    id BIGINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL, -- 如 "用户查询"
    permission_code VARCHAR(50) NOT NULL -- 如 "user:view" (Shiro/SpringSecurity 常用格式)
);

-- 4. 关联表：用户 -> 角色
CREATE TABLE sys_user_role (
    user_id BIGINT,
    role_id BIGINT,
    PRIMARY KEY(user_id, role_id)
);

-- 5. 关联表：角色 -> 权限
CREATE TABLE sys_role_permission (
    role_id BIGINT,
    permission_id BIGINT,
    PRIMARY KEY(role_id, permission_id)
);
```

```java
// Java 伪代码：在登录时查询用户所有权限
// Service 层逻辑
public Set<String> getUserPermissions(Long userId) {
    // 1. 根据 userId 查 sys_user_role 得到 roleId 列表
    List<Long> roleIds = userRoleMapper.selectRoleIdsByUserId(userId);
    
    // 2. 根据 roleIds 查 sys_role_permission 得到 permissionId 列表
    List<Long> permIds = rolePermissionMapper.selectPermIdsByRoleIds(roleIds);
    
    // 3. 根据 permIds 查 sys_permission 得到 permission_code
    List<String> codes = permissionMapper.selectCodesByIds(permIds);
    
    // 结果示例: ["user:add", "user:view", "order:export"]
    return new HashSet<>(codes);
}
```

## 5. ⚖️ 工程权衡与局限 (Trade-offs & Constraints)

> **工程视角:** *"RBAC 是基石，但不是终点。"*

*   **优点 (Pros):**
    *   **简化管理:** 极大地降低了用户授权的复杂度。
    *   **职责分离:** 角色对应组织架构中的职位，易于理解和映射。
    *   **扩展性:** 支持 RBAC0 (基础), RBAC1 (角色继承), RBAC2 (职责分离约束) 等变体。

*   **局限 (Cons) 与 扩展挑战:**
    *   **粒度不够细:** 传统的 RBAC 控制的是“能不能访问某个功能（API/菜单）”，但很难控制“能不能访问**数据**”。
        *   *场景:* 销售经理和销售员都有“查看订单”的角色权限，但销售员只能看*自己*的订单，经理能看*部门*的订单。单纯的 RBAC 无法解决**数据权限**问题。
    *   **角色爆炸:** 如果系统非常复杂，可能导致定义了数百个特定角色，管理又变得混乱。

## 6. 🌐 深度联想与扩展 (Deep Dive & Connections)

> **通识视角:** *"权限控制的未来是属性和动态策略。"*

*   **ABAC (Attribute-Based Access Control):** 
    *   当 RBAC 不够用时，我们引入 ABAC。基于**属性**（用户属性、环境属性、资源属性）的控制。
    *   *规则:* “允许（用户.部门 == 资源.部门）且（时间 > 9:00）的请求”。
    *   这是 AWS IAM Policy 等云原生权限系统的基础。

### 思考题解答: 数据权限通用方案

**问题:** 如何在现有的 RBAC 5张表基础上，设计一个通用的**数据权限**方案？

**核心思路:** 功能权限控制的是 **"Can Do"** (URL/Method)，数据权限控制的是 **"Where"** (SQL WHERE clause)。

**方案 1: 简单的 Scope 字段扩展 (最常用)**
在 `sys_role` 或 `sys_user_role` 表中增加一个 `data_scope` 字段。
*   `data_scope` 枚举值:
    1.  `ALL`: 全部数据
    2.  `DEPT_AND_CHILD`: 本部门及子部门数据
    3.  `DEPT`: 本部门数据
    4.  `SELF`: 仅本人数据
    5.  `CUSTOM`: 自定义（关联部门ID列表）

**方案 2: AOP + MyBatis 拦截器 (技术实现)**
1.  **定义注解:** `@DataScope(deptAlias = "d", userAlias = "u")` 标注在 Mapper 方法上。
2.  **拦截器逻辑:** MyBatis 拦截器拦截带有该注解的 SQL。
3.  **动态 SQL 拼接:**
    *   拦截器读取当前登录用户的 `data_scope` 和 `dept_id`。
    *   如果是 `SELF`，自动在 SQL 后追加 `AND u.user_id = {current_user_id}`。
    *   如果是 `DEPT`，自动追加 `AND d.dept_id = {current_dept_id}`。
4.  **结果:** 业务代码无需写任何权限过滤逻辑，SQL 自动加上了过滤条件。
