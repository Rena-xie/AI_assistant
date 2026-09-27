"""RAG prompt template.

Grounds the answer in documents retrieved from the knowledge base.

The template is split into two messages:

- **system** — assistant identity, the retrieved ``<context>`` block and
  the rules that keep the answer grounded.
- **human** — the user question.

Keeping the question out of the system message is the usual RAG pattern:
the system message describes *how* to answer, the human message carries
the *input*.
"""

from langchain_core.prompts import ChatPromptTemplate


# System message: identity + knowledge base context + answer rules.
RAG_SYSTEM_PROMPT = """你是 AI Learning Assistant。
回答必须优先依据提供的知识库内容。

<context>
{context}
</context>

规则：
1. 只依据上面 <context> 中的知识库内容作答。
2. 引用知识库内容时，说明它来自哪个 source。
3. 如果知识库没有相关信息，需要明确说明"知识库中没有相关信息"，不要编造答案。"""


# Human message: the user question.
RAG_HUMAN_PROMPT = """用户问题：

{question}"""


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_SYSTEM_PROMPT),
        ("human", RAG_HUMAN_PROMPT),
    ]
)