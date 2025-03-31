# 麦麦！MaiMBot-MaiCore (编辑中)

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/github/license/SengokuCola/MaiMBot)
![Status](https://img.shields.io/badge/状态-开发中-yellow)

</div>

## 📝 项目简介

**🍔MaiCore是一个基于大语言模型的可交互智能体**

- LLM 提供对话能力
- MongoDB 提供数据持久化支持
- 可扩展

**最新版本: v0.6.0-mmc** ([查看更新日志](changelog.md))
> [!WARNING]
> 该版本更新较大，建议单独开文件夹部署，然后转移/data文件，数据库可能需要删除messages下的内容（不需要删除记忆）

<div align="center">
<a href="https://www.bilibili.com/video/BV1amAneGE3P" target="_blank">
    <img src="docs/pic/video.png" width="300" alt="麦麦演示视频">
    <br>
    👆 点击观看麦麦演示视频 👆

</a>
</div>

> [!WARNING]
> - 项目处于活跃开发阶段，代码可能随时更改
> - 文档未完善，有问题可以提交 Issue 或者 Discussion
> - QQ机器人存在被限制风险，请自行了解，谨慎使用
> - 由于持续迭代，可能存在一些已知或未知的bug
> - 由于开发中，可能消耗较多token


## ✍️如何给本项目报告BUG/提交建议/做贡献

MaiCore是一个开源项目，我们非常欢迎你的参与。你的贡献，无论是提交bug报告、功能需求还是代码pr，都对项目非常宝贵。我们非常感谢你的支持！🎉 但无序的讨论会降低沟通效率，进而影响问题的解决速度，因此在提交任何贡献前，请务必先阅读本项目的[贡献指南](CONTRIBUTE.md)

### 💬交流群
- [五群](https://qm.qq.com/q/JxvHZnxyec) 1022489779（开发和建议相关讨论）不一定有空回复，会优先写文档和代码
- [一群](https://qm.qq.com/q/VQ3XZrWgMs) 766798517 【已满】（开发和建议相关讨论）不一定有空回复，会优先写文档和代码
- [二群](https://qm.qq.com/q/RzmCiRtHEW) 571780722（开发和建议相关讨论）不一定有空回复，会优先写文档和代码
- [三群](https://qm.qq.com/q/wlH5eT8OmQ) 1035228475【已满】（开发和建议相关讨论）不一定有空回复，会优先写文档和代码
- [四群](https://qm.qq.com/q/wlH5eT8OmQ) 729957033【已满】（开发和建议相关讨论）不一定有空回复，会优先写文档和代码


<div align="left">
<h2>📚 文档        ⬇️ 快速开始使用麦麦 ⬇️</h2>
</div>

### 部署方式(忙于开发，部分内容可能过时)

-  📦 **Windows 一键傻瓜式部署**：请运行项目根目录中的 `run.bat`，部署完成后请参照后续配置指南进行配置

-  📦 Linux 自动部署（Arch/CentOS9/Debian12/Ubuntu24.10） ：请下载并运行项目根目录中的`run.sh`并按照提示安装，部署完成后请参照后续配置指南进行配置

- [📦 Windows 手动部署指南 ](docs/manual_deploy_windows.md)

- [📦 Linux 手动部署指南 ](docs/manual_deploy_linux.md)

- [📦 macOS 手动部署指南 ](docs/manual_deploy_macos.md)

- [🖥️群晖 NAS 部署指南](docs/synology_deploy.md)

### 配置说明

- [🎀 新手配置指南](docs/installation_cute.md) - 通俗易懂的配置教程，适合初次使用的猫娘
- [⚙️ 标准配置指南](docs/installation_standard.md) - 简明专业的配置说明，适合有经验的用户

### 常见问题

- [❓ 快速 Q & A ](docs/fast_q_a.md) - 针对新手的疑难解答，适合完全没接触过编程的新手

<div align="left">
<h3>了解麦麦 </h3>
</div>


## 🎯 功能介绍

### 💬 聊天功能

- 支持关键词检索主动发言：对消息的话题topic进行识别，如果检测到麦麦存储过的话题就会主动进行发言
- 支持bot名字呼唤发言：检测到"麦麦"会主动发言，可配置
- 支持多模型，多厂商自定义配置
- 动态的prompt构建器，更拟人
- 支持图片，转发消息，回复消息的识别
- 错别字和多条回复功能：麦麦可以随机生成错别字，会多条发送回复以及对消息进行reply

### 😊 表情包功能

- 支持根据发言内容发送对应情绪的表情包
- 会自动偷群友的表情包

### 📅 日程功能

- 麦麦会自动生成一天的日程，实现更拟人的回复

### 🧠 记忆功能

- 对聊天记录进行概括存储，在需要时调用，待完善

### 📚 知识库功能

- 基于embedding模型的知识库，手动放入txt会自动识别，写完了，暂时禁用

### 👥 关系功能

- 针对每个用户创建"关系"，可以对不同用户进行个性化回复，目前只有极其简单的好感度（WIP）
- 针对每个群创建"群印象"，可以对不同群进行个性化回复（WIP）

## 开发计划TODO：LIST

规划主线
0.6.0：记忆系统更新
0.7.0: 麦麦RunTime

- 人格功能：WIP
- 群氛围功能：WIP
- 图片发送，转发功能：WIP
- 幽默和meme功能：WIP的WIP
- 让麦麦玩mc：WIP的WIP的WIP
- 兼容gif的解析和保存
- 小程序转发链接解析
- 对思考链长度限制
- 修复已知bug
- ~~完善文档~~
- 修复转发
- ~~config自动生成和检测~~
- ~~log别用print~~
- ~~给发送消息写专门的类~~
- 改进表情包发送逻辑
- 自动生成的回复逻辑，例如自生成的回复方向，回复风格
- 采用截断生成加快麦麦的反应速度
- 改进发送消息的触发

## 设计理念

> **千石可乐说：**
> - 这个项目最初只是为了给牛牛bot添加一点额外的功能，但是功能越写越多，最后决定重写。其目的是为了创造一个活跃在QQ群聊的"生命体"。可以目的并不是为了写一个功能齐全的机器人，而是一个尽可能让人感知到真实的类人存在.
> - 程序的功能设计理念基于一个核心的原则："最像而不是好"
> - 主打一个陪伴
> - 如果人类真的需要一个AI来陪伴自己，并不是所有人都需要一个完美的，能解决所有问题的helpful assistant，而是一个会犯错的，拥有自己感知和想法的"生命形式"。
> - 代码会保持开源和开放，但个人希望MaiMbot的运行时数据保持封闭，尽量避免以显式命令来对其进行控制和调试.我认为一个你无法完全掌控的个体才更能让你感觉到它的自主性，而视其成为一个对话机器.

## 📌 注意事项

SengokuCola~~纯编程外行，面向cursor编程，很多代码写得不好多多包涵~~已得到大脑升级

> [!WARNING]
> 本应用生成内容来自人工智能模型，由 AI 生成，请仔细甄别，请勿用于违反法律的用途，AI生成内容不代表本人观点和立场。

## 致谢

- [nonebot2](https://github.com/nonebot/nonebot2): 跨平台 Python 异步聊天机器人框架  
- [NapCat](https://github.com/NapNeko/NapCatQQ): 现代化的基于 NTQQ 的 Bot 协议端实现  

### 贡献者

感谢各位大佬！

<a href="https://github.com/MaiM-with-u/MaiBot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=MaiM-with-u/MaiBot" />
</a>

**也感谢每一位给麦麦发展提出宝贵意见与建议的用户，感谢陪伴麦麦走到现在的你们**

## Stargazers over time

[![Stargazers over time](https://starchart.cc/MaiM-with-u/MaiBot.svg?variant=adaptive)](https://starchart.cc/MaiM-with-u/MaiBot)
