from langchain_ollama import ChatOllama
from planner.planner_components import PlannerAgent

if __name__ == "__main__":
    llm = ChatOllama(base_url="http://localhost:11434", model="qwen2.5:7b")
    
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