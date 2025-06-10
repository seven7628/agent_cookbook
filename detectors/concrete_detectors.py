from .base_detector import BaseSceneDetector
from models.base_models import Track, MapData
from typing import Dict

class SuddenStopDetector(BaseSceneDetector):
    def detect(self, track: Track, _: MapData) -> Dict:
        return {
            "scene_type": "sudden_stop",
            "occurred": track.moving_info.acceleration < -3.0,
            "speed_when_stop": track.moving_info.speed
        }

class AdvancedLaneChangeDetector(BaseSceneDetector):
    def detect(self, track: Track, map_data: MapData) -> Dict:
        """结合文件读写和数据分析的变道检测"""
        # 实际应实现具体检测逻辑（示例伪代码）
        return {
            "scene_type": "advanced_lane_change",
            "occurred": False,
            "analysis_data": "航向角变化率: ..."
        }