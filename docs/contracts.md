# 业务数据与接口

行程 entered、left 为带时区时间；left 为 null 表示在资料截点尚未出场。vehicle_id 为已确认的车辆键，同车多次出现不是重复。prior_used 为该日资料覆盖开始前的已用免费次数，null 表示未知，不能当零。

价表的 quota 按车辆当地入场自然日共享，闭区间免费时长，超时是否扣除免费时长由 deduct_grace 决定。夜间定义为 18:00 至次日 08:00；跨越时段的服务报价会分别返回费用组成，额度归属仍为入场日。calendar 覆盖节假日并给出 quota_bonus。所有金额是整数分。

POST /v1/quote 接收 revision、trip_id、policy_id、free_available；返回该版本完整行程的 cents、parts、consumes_quota 和 evidence。短时全免或扣除免费时长均占一次额度，没有额度时从入场收费；夜间封顶本身不占额度。尚未结束的行程返回 422。报价是无副作用查询，不会代管共享额度。现有 summary 只描述行程数量和完整行程分钟数。

## 资料发布

GET /v1/catalog 返回 revision、cutoff、settings 以及表名。GET /v1/tables/表名 按 revision、offset、limit 分页。默认 31 行，最多 100 行；next=null 表示结束。错误版本返回 409，参数错误返回 400，领域查询不可计算时返回 422。资料从 JSON 加载后对当前实例不可变；重启可换一个发布版本。

所有时间均为带 +08:00 的 ISO 8601 字符串，资料窗口用半开区间，只有免费时长阈值明确包含端点。计数为非负整数；null 表示未观察或未知，不等于零。来源分页顺序不是业务先后顺序。来源参数 revision 必须与资料一致。

业务服务现有 GET /v1/summary、GET /v1/reports/标识和 GET /health。概览保留 revision 和 cutoff，store.py 对规范 JSON 计算 SHA-256，内容相同重复读取不会产生不同标识。新的研究结果可独立扩展，不应改变现有概览指标的含义。
