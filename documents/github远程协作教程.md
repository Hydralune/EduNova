##  GitHub 协作教程

为了方便大家协作开发，我整理了这份操作流程，请按步骤执行

------

### **前提**

- 已经在电脑上安装好 **Git**
- 已登录你的 **GitHub** 账号
   （登录方法这里不再赘述）

------

###  **1. 生成 SSH 密钥（用于安全访问仓库）**

在 **Git Bash** 或 **PowerShell** 中执行：

```bash
ssh-keygen -t rsa -b 4096 -C "你的邮箱@example.com"
```

- 连续按 **回车**，使用默认保存位置即可。
- 然后执行下面的命令，复制你的公钥：

```bash
cat ~/.ssh/id_rsa.pub
```

（Windows PowerShell 也可以用
 `Get-Content ~/.ssh/id_rsa.pub | clip`
 直接复制到剪贴板）

------

###  **2. 添加 SSH Key 到 GitHub**

1. 打开 GitHub 网站，右上角点击头像 → **Settings（设置）**
2. 左侧菜单找到 **SSH and GPG keys**
3. 点击右上角 **New SSH key**
   - **Title** 可以随便写，例如：`My Laptop SSH Key`
   - **Key** 栏粘贴刚刚复制的内容
4. 点击 **Add SSH key**

这样就配置好了 SSH 通道，后续 push 不需要输入账号密码。

------

###  **3. 告诉我你的 GitHub 用户名**

请把你的 GitHub 用户名发给我，我会把仓库的协作权限（写权限）邀请给你，接受后就可以提交代码了。

------

###  **4. 克隆仓库**

在你电脑上找个合适的文件夹，执行：

```bash
git clone git@github.com:Hydralune/EduNova.git
```

这一步会把仓库完整下载到本地。

------

###  **5. 每次开始工作前：先同步最新代码**

```bash
git pull origin main
```

------

###  **6. 提交你的修改**

开发完后，先把改动保存并提交：

```bash
git add .
git commit -m "这里写明你做了哪些修改"
```

------

###  **7. 推送到远程仓库**

```bash
git push origin main
```

------

###  **8. 如果推送失败（远程有更新）**

先拉取最新代码并自动合并：

```bash
git pull origin main
```

如遇冲突，解决冲突后再：

```bash
git add .
git commit -m "解决冲突"
git push origin main
```