from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.agents import AgentExecutor
from langchain.schema import BaseMessage, AIMessage, HumanMessage
from langchain.tools import FileSystemTool, PythonREPLTool  # 新增工具导入
from langgraph import Graph, Node, build_graph
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain import LLMChain
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish
import re

# ---------------------- Pydantic 数据模型定义 ----------------------
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
    lanes: Dict[str, Any] = Field(default={}, description="高精地图车道数据（lane_id为键）")
    links: Dict[str, Any] = Field(default={}, description="道路连接段数据（link_id为键）")

# ---------------------- LangGraph 智能体基类 ----------------------
class BaseAgent(Node):
    @abstractmethod
    def run(self, input: Any) -> Any:
        """智能体核心处理逻辑"""
        pass

    async def _call(self, input: Any) -> Any:
        return self.run(input)

# ---------------------- 具体智能体实现 ----------------------
class DataParserAgent(BaseAgent):
    def run(self, raw_data: List[Dict]) -> List[Track]:
        """将原始字典数据转换为Track模型列表"""
        return [Track.model_validate(item) for item in raw_data]

class MapQueryAgent(BaseAgent):
    def __init__(self, map_file_path: str):
        self.map_file_path = map_file_path
        self.map_data = self._load_map()

    def _load_map(self) -> MapData:
        """加载并解析高精地图文件"""
        with open(self.map_file_path, "r") as f:
            raw_map = f.read()
        return MapData.model_validate_json(raw_map)

    def run(self, _: Any) -> MapData:
        """返回预加载的地图数据"""
        return self.map_data

class SceneDetectorAgent(BaseAgent):
    def __init__(self):
        self.detectors: List[BaseSceneDetector] = []

    def register_detector(self, detector: "BaseSceneDetector") -> None:
        """注册新场景检测器"""
        self.detectors.append(detector)

    def run(self, data: tuple[List[Track], MapData]) -> List[Dict]:
        """执行多场景检测"""
        tracks, map_data = data
        results = []
        for track in tracks:
            for detector in self.detectors:
                results.append(detector.detect(track, map_data))
        return results

# ---------------------- 场景检测抽象基类 ----------------------
class BaseSceneDetector(ABC):
    @abstractmethod
    def detect(self, track: Track, map_data: MapData) -> Dict:
        """
        检测特定场景
        :return: 场景检测结果（如{"scene_type": "lane_change", "occurred": True}）
        """
        pass

# 示例：急停检测器（基于Pydantic数据验证）
class SuddenStopDetector(BaseSceneDetector):
    def detect(self, track: Track, _: MapData) -> Dict:
        return {
            "scene_type": "sudden_stop",
            "occurred": track.moving_info.acceleration < -3.0,  # 使用Pydantic模型字段
            "speed_when_stop": track.moving_info.speed
        }

class AdvancedLaneChangeDetector(BaseSceneDetector):
    def detect(self, track: Track, map_data: MapData) -> Dict:
        """结合文件读写和数据分析的变道检测"""
        # 示例逻辑：读取历史轨迹文件（使用FileSystemTool）
        # 伪代码：history_tracks = tool.run("cat ./history_tracks.json")
        # 计算航向角变化率（使用PythonREPLTool）
        # 伪代码：heading_diff = tool.run(f"({track.moving_info.heading} - prev_heading)/0.1")
        return {
            "scene_type": "advanced_lane_change",
            "occurred": False,  # 实际应替换为数据分析结果
            "analysis_data": "航向角变化率: ..."  # 包含数据分析结果
        }

# ---------------------- 主流程控制器 ----------------------
class ScenarioRecognitionSystem:
    def __init__(self, map_file_path: str):
        # 初始化智能体
        self.parser = DataParserAgent()
        self.map_agent = MapQueryAgent(map_file_path)
        self.detector_agent = SceneDetectorAgent()
        
        # 注册默认检测器
        self.detector_agent.register_detector(SuddenStopDetector())
        
        # 构建LangGraph交互图
        self.graph = self._build_graph()

    def _build_graph(self) -> Graph:
        """定义智能体交互流程"""
        @build_graph
        def flow():
            raw_tracks = HumanMessage("输入原始轨迹数据")  # 输入入口
            parsed_tracks = self.parser(raw_tracks)       # 数据解析
            map_data = self.map_agent("")                 # 获取地图数据
            result = self.detector_agent((parsed_tracks, map_data))  # 场景检测
            return AIMessage(result)                      # 输出结果
        return flow

    def run(self, raw_tracks: List[Dict]) -> List[Dict]:
        """执行检测流程（集成文件系统和数据分析工具）"""
        # 初始化工具：文件系统操作工具和Python REPL工具
        tools = [
            FileSystemTool(),
            PythonREPLTool()
        ]
        # 创建包含工具的executor（原第127行修改）
        executor = AgentExecutor.from_agent_and_tools(agent=self.graph, tools=tools)
        # 运行时传递原始轨迹数据（原第128行保持逻辑）
        return executor.run(raw_tracks)

# ---------------------- 新增工具定义 ----------------------
class DataParserTool(Tool):
    def __init__(self):
        super().__init__(
            name="DataParser",
            func=self.run_parser,
            description="用于解析原始轨迹数据为结构化Track对象，输入应为原始字典列表"
        )
    
    def run_parser(self, raw_data: str) -> List[Track]:
        """使用Pydantic模型解析数据"""
        return [Track.model_validate(eval(raw_data))]  # eval用于将字符串转回字典列表

class SceneDetectorTool(Tool):
    def __init__(self, detector_agent: SceneDetectorAgent):
        self.detector_agent = detector_agent
        super().__init__(
            name="SceneDetector",
            func=self.run_detection,
            description="用于执行场景识别，输入应为元组（Track列表, MapData对象）"
        )
    
    def run_detection(self, input_data: str) -> List[Dict]:
        """调用已注册的场景检测器"""
        tracks, map_data = eval(input_data)
        return self.detector_agent.run((tracks, map_data))

# ---------------------- Planner 提示模板 ----------------------
PLANNER_PROMPT_TEMPLATE = """
你是一个专业的场景分析任务规划智能体（Planner），需要按以下步骤处理用户输入的轨迹数据：

任务步骤：
1. 数据解析：使用`DataParser`工具将用户输入的原始轨迹数据（JSON列表）转换为结构化的Track对象列表
2. 数据分析：使用`PythonREPLTool`对Track数据进行统计分析（如速度均值、加速度极值），并使用`FileSystemTool`将分析结果写入`./analysis_report.json`
3. 场景识别：使用`SceneDetector`工具，结合步骤1的Track数据和MapQueryAgent加载的地图数据（路径：{map_file_path}）进行场景检测
4. 结果总结：使用`PythonREPLTool`对步骤2的数据分析结果和步骤3的场景识别结果进行综合总结，并使用`FileSystemTool`将最终结论写入`{output_dir}/final_summary.json`

当前可用工具列表：
{tools}

请严格按照以上步骤执行，每一步骤明确使用指定工具。你的最终输出应为任务执行结果的总结。

用户输入数据：{input}
"""

class PlannerPromptTemplate(StringPromptTemplate):
    input_variables = ["input", "tools", "map_file_path", "output_dir"]
    
    def format(self, **kwargs) -> str:
        tools_str = "\n".join([f"{tool.name}: {tool.description}" for tool in kwargs["tools"]])
        return PLANNER_PROMPT_TEMPLATE.format(
            tools=tools_str,
            input=kwargs["input"],
            map_file_path=kwargs["map_file_path"],
            output_dir=kwargs["output_dir"]
        )

# ---------------------- Planner 智能体实现 ----------------------
class PlannerAgent:
    def __init__(self, llm, map_file_path: str, output_dir: str = "./results"):
        # 初始化基础组件
        self.map_agent = MapQueryAgent(map_file_path)
        self.detector_agent = SceneDetectorAgent()
        self.detector_agent.register_detector(SuddenStopDetector())
        self.detector_agent.register_detector(AdvancedLaneChangeDetector())
        
        # 定义工具集合
        self.tools = [
            DataParserTool(),
            PythonREPLTool(),
            FileSystemTool(),
            SceneDetectorTool(self.detector_agent)
        ]
        
        # 初始化提示模板和LLM链
        self.prompt = PlannerPromptTemplate()
        self.llm_chain = LLMChain(llm=llm, prompt=self.prompt)
        
        # 配置代理输出解析器
        self.output_parser = self._get_output_parser()
        
        # 创建代理执行器
        self.agent = LLMSingleActionAgent(
            llm_chain=self.llm_chain,
            output_parser=self.output_parser,
            stop=["\nObservation:"],
            allowed_tools=[tool.name for tool in self.tools]
        )
        self.executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
        
        self.map_file_path = map_file_path
        self.output_dir = output_dir

    def _get_output_parser(self) -> AgentOutputParser:
        class PlannerOutputParser(AgentOutputParser):
            def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
                if "Final Answer:" in llm_output:
                    return AgentFinish(
                        return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                        log=llm_output
                    )
                # 解析工具调用（示例匹配模式）
                match = re.search(r"Action: (.*?)\nAction Input: (.*)", llm_output, re.DOTALL)
                if not match:
                    raise ValueError(f"无法解析LLM输出: {llm_output}")
                action = match.group(1).strip()
                action_input = match.group(2).strip()
                return AgentAction(
                    tool=action,
                    tool_input=action_input,
                    log=llm_output
                )
        return PlannerOutputParser()

    def run(self, user_input: str) -> str:
        """执行完整任务规划流程"""
        return self.executor.run({
            "input": user_input,
            "map_file_path": self.map_file_path,
            "output_dir": self.output_dir
        })

# ---------------------- 使用示例 ----------------------
if __name__ == "__main__":
    from langchain.llms import OpenAI  # 需要安装openai库并配置API key
    llm = OpenAI(temperature=0)  # 选择确定性强的模型提高任务准确率
    
    # 初始化Planner（输出目录设为./scenario_results）
    planner = PlannerAgent(
        llm=llm,
        map_file_path="map.json",
        output_dir="./scenario_results"
    )
    
    # 用户输入原始轨迹数据（JSON字符串格式）
    user_input = '''[{
        "position": {
            "x": 1.0, "y": 2.0, "z": 3.0,
            "lane_id": "1", "link_id": "1-2",
            "dis_to_link": 10.0, "position_type": "ON_LANE"
        },
        "frame_id": 100,
        "obj_id": "ego",
        "moving_info": {
            "speed": 10.0, "acceleration": -4.0, "heading": 0.0
        }
    }]'''
    
    # 执行规划流程
    result = planner.run(user_input)
    print("任务执行结果：", result)