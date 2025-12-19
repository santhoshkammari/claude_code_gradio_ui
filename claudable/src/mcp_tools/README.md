## WebSearch Comparison: MCP vs Claude Built-in
---
*Query: "find top5 rag papers, with 10 parallel search requests"*

| **Metric** | **MCP WebSearch** | **Claude Built-in WebSearch** | **Improvement** |
|------------|-------------------|-------------------------------|-----------------|
| **Duration** | 28,012 ms (28 sec) | 101,649 ms (102 sec) | **3.6x faster** |
| **API Duration** | 24,073 ms | 327,266 ms | **13.6x faster** |
| **Total Cost** | $0.095 USD | $1.515 USD | **94% cost reduction** |
| **Input Tokens** | 20,031 | 30,048 | **33% fewer tokens** |
| **Output Tokens** | 479 | 444 | Similar output |
| **Cache Creation Tokens** | 5,391 | 5,393 | Similar |
| **Cache Read Tokens** | 14,633 | 14,532 | Similar |
| **Web Search Requests** | 10 parallel searches | 10 parallel searches | Similar |
| **Total Turns** | 22 | 22 | Same complexity |

### Performance Summary:

**🚀 Speed Gains:**
- Overall execution: **3.6x faster**
- API processing: **13.6x faster**

**💰 Cost Efficiency:**
- **$1.42 savings per query** (94% reduction)
- **33% fewer input tokens** required

**📊 Resource Usage:**
- Similar output quality with significantly lower resource consumption
- More efficient search strategy vs multiple parallel requests
