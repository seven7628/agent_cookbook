from pydantic import BaseModel, Field
from typing import Any,List

class Position(BaseModel):
    x: float = Field(description="三维坐标x值")
    y: float = Field(description="三维坐标y值")
    z: float = Field(description="三维坐标z值")
    lane_id: str = Field(description="当前所在车道ID")
    link_id: str = Field(description="当前所在道路连接段ID")
    dis_to_link: float = Field(description="到道路连接段的距离")
    position_type: str = Field(description="位置类型（如ON_LANE）")

class MovingInfo(BaseModel):
    speed: float = Field(description="当前速度（m/s）")
    acceleration: float = Field(description="当前加速度（m/s²）")
    heading: float = Field(description="当前航向角（弧度）")

class Track(BaseModel):
    position: Position = Field(description="位置信息")
    frame_id: int = Field(description="帧ID")
    obj_id: str = Field(description="目标对象ID")
    moving_info: MovingInfo = Field(description="运动信息")

class MapData(BaseModel):
    junctions: List[Any] = Field(default={}, description="高精地图车道数据（lane_id为键）")
    segments: List[Any] = Field(default={}, description="道路连接段数据（link_id为键）")