import re
import time
from random import random

from ..memory_system.Hippocampus import HippocampusManager
from ..moods.moods import MoodManager  # 导入情绪管理器
from ..config.config import global_config
from .emoji_manager import emoji_manager  # 导入表情包管理器
from .llm_generator import ResponseGenerator
from .message import MessageSending, MessageRecv, MessageThinking, MessageSet

from .chat_stream import chat_manager

from .message_sender import message_manager  # 导入新的消息管理器
from .relationship_manager import relationship_manager
from .storage import MessageStorage
from .utils import is_mentioned_bot_in_message, get_recent_group_detailed_plain_text
from .utils_image import image_path_to_base64
from ..willing.willing_manager import willing_manager  # 导入意愿管理器
from ..message import UserInfo, Seg

from src.think_flow_demo.heartflow import heartflow
from src.common.logger import get_module_logger, CHAT_STYLE_CONFIG, LogConfig

from src.plugins.chat.voice_manager import VoiceManager  # 导入语音管理器

# 定义日志配置
chat_config = LogConfig(
    # 使用消息发送专用样式
    console_format=CHAT_STYLE_CONFIG["console_format"],
    file_format=CHAT_STYLE_CONFIG["file_format"],
)

# 配置主程序日志格式
logger = get_module_logger("chat_bot", config=chat_config)


class ChatBot:
    def __init__(self):
        self.storage = MessageStorage()
        self.gpt = ResponseGenerator()
        self.bot = None  # bot 实例引用
        self._started = False
        self.mood_manager = MoodManager.get_instance()  # 获取情绪管理器单例
        self.mood_manager.start_mood_update()  # 启动情绪更新

    async def _ensure_started(self):
        """确保所有任务已启动"""
        if not self._started:
            self._started = True

    async def message_process(self, message_data: str) -> None:
        """处理转化后的统一格式消息
        1. 过滤消息
        2. 记忆激活
        3. 意愿激活
        4. 生成回复并发送
        5. 更新关系
        6. 更新情绪
        """

        message = MessageRecv(message_data)
        groupinfo = message.message_info.group_info
        userinfo = message.message_info.user_info
        messageinfo = message.message_info

        # 消息过滤，涉及到config有待更新

        # 创建聊天流
        chat = await chat_manager.get_or_create_stream(
            platform=messageinfo.platform,
            user_info=userinfo,
            group_info=groupinfo,
        )
        message.update_chat_stream(chat)

        # 创建 心流与chat的观察
        heartflow.create_subheartflow(chat.stream_id)

        timer1 = time.time()
        await message.process()
        timer2 = time.time()
        logger.debug(f"2消息处理时间: {timer2 - timer1}秒")

        # 过滤词/正则表达式过滤
        if self._check_ban_words(message.processed_plain_text, chat, userinfo) or self._check_ban_regex(
            message.raw_message, chat, userinfo
        ):
            return

        await self.storage.store_message(message, chat)

        timer1 = time.time()
        interested_rate = 0
        interested_rate = await HippocampusManager.get_instance().get_activate_from_text(
            message.processed_plain_text, fast_retrieval=True
        )
        timer2 = time.time()
        logger.debug(f"3记忆激活时间: {timer2 - timer1}秒")

        is_mentioned = is_mentioned_bot_in_message(message)

        if global_config.enable_think_flow:
            current_willing_old = willing_manager.get_willing(chat_stream=chat)
            current_willing_new = (heartflow.get_subheartflow(chat.stream_id).current_state.willing - 5) / 4
            print(f"旧回复意愿：{current_willing_old}，新回复意愿：{current_willing_new}")
            current_willing = (current_willing_old + current_willing_new) / 2
        else:
            current_willing = willing_manager.get_willing(chat_stream=chat)

        willing_manager.set_willing(chat.stream_id, current_willing)

        timer1 = time.time()
        reply_probability = await willing_manager.change_reply_willing_received(
            chat_stream=chat,
            is_mentioned_bot=is_mentioned,
            config=global_config,
            is_emoji=message.is_emoji,
            interested_rate=interested_rate,
            sender_id=str(message.message_info.user_info.user_id),
        )
        timer2 = time.time()
        logger.debug(f"4计算意愿激活时间: {timer2 - timer1}秒")

        # 神秘的消息流数据结构处理
        if chat.group_info:
            if chat.group_info.group_name:
                mes_name_dict = chat.group_info.group_name
                mes_name = mes_name_dict.get("group_name", "无名群聊")
            else:
                mes_name = "群聊"
        else:
            mes_name = "私聊"

        # 打印收到的信息的信息
        current_time = time.strftime("%H:%M:%S", time.localtime(messageinfo.time))
        logger.info(
            f"[{current_time}][{mes_name}]"
            f"{chat.user_info.user_nickname}:"
            f"{message.processed_plain_text}[回复意愿:{current_willing:.2f}][概率:{reply_probability * 100:.1f}%]"
        )

        if message.message_info.additional_config:
            if "maimcore_reply_probability_gain" in message.message_info.additional_config.keys():
                reply_probability += message.message_info.additional_config["maimcore_reply_probability_gain"]

        # 开始组织语言
        if random() < reply_probability:
            timer1 = time.time()
            response_set, thinking_id = await self._generate_response_from_message(message, chat, userinfo, messageinfo)
            timer2 = time.time()
            logger.info(f"5生成回复时间: {timer2 - timer1}秒")

            if not response_set:
                logger.info("为什么生成回复失败？")
                return

            # 发送消息
            timer1 = time.time()
            await self._send_response_messages(message, chat, response_set, thinking_id)
            timer2 = time.time()
            logger.info(f"7发送消息时间: {timer2 - timer1}秒")

            # 处理表情包
            timer1 = time.time()
            await self._handle_emoji(message, chat, response_set)
            timer2 = time.time()
            logger.debug(f"8处理表情包时间: {timer2 - timer1}秒")

            timer1 = time.time()
            await self._update_using_response(message, chat, response_set)
            timer2 = time.time()
            logger.info(f"6更新htfl时间: {timer2 - timer1}秒")

            # 更新情绪和关系
            # await self._update_emotion_and_relationship(message, chat, response_set)

    async def _generate_response_from_message(self, message, chat, userinfo, messageinfo):
        """生成回复内容

        Args:
            message: 接收到的消息
            chat: 聊天流对象
            userinfo: 用户信息对象
            messageinfo: 消息信息对象

        Returns:
            tuple: (response, raw_content) 回复内容和原始内容
        """
        bot_user_info = UserInfo(
            user_id=global_config.BOT_QQ,
            user_nickname=global_config.BOT_NICKNAME,
            platform=messageinfo.platform,
        )

        thinking_time_point = round(time.time(), 2)
        thinking_id = "mt" + str(thinking_time_point)
        thinking_message = MessageThinking(
            message_id=thinking_id,
            chat_stream=chat,
            bot_user_info=bot_user_info,
            reply=message,
            thinking_start_time=thinking_time_point,
        )

        message_manager.add_message(thinking_message)
        willing_manager.change_reply_willing_sent(chat)

        response_set = await self.gpt.generate_response(message)

        return response_set, thinking_id

    async def _update_using_response(self, message, response_set):
        # 更新心流状态
        stream_id = message.chat_stream.stream_id
        chat_talking_prompt = ""
        if stream_id:
            chat_talking_prompt = get_recent_group_detailed_plain_text(
                stream_id, limit=global_config.MAX_CONTEXT_SIZE, combine=True
            )

        heartflow.get_subheartflow(stream_id).do_after_reply(response_set, chat_talking_prompt)

    async def _send_response_messages(self, message, chat, response_set, thinking_id):
        container = message_manager.get_container(chat.stream_id)
        thinking_message = None

        # logger.info(f"开始发送消息准备")
        for msg in container.messages:
            if isinstance(msg, MessageThinking) and msg.message_info.message_id == thinking_id:
                thinking_message = msg
                container.messages.remove(msg)
                break

        if not thinking_message:
            logger.warning("未找到对应的思考消息，可能已超时被移除")
            return

        # logger.info(f"开始发送消息")
        thinking_start_time = thinking_message.thinking_start_time
        message_set = MessageSet(chat, thinking_id)

        mark_head = False
        # 添加随机语音发送逻辑
        should_send_voice = random() < 0.01  # 40%概率发送语音
        if should_send_voice:
            voice=VoiceManager()
            message_full="，".join(response)
            voice_path=voice.generate_voice(message_full)
            voice_message=voice.generate_voice_message(voice_path,think_id,chat,bot_user_info,userinfo,thinking_start_time)
            message_set.add_message(voice_message)
            logger.debug(f"添加语音消息到message_set: {message_full}")
        else:
            for msg in response_set:
                message_segment = Seg(type="text", data=msg)
                bot_message = MessageSending(
                    message_id=thinking_id,
                    chat_stream=chat,
                    bot_user_info=UserInfo(
                        user_id=global_config.BOT_QQ,
                        user_nickname=global_config.BOT_NICKNAME,
                        platform=message.message_info.platform,
                    ),
                    sender_info=message.message_info.user_info,
                    message_segment=message_segment,
                    reply=message,
                    is_head=not mark_head,
                    is_emoji=False,
                    thinking_start_time=thinking_start_time,
                )
                if not mark_head:
                    mark_head = True
                message_set.add_message(bot_message)
            # logger.info(f"开始添加发送消息")
            message_manager.add_message(message_set)

    async def _handle_emoji(self, message, chat, response):
        """处理表情包

        Args:
            message: 接收到的消息
            chat: 聊天流对象
            response: 生成的回复
        """
        if random() < global_config.emoji_chance:
            emoji_raw = await emoji_manager.get_emoji_for_text(response)
            if emoji_raw:
                emoji_path, description = emoji_raw
                emoji_cq = image_path_to_base64(emoji_path)

                thinking_time_point = round(message.message_info.time, 2)

                message_segment = Seg(type="emoji", data=emoji_cq)
                bot_message = MessageSending(
                    message_id="mt" + str(thinking_time_point),
                    chat_stream=chat,
                    bot_user_info=UserInfo(
                        user_id=global_config.BOT_QQ,
                        user_nickname=global_config.BOT_NICKNAME,
                        platform=message.message_info.platform,
                    ),
                    sender_info=message.message_info.user_info,
                    message_segment=message_segment,
                    reply=message,
                    is_head=False,
                    is_emoji=True,
                )
                message_manager.add_message(bot_message)

    async def _update_emotion_and_relationship(self, message, chat, response, raw_content):
        """更新情绪和关系

        Args:
            message: 接收到的消息
            chat: 聊天流对象
            response: 生成的回复
            raw_content: 原始内容
        """
        stance, emotion = await self.gpt._get_emotion_tags(raw_content, message.processed_plain_text)
        logger.debug(f"为 '{response}' 立场为：{stance} 获取到的情感标签为：{emotion}")
        await relationship_manager.calculate_update_relationship_value(chat_stream=chat, label=emotion, stance=stance)
        self.mood_manager.update_mood_from_emotion(emotion, global_config.mood_intensity_factor)

    def _check_ban_words(self, text: str, chat, userinfo) -> bool:
        """检查消息中是否包含过滤词

        Args:
            text: 要检查的文本
            chat: 聊天流对象
            userinfo: 用户信息对象

        Returns:
            bool: 如果包含过滤词返回True，否则返回False
        """
        for word in global_config.ban_words:
            if word in text:
                logger.info(
                    f"[{chat.group_info.group_name if chat.group_info else '私聊'}]{userinfo.user_nickname}:{text}"
                )
                logger.info(f"[过滤词识别]消息中含有{word}，filtered")
                return True
        return False

    def _check_ban_regex(self, text: str, chat, userinfo) -> bool:
        """检查消息是否匹配过滤正则表达式

        Args:
            text: 要检查的文本
            chat: 聊天流对象
            userinfo: 用户信息对象

        Returns:
            bool: 如果匹配过滤正则返回True，否则返回False
        """
        for pattern in global_config.ban_msgs_regex:
            if re.search(pattern, text):
                logger.info(
                    f"[{chat.group_info.group_name if chat.group_info else '私聊'}]{userinfo.user_nickname}:{text}"
                )
                logger.info(f"[正则表达式过滤]消息匹配到{pattern}，filtered")
                return True
        return False


# 创建全局ChatBot实例
chat_bot = ChatBot()
