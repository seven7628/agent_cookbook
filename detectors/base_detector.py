from abc import ABC, abstractmethod
from models.base_models import Track, MapData
from typing import Dict

class BaseSceneDetector(ABC):
    @abstractmethod
    def detect(self, track: Track, map_data: MapData) -> Dict:
        """
        检测特定场景
        :return: 场景检测结果（如{"scene_type": "lane_change", "occurred": True}）
        """
        pass