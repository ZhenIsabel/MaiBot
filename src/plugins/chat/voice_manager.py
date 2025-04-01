import os
import time
import requests

from src.common.logger import get_module_logger
from src.plugins.chat.message import MessageSending
from src.plugins.chat.message_base import Seg

logger = get_module_logger("chat_voice") 

class VoiceManager:
    _instance = None
    VOICE_DIR = "data"  # 语音存储根目录
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._ensure_voice_dir()
            self._initialized = True
            # self._llm = LLM_request(model=global_config.llm_tts_model, request_type="tts")
    
    def _ensure_voice_dir(self):
        """确保语音存储目录存在"""
        os.makedirs(self.VOICE_DIR, exist_ok=True)


    # 使用自己的request方法，不用全局的
    def generate_voice(self, text: str, voice_type: str = "normal",voice_model:str="alex") ->str:
        """生成语音文件
        
        Args:
            text: 要转换的文本
            voice_type: 语音类型('normal', 'happy', 'sad' 等)
            
        Returns:
            Optional[str]: 生成的语音文件路径，失败则返回None
        """
        voice="FunAudioLLM/CosyVoice2-0.5B:"+voice_model
        url = "https://api.siliconflow.cn/v1/audio/speech"
        payload = {
            "model": "FunAudioLLM/CosyVoice2-0.5B",
            "input": "你能用嫌弃的情绪说这句话吗？<|endofprompt|>"+text,
            "voice": voice,
            "response_format": "mp3",
            "sample_rate": 44100,
            "stream": True,
            "speed": 1,
            "gain": 0
        }
        headers = {
            "Authorization": "Bearer sk-dbujpghcchabpkohjrxzekohyfxtdxfdeepfldbtlzzaogvj", # 替换为你的API密钥
            "Content-Type": "application/json"
        }


        try:
            # 生成语音文件
            logger.info(f"生成语音文件: {text}")
            response = requests.request("POST", url, json=payload, headers=headers)
            logger.info(f"API响应状态码: {response.status_code}")
            voice_data = response.content
            if not voice_data:
                logger.error(f"生成语音文件失败，未得到返回数据")
                return None
                
            # 保存语音文件
            timestamp = int(time.time())
            filename = f"{timestamp}.mp3"  # 修改为mp3格式
            voice_dir = os.path.join(self.VOICE_DIR, "voice")
            os.makedirs(voice_dir, exist_ok=True)
            file_path = os.path.join(voice_dir, filename)
            try:
                with open(file_path, "wb") as f:
                    f.write(voice_data)
                    
                logger.success(f"保存语音文件: {file_path}")
                # 将文件路径转换为绝对路径并使用 file:/// 协议
                abs_path = os.path.abspath(file_path)
                normalized_path = os.path.normpath(abs_path).replace(os.path.sep, '/')
                file_uri = f"file:///{normalized_path}"
                # 清理上一次拉的屎
                self.delete_shit(file_path)
                return file_uri
                
            except Exception as e:
                logger.error(f"保存语音文件失败: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"生成语音失败: {str(e)}")
            return None

    def generate_voice_message(self, file_path: str,think_id,chat_stream,bot_user_info,userinfo,thinking_start_time):
        """发送语音文件

        Args:
            file_path: 语音文件路径
        """
        # 发送语音文件
        # 这里可以添加发送语音文件的逻辑，例如使用第三方API或WebSocket等
        
        # 构造语音消息
        # 生成语音文件的CQ码
        voice_cq_code = f"[CQ:record,file={file_path}]"
        voice_seg=Seg(type="record",data=voice_cq_code)
        voice_message = MessageSending(
                message_id=think_id,
                chat_stream=chat_stream,
                bot_user_info=bot_user_info,
                sender_info=userinfo,
                message_segment=voice_seg,
                is_head=False,
                is_emoji=False,
                thinking_start_time=thinking_start_time
            )
        logger.success(f"生成语音消息: {file_path}")
        return voice_message

    def delete_shit(self, excluded_file_path: str):
        """删除指定目录下除了特定文件外的所有文件
        
        Args:
            directory: 目标目录的路径
            excluded_files: 要保留的文件名列表
        """
        try:
            # 统一路径分隔符并获取目标文件所在目录和文件名
            normalized_path = os.path.normpath(excluded_file_path)
            directory = os.path.dirname(normalized_path)
            excluded_filename = os.path.basename(normalized_path)
            
            # 确保目录存在
            if not os.path.exists(directory):
                logger.warning(f"目录不存在: {directory}")
                return
                
            # 获取目录中的所有文件
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                # 只处理文件，不处理目录
                if os.path.isfile(file_path) and filename != excluded_filename:
                    try:
                        # 从文件名中提取时间戳（假设文件名格式为 "timestamp.mp3"）
                        timestamp = int(filename.split('.')[0])
                        # 如果文件创建时间超过20分钟（1200秒）
                        current_time = int(time.time())
                        if current_time - timestamp > 1200:
                            os.remove(file_path)
                            logger.success(f"删除过期文件: {file_path}")
                    except Exception as e:
                        logger.error(f"删除文件失败 {file_path}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"清理目录失败: {str(e)}")

# 创建全局单例
voice_manager = VoiceManager()