# Windows 多GitHub账号配置指南

> 本文档详细介绍如何在Windows 11环境下同时使用多个GitHub账号（如公司账号和个人账号）。

## 目录

- [场景说明](#场景说明)
- [前置条件](#前置条件)
- [配置步骤](#配置步骤)
  - [步骤1：生成SSH密钥](#步骤1生成ssh密钥)
  - [步骤2：将公钥添加到GitHub](#步骤2将公钥添加到github)
  - [步骤3：配置SSH config文件](#步骤3配置ssh-config文件)
  - [步骤4：测试SSH连接](#步骤4测试ssh连接)
- [使用指南](#使用指南)
  - [克隆新项目](#克隆新项目)
  - [配置仓库用户信息](#配置仓库用户信息)
  - [修改已有项目的远程地址](#修改已有项目的远程地址)
- [常见场景](#常见场景)
  - [场景1：已用个人账号克隆项目，如何用公司账号克隆另一个项目](#场景1已用个人账号克隆项目如何用公司账号克隆另一个项目)
  - [场景2：已有项目需要切换账号](#场景2已有项目需要切换账号)
  - [场景3：全局默认使用公司账号](#场景3全局默认使用公司账号)
- [常见问题](#常见问题)
- [附录：命令速查表](#附录命令速查表)

---

## 场景说明

假设你有两个GitHub账号：

| 账号类型 | 账号名称 | 邮箱 | 用途 |
|---------|---------|------|------|
| 账号A（默认） | company-user | work@company.com | 公司项目 |
| 账号B | personal-user | personal@gmail.com | 个人项目 |

目标：让Git能够根据不同的项目自动使用对应的账号进行操作。

---

## 前置条件

1. Windows 11 系统
2. 已安装 Git for Windows
3. 拥有两个GitHub账号

验证Git安装：

```powershell
git --version
```

---

## 配置步骤

### 步骤1：生成SSH密钥

打开 PowerShell 或 Git Bash，为每个账号生成独立的SSH密钥。

**生成公司账号密钥（账号A）：**

```bash
ssh-keygen -t ed25519 -C "work@company.com" -f ~/.ssh/id_ed25519_company
```

**生成个人账号密钥（账号B）：**

```bash
ssh-keygen -t ed25519 -C "personal@gmail.com" -f ~/.ssh/id_ed25519_personal
```

**说明：**
- `-t ed25519`：使用ed25519算法（推荐，更安全更快）
- `-C`：添加注释，一般填写邮箱便于识别
- `-f`：指定密钥文件路径和名称

生成时会提示输入密码（passphrase），可以直接回车跳过，也可以设置密码增加安全性。

**验证密钥生成成功：**

```powershell
# 查看生成的密钥文件
ls ~/.ssh/

# 应该看到以下文件：
# id_ed25519_company      （公司账号私钥）
# id_ed25519_company.pub  （公司账号公钥）
# id_ed25519_personal     （个人账号私钥）
# id_ed25519_personal.pub （个人账号公钥）
```

---

### 步骤2：将公钥添加到GitHub

#### 2.1 复制公钥内容

**PowerShell方式：**

```powershell
# 复制公司账号公钥
Get-Content ~/.ssh/id_ed25519_company.pub | Set-Clipboard

# 复制个人账号公钥
Get-Content ~/.ssh/id_ed25519_personal.pub | Set-Clipboard
```

**Git Bash方式：**

```bash
# 复制公司账号公钥
cat ~/.ssh/id_ed25519_company.pub | clip

# 复制个人账号公钥
cat ~/.ssh/id_ed25519_personal.pub | clip
```

#### 2.2 添加到GitHub

1. 登录**公司GitHub账号**
2. 点击右上角头像 → **Settings**
3. 左侧菜单选择 **SSH and GPG keys**
4. 点击 **New SSH key**
5. 填写：
   - Title：`Company-Windows`（自定义名称，便于识别）
   - Key type：`Authentication Key`
   - Key：粘贴公司账号的公钥内容
6. 点击 **Add SSH key**

**重复以上步骤，登录个人GitHub账号添加个人账号的公钥。**

---

### 步骤3：配置SSH config文件

创建或编辑SSH配置文件，让系统知道不同的Host使用哪个密钥。

**文件位置：** `C:\Users\你的用户名\.ssh\config`

**创建/编辑config文件：**

```powershell
# 使用记事本创建/编辑
notepad ~/.ssh/config
```

**写入以下内容：**

```
# ========================================
# 公司GitHub账号 (默认账号A)
# ========================================
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_company
    IdentitiesOnly yes

# ========================================
# 个人GitHub账号 (账号B)
# ========================================
Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
    IdentitiesOnly yes
```

**配置说明：**

| 配置项 | 说明 |
|-------|------|
| `Host` | 自定义的别名，用于在git命令中引用 |
| `HostName` | 实际的主机名，GitHub固定为github.com |
| `User` | 用户名，GitHub固定为git |
| `IdentityFile` | 指定使用的私钥文件路径 |
| `IdentitiesOnly yes` | 只使用指定的密钥，避免尝试其他密钥 |

**关键点：**
- `github.com` 作为公司账号的Host，这样默认的git操作都会使用公司账号
- `github-personal` 作为个人账号的Host别名，需要使用个人账号时指定这个别名

---

### 步骤4：测试SSH连接

验证两个账号的SSH配置是否正确：

```bash
# 测试公司账号连接
ssh -T git@github.com

# 测试个人账号连接
ssh -T git@github-personal
```

**成功输出示例：**

```
Hi company-user! You've successfully authenticated, but GitHub does not provide shell access.
```

```
Hi personal-user! You've successfully authenticated, but GitHub does not provide shell access.
```

如果看到对应的用户名，说明配置成功。

---

## 使用指南

### 克隆新项目

#### 使用公司账号克隆（默认）

由于配置了`github.com`使用公司账号密钥，正常的克隆命令会自动使用公司账号：

```bash
# 标准SSH克隆方式，自动使用公司账号
git clone git@github.com:company-org/project.git
```

#### 使用个人账号克隆

需要将`github.com`替换为配置的别名`github-personal`：

```bash
# 使用个人账号克隆
git clone git@github-personal:personal-user/my-project.git
```

**注意：** 从GitHub页面复制的SSH地址是`git@github.com:xxx/xxx.git`，需要手动将`github.com`改为`github-personal`。

---

### 配置仓库用户信息

克隆项目后，进入项目目录设置本地用户信息：

**公司项目：**

```bash
cd company-project
git config user.name "Company Name"
git config user.email "work@company.com"
```

**个人项目：**

```bash
cd personal-project
git config user.name "Personal Name"
git config user.email "personal@gmail.com"
```

**验证配置：**

```bash
git config user.name
git config user.email
```

---

### 修改已有项目的远程地址

如果项目已经克隆，需要修改远程仓库地址以使用正确的账号。

**查看当前远程地址：**

```bash
git remote -v
```

**输出示例：**

```
origin  git@github.com:personal-user/my-project.git (fetch)
origin  git@github.com:personal-user/my-project.git (push)
```

**修改为个人账号：**

```bash
git remote set-url origin git@github-personal:personal-user/my-project.git
```

**修改为公司账号（如果需要）：**

```bash
git remote set-url origin git@github.com:company-org/project.git
```

---

## 常见场景

### 场景1：已用个人账号克隆项目，如何用公司账号克隆另一个项目

**前提条件：** 已完成上述SSH配置步骤。

**情况描述：**
- 之前已用个人账号B克隆了项目 `my-personal-repo`
- 现在需要用公司账号A克隆公司项目 `company-repo`

**操作步骤：**

1. **确认个人项目的远程地址使用正确的Host别名**

```bash
cd my-personal-repo
git remote -v
```

如果显示的是 `git@github.com:...`，需要修改为个人账号的别名：

```bash
git remote set-url origin git@github-personal:personal-user/my-personal-repo.git
```

2. **克隆公司项目（使用默认配置）**

```bash
# 直接使用标准SSH地址，会自动使用公司账号
git clone git@github.com:company-org/company-repo.git
```

3. **配置公司项目的用户信息**

```bash
cd company-repo
git config user.name "Company Name"
git config user.email "work@company.com"
```

4. **验证配置**

```bash
# 在公司项目目录
git remote -v
# 输出: origin  git@github.com:company-org/company-repo.git

# 在个人项目目录
cd ../my-personal-repo
git remote -v
# 输出: origin  git@github-personal:personal-user/my-personal-repo.git
```

---

### 场景2：已有项目需要切换账号

**情况描述：** 之前用HTTPS克隆的项目，现在要切换到SSH方式使用特定账号。

**操作步骤：**

1. **查看当前远程地址**

```bash
git remote -v
# 输出: origin  https://github.com/username/repo.git
```

2. **修改为SSH地址**

```bash
# 切换到公司账号
git remote set-url origin git@github.com:company-org/repo.git

# 或切换到个人账号
git remote set-url origin git@github-personal:personal-user/repo.git
```

3. **更新用户信息**

```bash
git config user.name "对应账号的用户名"
git config user.email "对应账号的邮箱"
```

---

### 场景3：全局默认使用公司账号

设置全局默认的用户信息为公司账号，个人项目单独配置。

**设置全局配置（公司账号）：**

```bash
git config --global user.name "Company Name"
git config --global user.email "work@company.com"
```

**个人项目单独配置：**

```bash
cd personal-project
git config user.name "Personal Name"
git config user.email "personal@gmail.com"
```

**配置优先级：** 仓库本地配置 > 全局配置

---

## 常见问题

### Q1：出现"Permission denied (publickey)"错误

**可能原因：**
1. SSH密钥未添加到GitHub
2. config文件配置错误
3. 密钥文件路径错误

**解决方法：**

```bash
# 1. 检查SSH agent是否运行
eval $(ssh-agent -s)

# 2. 添加密钥到agent
ssh-add ~/.ssh/id_ed25519_company
ssh-add ~/.ssh/id_ed25519_personal

# 3. 验证密钥已添加
ssh-add -l

# 4. 再次测试连接
ssh -T git@github.com
ssh -T git@github-personal
```

### Q2：push时提示使用了错误的账号

**解决方法：**

1. 检查远程地址是否正确：

```bash
git remote -v
```

2. 修改为正确的Host：

```bash
# 如果应该使用个人账号
git remote set-url origin git@github-personal:username/repo.git
```

### Q3：如何查看当前仓库使用的用户信息

```bash
# 查看本地配置
git config user.name
git config user.email

# 查看全局配置
git config --global user.name
git config --global user.email

# 查看所有配置及来源
git config --list --show-origin
```

### Q4：Windows上config文件路径问题

在Windows上，`~`表示用户主目录，即`C:\Users\你的用户名\`。

SSH配置文件完整路径：`C:\Users\你的用户名\.ssh\config`

确保`.ssh`文件夹存在，如果不存在可手动创建：

```powershell
mkdir ~/.ssh
```

### Q5：如何临时使用不同账号push

如果只是临时需要使用不同账号，可以直接指定完整URL：

```bash
# 临时使用个人账号push
git push git@github-personal:personal-user/repo.git main
```

---

## 附录：命令速查表

### SSH密钥相关

| 操作 | 命令 |
|------|------|
| 生成密钥 | `ssh-keygen -t ed25519 -C "email" -f ~/.ssh/keyname` |
| 查看公钥 | `cat ~/.ssh/keyname.pub` |
| 复制公钥到剪贴板 | `Get-Content ~/.ssh/keyname.pub \| Set-Clipboard` |
| 测试SSH连接 | `ssh -T git@host` |
| 启动SSH agent | `eval $(ssh-agent -s)` |
| 添加密钥到agent | `ssh-add ~/.ssh/keyname` |
| 查看agent中的密钥 | `ssh-add -l` |

### Git远程仓库相关

| 操作 | 命令 |
|------|------|
| 查看远程地址 | `git remote -v` |
| 修改远程地址 | `git remote set-url origin <url>` |
| 添加远程仓库 | `git remote add origin <url>` |
| 删除远程仓库 | `git remote remove origin` |

### Git用户配置相关

| 操作 | 命令 |
|------|------|
| 设置本地用户名 | `git config user.name "name"` |
| 设置本地邮箱 | `git config user.email "email"` |
| 设置全局用户名 | `git config --global user.name "name"` |
| 设置全局邮箱 | `git config --global user.email "email"` |
| 查看所有配置 | `git config --list --show-origin` |

### 克隆命令模板

```bash
# 公司账号（默认）
git clone git@github.com:company-org/repo.git

# 个人账号
git clone git@github-personal:personal-user/repo.git
```

---

## 总结

配置多GitHub账号的核心思路：

1. **一账号一密钥**：每个账号生成独立的SSH密钥对
2. **SSH config区分**：通过Host别名区分不同账号
3. **默认账号设置**：将最常用的账号（如公司账号）配置为默认的`github.com`
4. **项目级配置**：每个仓库配置正确的远程地址和用户信息

配置完成后的日常使用：
- 公司项目：正常使用标准命令，自动使用公司账号
- 个人项目：克隆/推送时使用`github-personal`替代`github.com`

