## 项目背景
[toc]
通过学习『杜赛』大佬的搭建 Django 博客&论坛的教程，通过实际上线站点，熟悉 Django 项目的`传统部署流程`，后续继续实践基于 Docker 容器的部署方法。
当前站点的业务视图，是基于函数的视图，前端采用 BootStrap4 构建，前后端耦合。基于类的视图，以及前后端分离仍在继续学习中。

后续会持续优化站点，记录部署步骤。

## 部署环境

- 服务器：Aliyun
- 操作系统：Ubuntu 16.04 TLS 64位
- 反向代理：Nginx 1.10.3
- WSGI服务器：Gunicorn 20.1.0
- 后端环境：Django（Python 3.5 + virtualenv 20.13.1）
- 数据库：Sqlit3（后续更换`Mysql`）

## 部署步骤

1. 配置服务器

   在阿里云服务器的入站安全组中，添加`80`、`443`、`22` 端口

   配置 ssh 访问方式为密钥组访问，提升访问安全性

2. 更新服务器软件

   连接上服务器后，在终端运行命令

   ```bash
   $ sudo apt-get update
   $ sudo apt-get upgrade
   ```

3. 安装 Git

   ```bash
   $ sudo apt-get install git
   ```

   完成安装后，需要配置自己项目仓库的访问，添加 `ssh` 访问密钥，用于通过 `ssh` 方式拉取项目代码

   ```bash
   $ ssh-keygen -t ed25519 -C "your_email@example.com"
   $ or
   $ ssh-keygen -t rsa
   ```
   **原因是：用 `https` 拉取项目代码，国内服务器拉取仓库代码存在不稳定因素，容易出现**
   
   > fatal: unable to access 'https://github.com/CoreJK/django_blog.git/': Empty reply from server

   配置自己邮箱、和用户名，便于后续开发维护。

   ```bash
   $ git config --global user.name "your self"
   $ git config --global user.email yourEmail@example.com
   ```
4. 安装 Nginx

   > 在 linux 上部署需要配置，windows 本地调试可以不用安装 Nginx 
     
   ```bash
   $ sudo apt-get install nginx
   ```

5. 拉取代码

   进入 `/home`，新建一个用于存放项目代码的目录，并拉取代码

   ```bash
   $ cd /home; mkdir -p /sites
   $ cd /sites
   $ git git@git@github.com:CoreJK/django_blog.git
   ```

   ~~我的项目代码里，需要新键一个`meida`目录，进入 `/home/sites/django_blog/my_blog`~~

   还需要在 `/home/sites/django_blog/myblog/` 目录下新键一个`.env`文件

   > 在开发时我们往 `settings.py` 中写入如 SECRET_KEY 、邮箱密码等各种敏感信息，部署时千万不要直接上传到互联网（GitHub 库是公开的！），而是把这些信息写到服务器本地，然后在 `settings.py` 中读取。
   >
   > **该文件是`settings.py`配置信息的环境变量，我选用了`django-environ==0.8.1`模块，因此需要配置此文件**
   > 
   > 下面文件中的中文注释，一定要删除！否则执行后续的 `python manage.py` 命令会报错！

   ```
   # 关闭debug模式
   DEBUG=False
   SECRET_KEY='替换成你自己的密钥'
   
   # smtp 邮箱配置
   EMAIL_HOST='smtp.xxx.com'
   EMAIL_HOST_USER='xxx@xx.com'
   EMAIL_HOST_PASSWORD='xxxxxxxxxxxx'
   EMAIL_PORT=xx
   DEFAULT_FROM_EMAIL='xxx Blog <xxx@xxx.com>'
   
   # 替换为允许访问的主机 IP,或者保持不变
   ALLOWED_HOSTS='*'
   ```

   **这个文件一定要添加到 `.gitignore` 文件中，这里存放着许多配置信息！不能被 git 版本控制记录**

6. 代码部署

   进入 `/home/sites/django_blog/`

   - 激活 `python` 虚拟环境，并安装项目所需模块

     ```bash
     $ sudo pip3 install virtualenv
     $ virtualenv --python=python3.5 venv
     $ source venv/bin/activate
     $ (env) ../dajngo_blog$ pip3 install -r requirements.txt
     ```

   - 进行静态文件收集、数据库迁移

     ```bash
     $ cd /home/sites/django_blog/my_blog/
     $ python3 manage.py collectstatic
     $ python3 manage.py migrate
     ```

7. 配置 Nginx

   - 在 `/etc/nginx/sites-available/` 中新建名为 `my_blog` 配置文件，写入如下配置，并保存

     ```bash
     server {
         charset utf-8;
         listen 80;
         server_name 服务器IP或域名;
         
         location /static {
             alias /home/sites/django_blog/my_blog/collected_static;
         }
     
         location /media {
             alias /home/sites/django_blog/my_blog/media;
         }
     
         location / {
             proxy_set_header Host $host;
             proxy_pass http://unix:/tmp/服务器IP或域名.socket;
         }
     }
     
   - 激活`my_blog`配置，删除默认配置文件 `default`，启动 `nginx` 服务

     ```bash
     $ sudo ln -s /etc/nginx/sites-available/my_blog /etc/nginx/sites-enabled
     $ rm /etc/nginx/sites-enabled/default
     $ service nginx start
     ```

8. 配置进程托管

   - 在 `/etc/systemd/system/`目录下，新建 `my_blog.service`文件，并写入保存

     ```bash
     [Unit]
     Description=My Blog Service
     
     [Service]
     Type=simple
     # manage.py 所在目录
     WorkingDirectory=/home/sites/django_blog/my_blog/
     # wsgi 服务器安装目录，服务启动命令，需要配置好 Nginx 才能正常访问
     ExecStart=/home/sites/django_blog/venv/bin/gunicorn --bind unix:/tmp/服务器IP或域名.socket my_blog.wsgi:application
     KillMode=process
     # 进程意外退出后 10s 重启
     Restart=on-failure
     RestartSec=10s
     
     [Install]
     WantedBy=multi-user.target
     ```
     
   - 启用`my_blog.service`进程托管配置，并启动服务
   
     ```bash
     $ systemctl enable my_blog
     $ systemctl start my_blog    # 启动my_blog进程
     ```
   
9. 博客的运行和维护

   - systemctl 管理博客进程

     ```bash
     $ systemctl status my_blog    # 查看进程状态
     $ systemctl stop my_blog    # 终止my_blog进程
     $ systemctl start my_blog    # 启动my_blog进程
     $ systemctl restart my_blog    # 重新启动my_blog进程
     ```

   - 通过 GitHub 更新服务器代码，并且重新收集静态文件

     ```bash
     $ git pull origin master
     $ python3 manage.py collectstatic
     ```
## ToDo ✔
- [ ] 数据库替换为 Mysql
- [ ] 优化文章展示页面
- [ ] 业务视图替换为类视图(可能另开仓库，用于学习对照)

## 参考教程
1. [@Dusai Django博客部署教程](https://github.com/stacklens/django_blog_tutorial)
1. [@Frost's 《Web 服务的进程托管》](https://frostming.com/2020/05-24/process-management/)
