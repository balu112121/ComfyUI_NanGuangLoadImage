# 南光AI加载图像(宽高) - ComfyUI 自定义节点

## 简介
该节点用于加载单张或批量图像，输出图像、遮罩、宽度、高度。支持透明通道（自动提取Alpha作为遮罩），批量模式最多100张，自动去重并统一尺寸。

**新特性**：节点现在具有可选输入端“输入图像”和“输入遮罩”。如果连接了输入图像，则直接使用该图像（忽略文件加载），输入遮罩可选。

## 安装
1. 将本文件夹 `ComfyUI_NanGuangLoadImage` 复制到 ComfyUI 的 `custom_nodes` 目录下。
2. 重启 ComfyUI（或点击刷新按钮）。
3. 在节点菜单中找到 `南光AI/图像` → `南光AI加载图像(宽高)`。

## 使用方法

### 输入端（可选）
- **输入图像**：可直接接入外部图像张量。如果连接，将忽略下方的“模式”和“路径”设置，直接输出此图像。
- **输入遮罩**：可选，为输出提供遮罩。若不提供，节点会自动生成（从输入图像的Alpha通道或全白）。

### 参数（仅在未连接输入图像时生效）
- **模式**：选择“单张”或“批量”。
  - 单张：路径需填写图像文件的完整路径（如 `C:/images/photo.png`）。
  - 批量：路径需填写包含多张图像的文件夹路径（如 `C:/images/batch/`）。
- **路径**：根据模式填写文件或文件夹路径。Windows下建议使用正斜杠 `/` 或双反斜杠 `\\`。

### 输出
- **图像**：RGB张量，形状 `[1, H, W, 3]`（单张）或 `[N, H, W, 3]`（批量，N≤100）。
- **遮罩**：单通道张量，形状 `[1, H, W]` 或 `[N, H, W]`，值域0~1（1=不透明）。
- **宽度**、**高度**：整数，图像的实际尺寸（批量模式下为第一张图的尺寸）。

## 工作流示例
见 `workflows/example_workflow.json`

## 常见问题
**Q：如何同时使用输入图像和文件加载？**  
A：若连接了输入图像，则文件加载被忽略。您可以将输入图像设为可选，通过控制连线来切换。

**Q：遮罩输入与自动生成的遮罩哪个优先级高？**  
A：如果提供了输入遮罩，将优先使用输入遮罩；否则节点会自动生成。

### 南光AIGC绘画

南光AIGC-AIGC全能方案设计解决专家 VX:nankodesign2001

RH新人注册网址---
粉丝福利：https://pre.runninghub.cn/?inviteCode=t7ztfeiw-填入邀请码，领1000RH币，每天登录还有100币 邀请码：t7ztfeiw

仙宫云新人注册网址---
https://www.xiangongyun.com/register/MJAT43 新人注册仙宫云送5元代金券， 填写邀请码（输入我们的邀请码：MJAT43 ）还额外送3元代金券 完成后可以得到仙宫云8元账户余额，可以免费带你玩转5小时发高配4090 D显卡AIGC绘画。


PS软件（AI）插件
https://istarry.com.cn/?sfrom=jbEHmC
提供多种强大的AI功能，轻松提升设计效率，邀您免费体验


### 三大自媒体平台

小红书
https://www.xiaohongshu.com/user/profile/5fe63b41000000000100811d?m_source=itab

抖音
https://www.douyin.com/user/self?showTab=post

bilibili（B站）
https://space.bilibili.com/404783526


### 如果您受益于本项目，不妨请作者喝杯咖啡，您的支持是我最大的动力

<div style="display: flex; justify-content: left; gap: 20px;">
    <img src="https://github.com/balu112121/ComfyUI_NanKo_AI_Recognize/blob/main/Alipay.jpg" width="300" alt="支付宝收款码">
    <img src="https://github.com/balu112121/ComfyUI_NanKo_AI_Recognize/blob/main/WeChat.jpg" width="300" alt="微信收款码">
</div>

# 商务合作
如果您有定制工作流/节点的需求，或者想要学习插件制作的相关课程，请联系我
wechat:nankodesign2001