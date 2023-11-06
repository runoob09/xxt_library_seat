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

- <手机号>：你的手机号。
- <密码>：你的密码。
- <自习室ID>：要预约的自习室ID。
- <座位号>：座位号。
- <小时数>：当当前时间的小时数等于该参数值时，程序将执行抢座操作。
- <时间段>：是一个二元组列表，不填写该参数则会使用默认的时间列表`[("08:00", "12:00"), ("12:00", "16:00"), ("16:00", "20:00"), ("20:00", "22:00")]`。
- <操作类型类型>
    - `submit`:表示预约第二天的座位
    - `sign`:表示进行签到操作

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

## 免责声明

本项目仅供学习和研究使用，严禁用于商业目的。使用本项目产生的任何后果和责任将完全由使用者自行承担。

请注意，使用本项目进行自动预约等操作可能违反相关网站的使用条款和规定。在进行任何操作之前，请确保你已经获得合法的授权或得到了相关机构的许可，以避免违法行为。

作者对使用本项目导致的任何问题、损失或法律责任概不负责。请在使用前谨慎评估风险，并遵守当地法律法规。

## 联系方式

QQ:2499469495\
微信:15591708527