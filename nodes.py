import os
import torch
import numpy as np
from PIL import Image
import folder_paths
from typing import Tuple, Optional

class Comfyui_loads_lmages:
    """
    南光AI加载图像(宽高)
    支持单张或批量加载图像，输出图像、遮罩、宽度、高度。
    可选输入端：输入图像、输入遮罩（若提供则直接使用，忽略文件加载）
    """
    NAME = "Comfyui_loads_lmages"
    CATEGORY = "南光AI/图像"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "模式": (["单张", "批量"], {"default": "单张"}),
                "路径": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "输入图像": ("IMAGE",),
                "输入遮罩": ("MASK",),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("图像", "遮罩", "宽度", "高度")
    FUNCTION = "load_images"
    CATEGORY = CATEGORY
    OUTPUT_NODE = False

    def load_images(self, 模式: str, 路径: str, 输入图像: Optional[torch.Tensor] = None, 输入遮罩: Optional[torch.Tensor] = None):
        """
        加载或处理图像
        - 如果提供了 输入图像，则直接使用它，并忽略 模式 和 路径
        - 否则根据模式从路径加载图像
        - 遮罩：优先使用 输入遮罩，若未提供则从图像生成（基于Alpha或全白）
        """
        # 优先使用输入图像
        if 输入图像 is not None:
            # 确保输入图像是4维 [N,H,W,C]
            if 输入图像.dim() == 3:
                输入图像 = 输入图像.unsqueeze(0)
            # 处理遮罩
            if 输入遮罩 is not None:
                mask = 输入遮罩
                # 确保mask与图像同批次数量
                if mask.dim() == 2:
                    mask = mask.unsqueeze(0)
                elif mask.dim() == 3 and mask.shape[0] != 输入图像.shape[0]:
                    # 如果mask是单张但图像是多张，复制mask
                    if mask.shape[0] == 1:
                        mask = mask.repeat(输入图像.shape[0], 1, 1)
            else:
                # 从输入图像生成全白遮罩
                batch, H, W, C = 输入图像.shape
                mask = torch.ones(batch, H, W, dtype=torch.float32)
            # 获取宽度高度（取第一张）
            _, H, W, _ = 输入图像.shape
            return (输入图像, mask, W, H)

        # 没有输入图像，按照原逻辑从文件加载
        if not 路径 or not os.path.exists(路径):
            raise FileNotFoundError(f"路径不存在或未提供: {路径}")

        if 模式 == "单张":
            img_tensor, mask_tensor, w, h = self._load_single(路径)
            # 如果提供了输入遮罩，用输入遮罩覆盖（输入遮罩通常维度匹配，这里单张）
            if 输入遮罩 is not None:
                # 确保输入遮罩与图像尺寸匹配
                if 输入遮罩.dim() == 2:
                    mask_tensor = 输入遮罩.unsqueeze(0)
                elif 输入遮罩.dim() == 3:
                    mask_tensor = 输入遮罩
            return (img_tensor, mask_tensor, w, h)
        else:  # 批量
            if not os.path.isdir(路径):
                raise NotADirectoryError(f"批量模式需要文件夹路径: {路径}")
            exts = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')
            files = []
            for f in os.listdir(路径):
                if f.lower().endswith(exts):
                    full_path = os.path.join(路径, f)
                    files.append(full_path)
            files = list(set(files))
            files.sort()
            if len(files) > 100:
                print(f"[南光AI] 警告：文件夹内图像超过100张，仅加载前100张。")
                files = files[:100]
            if not files:
                raise ValueError(f"文件夹中没有找到图像: {路径}")

            images = []
            masks = []
            target_w = target_h = None
            for idx, fpath in enumerate(files):
                img_t, mask_t, w, h = self._load_single(fpath)
                if idx == 0:
                    target_w, target_h = w, h
                if (w, h) != (target_w, target_h):
                    img_pil, mask_pil = self._load_pil_mask(fpath)
                    img_pil = img_pil.resize((target_w, target_h), Image.Resampling.LANCZOS)
                    mask_pil = mask_pil.resize((target_w, target_h), Image.Resampling.LANCZOS)
                    img_t = self._pil_to_tensor(img_pil)
                    mask_t = self._pil_to_tensor(mask_pil, is_mask=True)
                images.append(img_t)
                masks.append(mask_t)
            image_batch = torch.cat(images, dim=0)
            mask_batch = torch.cat(masks, dim=0)

            # 如果提供了输入遮罩，用输入遮罩覆盖整个批次（需尺寸匹配）
            if 输入遮罩 is not None:
                # 假设输入遮罩是单张或批次，需要广播或重复
                if 输入遮罩.dim() == 2:
                    mask_batch = 输入遮罩.unsqueeze(0).repeat(image_batch.shape[0], 1, 1)
                elif 输入遮罩.dim() == 3:
                    if 输入遮罩.shape[0] == 1:
                        mask_batch = 输入遮罩.repeat(image_batch.shape[0], 1, 1)
                    else:
                        mask_batch = 输入遮xture  # 假设批次匹配
            return (image_batch, mask_batch, target_w, target_h)

    def _load_single(self, file_path: str):
        img_pil, mask_pil = self._load_pil_mask(file_path)
        w, h = img_pil.size
        img_t = self._pil_to_tensor(img_pil)
        mask_t = self._pil_to_tensor(mask_pil, is_mask=True)
        return img_t, mask_t, w, h

    def _load_pil_mask(self, file_path: str):
        try:
            img = Image.open(file_path)
        except Exception as e:
            raise IOError(f"无法打开图像文件 {file_path}: {e}")
        if img.mode == 'RGBA':
            rgb_img = img.convert('RGB')
            mask = img.split()[-1]
            if mask.mode != 'L':
                mask = mask.convert('L')
        else:
            rgb_img = img.convert('RGB')
            mask = Image.new('L', img.size, 255)
        return rgb_img, mask

    def _pil_to_tensor(self, pil_img: Image.Image, is_mask=False):
        img_np = np.array(pil_img).astype(np.float32) / 255.0
        if is_mask:
            if len(img_np.shape) == 3:
                img_np = img_np[:, :, 0]
            tensor = torch.from_numpy(img_np).unsqueeze(0)
            return tensor
        else:
            if img_np.shape[-1] == 4:
                img_np = img_np[:, :, :3]
            tensor = torch.from_numpy(img_np).unsqueeze(0)
            return tensor


NODE_CLASS_MAPPINGS = {
    "Comfyui_loads_lmages": Comfyui_loads_lmages,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Comfyui_loads_lmages": "南光AI加载图像(宽高)",
}