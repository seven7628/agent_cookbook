from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from langchain.agents import LLMSingleActionAgent, AgentOutputParser, AgentExecutor
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish
import re
# from tools.custom_tools import DataParserTool, SceneDetectorTool
from langchain_experimental.tools import PythonREPLTool
from langchain_community.agent_toolkits import FileManagementToolkit

# from agents.concrete_agents import MapQueryAgent, SceneDetectorAgent
from detectors.concrete_detectors import SuddenStopDetector, AdvancedLaneChangeDetector

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
    input_variables: list[str] = ["input", "tools", "map_file_path", "output_dir"]  # 添加类型注解
    
    def format(self, **kwargs) -> str:
        tools_str = "\n".join([f"{tool.name}: {tool.description}" for tool in kwargs["tools"]])
        return PLANNER_PROMPT_TEMPLATE.format(
            tools=tools_str,
            input=kwargs["input"],
            map_file_path=kwargs["map_file_path"],
            output_dir=kwargs["output_dir"]
        )

class PlannerAgent:
    def __init__(self, llm, map_file_path: str, output_dir: str = "./results"):
        # self.map_agent = MapQueryAgent(map_file_path)
        # self.detector_agent = SceneDetectorAgent()
        # self.detector_agent.register_detector(SuddenStopDetector())
        # self.detector_agent.register_detector(AdvancedLaneChangeDetector())
        
        self.tools = [
            # DataParserTool(),
            PythonREPLTool(),
            # FileManagementToolkit,
            # FileSystemTool(),
            # SceneDetectorTool(self.detector_agent)
        ]
        
        self.prompt = PlannerPromptTemplate()
        self.llm_chain = LLMChain(llm=llm, prompt=self.prompt)
        self.output_parser = self._get_output_parser()
        
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
            "output_dir": self.output_dir,
            "tools": self.tools
        })