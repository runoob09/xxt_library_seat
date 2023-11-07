# 学习通图书馆座位预约服务

---

## 项目名称

学习通图书馆通用座位预约、签到程序

## 项目概述

这是一个用于学习通图书馆座位预约和签到的 Python 程序。它提供了自动预约和签到的功能，可以在每天指定的时间自动完成操作。

## 功能特点

- 自动预约：在每天指定的时间，程序可以自动进行座位预约，方便用户获取图书馆座位。
- 座位签到：用户可以使用程序进行座位签到，无需手动操作。
- 定时任务：程序可以根据设定的时间表执行自动预约和签到任务。
- 灵活配置：提供用户友好的配置选项，允许用户自定义预约和签到的参数。

## 安装和使用说明

### 环境要求

- Python 3.11 或更高版本

### 安装依赖项

1. 克隆项目到本地：

   ```shell
   git clone https://github.com/runoob09/xxt_library_seat
   ```
2. 进入项目目录
   ```shell
   cd xxt_library_seat
   ```
3. 安装依赖项
   ```shell
   pip install -r requirements.txt
   ```

### 运行程序

你可以按照下面的格式来运行程序

   ```shell
   python main.py user_name=<手机号> password=<密码> room_id=<自习室ID> seat_id=<座位号> hour=<小时数> type=<操作类型> time_list=<时间段>
   ```

#### submit命令

该命令实现对于第二天的占座

```shell
python main.py user_name=<手机号> password=<密码> room_id=<自习室ID> seat_id=<座位号> hour=<小时数> type=submit time_list=<时间段>
```

- user_name:必选参数，账号
- password:必选参数，密码
- room_id:必选参数，要占座的自习室id
- seat_id:必选参数，要占的座位id
- hour:必选参数，程序会延迟到填写的hour继续执行
- time_list:非必选参数，表示你要选择的座位时间。该参数的格式为`start_time1-end_time1,start_time2-end_time2...`

### sign命令

执行签到操作

```shell
python main.py user_name=<手机号> password=<密码> type=sign
```

- user_name:必选参数，账号
- password:必选参数，密码

### list_room命令

列出学校所有的自习室名称及自习室id

```shell
python main.py user_name=<手机号> password=<密码> type=list_room
```

- user_name:必选参数，账号
- password:必选参数，密码

## 贡献

如果你发现任何问题或有改进建议，请在项目的 [Issue 页面]() 提交问题或功能请求。

如果你希望为项目做出贡献，请按照以下步骤进行：

1. 克隆项目到本地：

   ```shell
   git clone https://github.com/runoob09/xxt_library_seat
    ```
2. 创建一个新的分支
    ```shell
   git checkout -b feature/your-feature
   ```
3. 进行修改和改进。

4. 提交代码并创建一个 Pull Request。

欢迎并感谢任何形式的贡献！

## 项目结构

- `js`:该文件夹下是一些参数的加密的相关js逻辑
- `python`:将js的逻辑转换为python的逻辑
- `main.py`:主程序文件，用于执行自习室座位预约和签到操作的脚本。
- `README.md`:项目的说明文档，提供了安装、配置、运行等方面的详细信息。
- `utils.py`:提供的一些工具方法
- `rebuild.py`:重构的main.py
- `requirements.txt`:存放项目所需的依赖项列表，可通过 `pip install -r requirements.txt` 安装所有依赖。

## 需求和反馈

如果你有任何需求、建议或问题，请随时提出。请在 [Issues](https://github.com/runoob09/xxt_library_seat/issues)
页面编写一个新的issue，我会尽快回复。

非常欢迎你的反馈和贡献！

## 免责声明

本项目仅供学习和研究使用，严禁用于商业目的。使用本项目产生的任何后果和责任将完全由使用者自行承担。

请注意，使用本项目进行自动预约等操作可能违反相关网站的使用条款和规定。在进行任何操作之前，请确保你已经获得合法的授权或得到了相关机构的许可，以避免违法行为。

作者对使用本项目导致的任何问题、损失或法律责任概不负责。请在使用前谨慎评估风险，并遵守当地法律法规。

## 联系方式声明

感谢您对本项目的兴趣和支持。我非常乐意与其他开发者就与代码相关的问题进行交流和讨论。

如果您在安装和配置本项目时遇到困难，我提供付费帮助来解决与代码安装和配置相关的问题。

请注意，我的联系方式仅用于与代码安装和配置相关的帮助请求。我无法回答与其他主题无关的咨询、请求或合作邀约。

如果您需要付费支持来解决安装和配置问题，请通过以下方式与我联系：

- 发送电子邮件：将您的问题和需求发送至我的邮箱`2499469495@qq.com`。
- 添加QQ：`2499469495`
- 添加微信：`15591708527`

请尊重我的时间和努力，避免发送与代码安装和配置无关的请求。非与代码安装和配置相关的联系请求将不会得到回复。

感谢您的理解与配合！