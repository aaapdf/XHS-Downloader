from source.expansion import Namespace
from .request import Html

__all__ = ["Video"]


class Video:
    VIDEO_LINK = (
        "video",
        "consumer",
        "originVideoKey",
    )

    @classmethod
    def deal_video_link(
        cls,
        data: Namespace,
        preference="resolution",
    ):
        return cls.generate_video_link(data) or cls.get_video_link(data, preference)

    @classmethod
    def generate_video_link(cls, data: Namespace) -> list:
        return (
            [Html.format_url(f"https://sns-video-bd.xhscdn.com/{t}")]
            if (t := data.safe_extract(".".join(cls.VIDEO_LINK)))
            else []
        )

    @classmethod
    def get_video_link(
        cls,
        data: Namespace,
        preference="resolution",
    ) -> list:
        if not (items := cls.get_video_items(data)):
            return []
        
        # 加入 or 0 等后备方案，防止某个混淆的视频流里缺少相应字段时触发排序异常
        match preference:
            case "resolution":
                items.sort(key=lambda x: x.height or x.videoBitrate or 0)
            case "bitrate":
                items.sort(key=lambda x: x.videoBitrate or x.avgBitrate or 0)
            case "size":
                items.sort(key=lambda x: x.size or 0)
            case _:
                raise ValueError(f"Invalid video preference value: {preference}")
                
        return [b[0]] if (b := items[-1].backupUrls) else [items[-1].masterUrl]

    @staticmethod
    def get_video_items(data: Namespace) -> list:
        # 建立我们之前测试出的新编码字段映射，优先寻找新字段，也保留旧字段向下兼容
        codec_keys = ['EF5', 'EF4', 'EF7', 'EF6', 'h265', 'h264', 'av1']
        items = []
        for codec in codec_keys:
            # 循环提取每种编码下的视频流列表
            if streams := data.safe_extract(f"video.media.stream.{codec}", []):
                # 确保提取出来的是列表格式，全部装进 items 里
                if isinstance(streams, list):
                    items.extend(streams)
        return items
