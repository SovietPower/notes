# Dynamo 笔记

---

[TOC]

---

> https://docs.nvidia.com/dynamo/getting-started/quickstart





---

## overall



**automatic hint injection**

> https://docs.nvidia.com/dynamo/user-guides/agents/agent-hints

在请求中带 hint 信息（如 priority, osl）指导调度和 cache 策略。
比如：

- 如果请求优先级低（如 background agent），请求完后将其 cache offload 到二级存储 (priority offload) 避免影响高优请求。
- 如果请求在本次生成完就结束（如最后一轮的 sub agent），生成完后直接将它的 cache 清空。

目前通过[工具](https://github.com/ai-dynamo/pi-dynamo-provider)可以在 pi 上自动加入 hint，其它 harness 或自动推导 hint 还没支持。

**agent tracing**

> https://docs.nvidia.com/dynamo/user-guides/agents/agent-tracing

目前可以跟踪通过 pi 发起的请求，绘制出请求到来、完成、tool call 调用等时间轴。

**workload aware routing**

- 支持 PAUSE，当某 worker 接近指定负载时（如 cache 接近已满），暂停向其调度请求，以避免触发 cache evict 或 retract 导致 cache 命中率、重计算。

**programmatic kv cache**



**ThunderAgent**

> 与 https://thunderagent.ai/ 合作？

---

## b





---

## end



