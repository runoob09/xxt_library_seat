from chaoxing import Chaoxing
from new_chaoxing import NewChaoxing
from old_chaoxing import OldChaoxing
from utils import param_utils
import aiohttp
import asyncio

async def main():
    chaoxing: Chaoxing = None
    p = param_utils.get_param()
    if p.get_system_type() == "new":
        chaoxing = NewChaoxing(p)
    else:
        chaoxing = OldChaoxing(p)
    # 进行登录逻辑
    chaoxing.login()
    chaoxing.get_fid_enc()
    # 创建异步session
    async with aiohttp.ClientSession(cookies=chaoxing.get_cookies()) as async_session:
        chaoxing.async_session = async_session
        # 解析命令
        command = {
            "submit": chaoxing.submit,
            "list_room": chaoxing.list_room
        }
        await command[p.get_type()]()


if __name__ == '__main__':
    asyncio.run(main())