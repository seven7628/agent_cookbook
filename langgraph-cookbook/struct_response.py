from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOllama(base_url="http://localhost:11434", model="qwen2.5:7b")

class Section(BaseModel):
    """A section of a document."""

    title: str = Field(description="The title of the section.")
    content: str = Field(description="The content of the section.")

class Sections(BaseModel):
    """A document with sections."""
    sections: list[Section] = Field(description="The sections of the document.")

planner = llm.with_structured_output(Sections)

res = planner.invoke(
    [
        SystemMessage(content="根据研究主题生成计划。该计划每份信息包括 title 和 content. 其中 title 是信息的标题, content 是信息的内容."),
        HumanMessage(
            content="该报告的主题是: LLM Scaling Law. "
        ),
    ]
)
print(res)