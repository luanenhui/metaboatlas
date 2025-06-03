### 项目目录及用法
[toc]

### 针对开发人员
#### step 0：项目依赖于python， R 和postgresql数据库
1. 安装python
2. 安装postgresql数据库 
   [**windows下安装教程**](https://www.runoob.com/postgresql/windows-install-postgresql.html)
3. 在postgresql数据库中新建名为 metabo 的database
4. windows环境下，配置odbc连接, R分析脚本访问数据库会用到  
   [**教程**](https://www.jianshu.com/p/0300a8286ecf)
5. 安装 R-3.6
   [地址](https://mirrors.tuna.tsinghua.edu.cn/CRAN/)
6. 为R安装argparse和RODBC包
   ```bash
     # 进入命令行
     Rscript -e 'install.packages(c("argparse","RODBC))'
   ```
7. 安装Redis数据库
    [**教程**](https://www.runoob.com/redis/redis-install.html)

#### step 1  运行环境
根目录下有两个文件跟虚拟运行环境有关
    * Pipfile
    * Pipfile.lock
虚拟运行环境使用pipenv管理，启动命令行工具，命令如下
```bash
  pip install pipenv    # 使用pip安装pipenv虚拟环境管理工具
  pipenv install --dev   # pipenv根据Pipfile.lock自动安装依赖Package, --dev表示安装开发环境需要的package
  pipenv shell          # 进入虚拟环境
```

#### step 2 环境配置
.env和.flaskenv文件里配置了系统环境变量，网站程序启动时，python会自动读取
** *.env文件* **
** 配置非常敏感的身份信息**
DATABASE_URI=postgresql://username:password@host:port/database
* username: postgresql数据库用户名
* password: 用户密码
* host: postgresql主机地址
* port: postgresql端口
* database: 数据库名称

** *.flaskenv 文件* **
** 配置app运行信息 **
FLASK_APP=metaboatlas  # app目录，本例中为metaboatlas Package
FLASK_ENV=development  # production 生产环境； development 开发环境
FLASK_RUN_HOST=127.0.0.1  # 网站IP
FLASK_RUN_PORT=8000    # 网站端口

#### step 3 初始化数据库
```bash
  flask  # 查看都有哪些命令
  flask initdb  #初始化数据库
```
在初始化数据库后，使用pgadmin4 可以看到postgresql里metabo数据库多了compound和spectra两个表格
![](./image/pgadmin.png)

#### step 4 导入数据
如上图所示，postgresql可直接从txt或者csv格式的文件直接导入数据
考虑到代谢物名称很多包含逗号(,)，建议用tab分隔的txt格式
** data文件夹下有实例数据可以导入 **
* compound_exam.txt   代谢物信息，导入到compound数据表
* spectra.txt  谱图信息，导入到spectra数据表

#### step 5 配置R脚本信息
** scripts文件夹里有执行谱图相似性计算的R脚本文件 **
* score.r  用户提交的谱图与数据库谱图进行比对
  > * 提交数据使用csv格式，示例文件 data/ms2.csv
  > * score.r需要连接到postgresql数据库，在脚本中找到如下命令并更改
```R
conn = odbcConnect("PostgreSQL35W", uid="用户名", pwd="密码")
```

#### step 6 启动网站
```bash
  flask run
```
启动网站后在浏览器中输入 http://127.0.0.1:8000 即可打开首页

### 针对测试人员
输入测试网址即可打开首页，开发者在个人电脑上已经部署了一个测试环境，地址为
http://192.168.50.151:8000    # 首页
http://192.168.50.151:8000/help #帮助页面

#### step 7 网站测试
首页有六个功能可供测试，**单击每个功能即可弹出该功能下的表单**
![](./image/index1.png)
![](./image/index2.png)
* 查询功能
  * 1 代谢物名称查询  点击 **example**按钮后，点击**Search**按钮
  * 2 根据通路查询代谢物  测试方法同上
  * 3 **根据二级谱图标签获取所有二级谱图，返回json格式，可供R和python直接调用**
* 谱图比对功能
  * 4 用户提交单张谱图，与数据库中的谱图做比对  参数参照图片，测试文件为 data文件夹下的 ms2.csv 文件
  * 5 用户提交包含多张谱图的文件，比较该文件谱图的相似性  参数参照图片，测试文件有两个，分别为
      * data文件夹下的 **test1.mgf** (没有任意两张谱图相似)
      * data文件夹下的 **test2.mgf** (有多张谱图相似)
  * 6 用户提交的包含多张谱图的mgf文件，比较该文件中每个谱图与数据库谱图的相似性，测试文件为data文件夹下的 **QC-2 HILIC POS-QC-2.mgf**
      * 出于节省计算资源的考虑，目前只允许单次提交一个文件，且只比对mgf中的前1000张谱图（针对外部用户）
      * 比对后台采用的是R脚本，可直接集成到本地R分析环境中（针对本地用户）