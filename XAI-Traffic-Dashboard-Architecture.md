# XAI Urban Traffic Management Dashboard — 系统架构与功能规格

> 项目名称：XAI Urban Traffic Management Dashboard (XAI-TMD)
> 课程：CCS5204 Internet of Things
> 目标：对 IoT 数据进行清洗、分析和可视化展示
> 数据集：Smart City Traffic Stress Index Dataset (Kaggle)
> 技术栈：Django 5 + Vue 3 + JavaScript + MySQL 8.0

---

## 一、项目目标

基于 Kaggle 公开数据集，完成以下核心任务：

1. **数据清洗**：处理缺失值、异常值、数据标准化
2. **数据分析**：统计描述、时序分析、区域分析
3. **可视化展示**：KPI 总览、趋势图表、分布图表
4. **XAI 可解释分析**：使用 KernelExplainer（SHAP）和 LimeTabularExplainer（LIME），直接解释数据本身的统计规律，**无需训练 ML 模型**

---

## 二、系统架构

### 2.1 整体架构图

```
┌──────────────────────────────────────────────────────────────┐
│                     Vue 3 + Vite + ECharts                   │
│                                                               │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│   │  Traffic      │  │     SHAP      │  │    LIME      │    │
│   │  Overview     │  │  Explanation  │  │  Explanation │    │
│   │  (总览页面)   │  │  (解释页面)   │  │  (解释页面)  │    │
│   └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                               │
│   ┌──────────────┐                                          │
│   │  Data Table   │                                          │
│   │  (数据表页面)  │                                          │
│   └──────────────┘                                          │
│                         Axios (30s polling)                   │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP / REST
┌─────────────────────────────▼───────────────────────────────┐
│                  Django 5 + Django REST Framework              │
│                                                               │
│    traffic             xai              monitoring            │
│    ──────            ────              ──────────            │
│    · 数据清洗         · SHAP 计算       · /health 健康检查    │
│    · 统计分析         · LIME 计算       · /stats 数据统计      │
│    · 趋势查询         · 解释结果查询                           │
│                                                               │
│    shared/error.py:  TypedError 全局错误处理                   │
│    shared/config.py: 配置中心（环境变量，fail-fast）           │
└─────────────────────────────┬───────────────────────────────┘
                              │ Django ORM
┌─────────────────────────────▼───────────────────────────────┐
│                        MySQL 8.0                               │
│                                                               │
│    traffic_record   xai_shap_local   xai_lime_local         │
│    xai_shap_global  monitoring_stats                          │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 部署架构

```
                         Nginx (端口 80/443)
                      反向代理 + 静态文件服务
                              │
              ┌───────────────┴───────────────┐
              │                               │
    [Vue 构建产物 dist/]           [Django Gunicorn]
       静态资源 Nginx 托管               端口 8000
                                              │
                                     ┌────────▼────────┐
                                     │   MySQL 8.0   │
                                     │   端口 3306    │
                                     └────────┴────────┘
```

### 2.3 Django App 结构

| App | Model | Service | API 前缀 | 职责 |
|-----|-------|---------|---------|------|
| `traffic` | `TrafficRecord` | `TrafficService` | `/api/traffic/` | 数据清洗/统计/趋势/区域分析 |
| `xai` | `SHAPGlobal, SHAPLocal, LIMELocal` | `SHAPService, LIMEService` | `/api/xai/` | SHAP/LIME 解释计算与查询 |
| `monitoring` | `MonitoringStats` | `MonitoringService` | `/api/system/` | 健康检查/数据统计 |

---

## 三、ETL 数据处理流水线

```
[Kaggle CSV: Smart City Traffic Stress Index Dataset]
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  STEP 1: 数据加载与清洗                          │
│  · pandas read_csv 读取原始数据                  │
│  · 缺失值检测：均值/中位数填补                    │
│  · 异常值过滤：基于 IQR 识别并删除异常记录         │
│  · 数据类型标准化：时间格式/数值格式/类别编码      │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  STEP 2: 特征工程                                │
│  · 时间特征提取: hour, day_of_week, is_weekend  │
│  · 目标变量构建: stress_level (低/中/高)         │
│  · 特征标准化: StandardScaler (用于 LIME)        │
│  · 类别变量编码: LabelEncoder (weather/driver)  │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  STEP 3: SHAP 值预计算 (KernelExplainer)         │
│  · 无需训练模型，直接解释数据本身的统计规律        │
│  · shap.KernelExplainer(predict_fn, X_sample)   │
│  · 全局重要性: mean(|SHAP|) 降序 → shap_global │
│  · 局部解释: 每条记录 SHAP 值 → xai_shap_local  │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  STEP 4: LIME 解释预计算                        │
│  · lime.LimeTabularExplainer 批量计算           │
│  · 基于线性回归局部近似                          │
│  · 每条记录 LIME 局部解释 → xai_lime_local     │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  STEP 5: 数据持久化 (Django ORM → MySQL)         │
│  · bulk_create 批量写入                         │
│  · transaction.atomic 保证事务一致性             │
└─────────────────────────────────────────────────┘
```

> **ETL 执行时机**：项目部署时一次性运行，数据入库后前端仅做查询展示，不再执行 ETL。

---

## 四、功能总表

### 4.1 数据清洗

| 序号 | 功能点 | 描述 |
|:----:|--------|------|
| 1 | 缺失值处理 | 自动检测并填补缺失记录，支持均值/中位数策略 |
| 2 | 异常值过滤 | 基于 IQR 四分位距识别并过滤异常压力指数记录 |
| 3 | 数据类型标准化 | 统一字段格式：时间格式规范、数值精度统一、类别字段编码 |

### 4.2 数据分析与展示

| 序号 | 功能点 | 描述 |
|:----:|--------|------|
| 4 | KPI 总览卡片 | 展示平均压力指数、记录总数、高压力记录占比、趋势箭头 |
| 5 | 压力分布图表 | 环形饼图，低/中/高各等级记录数及占比 |
| 6 | 时间序列趋势 | 折线图展示压力指数随时间变化，支持按小时/日切换粒度 |
| 7 | 区域统计排行 | 横向柱状图，各区域平均压力指数从高到低排序 |
| 8 | 原始数据表格 | 分页展示清洗后的数据，支持按列排序 |

### 4.3 SHAP 可解释分析

| 序号 | 功能点 | 描述 |
|:----:|--------|------|
| 9 | 全局特征重要性 | 水平柱状图，mean |SHAP| 降序排列，展示各特征对 stress_index 的贡献度（基于数据统计，无模型） |
| 10 | 单条局部解释 | 输入记录ID，返回该条数据的 SHAP 分解（水母图），基于 KernelExplainer 直接解释数据，逐特征展示正负贡献 |
| 11 | SHAP 摘要散点图 | 散点图：X轴为特征原始值，Y轴为 SHAP 值，颜色区分压力等级，直观展示特征影响力方向与强度 |

### 4.4 LIME 可解释分析

| 序号 | 功能点 | 描述 |
|:----:|--------|------|
| 12 | 单条局部解释 | 输入记录ID，返回 LIME 线性近似解释（特征名称 + 权重列表） |
| 13 | LIME 可视化 | 水平柱状图，正权重绿色向右、负权重红色向左，直观展示各特征正负贡献 |

### 4.5 SHAP 与 LIME 对比

| 序号 | 功能点 | 描述 |
|:----:|--------|------|
| 14 | 同一记录两种方法对比 | 输入记录ID，同时展示 SHAP 水母图和 LIME 柱状图，基于同一份数据对比两种解释方法的差异 |

---

## 五、API 端点总览

| 端点 | 方法 | 所属模块 | 说明 |
|------|:----:|---------|------|
| `GET /api/traffic/summary` | GET | traffic | KPI 总览（平均指数/记录数/高压力占比） |
| `GET /api/traffic/distribution` | GET | traffic | 压力等级分布（低/中/高 各等级数量及占比） |
| `GET /api/traffic/timeseries` | GET | traffic | 时序趋势数据（时间粒度可参数切换） |
| `GET /api/traffic/zone-stats` | GET | traffic | 区域统计排行（各区域平均压力指数排序） |
| `GET /api/traffic/records` | GET | traffic | 原始数据分页表（page/page_size/sort 参数） |
| `GET /api/xai/shap/global` | GET | xai | SHAP 全局特征重要性 |
| `GET /api/xai/shap/local/<record_id>` | GET | xai | 单条 SHAP 局部解释 |
| `GET /api/xai/shap/summary` | GET | xai | SHAP 摘要散点图数据 |
| `GET /api/xai/lime/local/<record_id>` | GET | xai | 单条 LIME 局部解释 |
| `GET /api/xai/compare/<record_id>` | GET | xai | SHAP 与 LIME 同一记录对比 |
| `GET /api/system/health` | GET | monitoring | 健康检查（Django + MySQL 状态） |
| `GET /api/system/stats` | GET | monitoring | 数据统计（记录数/区域数/时间范围） |

---

## 六、数据库表结构

| 表名 | 所属 App | 说明 |
|------|---------|------|
| `traffic_record` | traffic | 清洗后的交通记录原始数据 |
| `xai_shap_global` | xai | SHAP 全局特征重要性（预计算结果） |
| `xai_shap_local` | xai | SHAP 局部解释（每条记录一行） |
| `xai_lime_local` | xai | LIME 局部解释（每条记录一行） |
| `monitoring_stats` | monitoring | 系统统计数据（记录数/区域数等） |

---

## 七、前端页面结构

```
/                     # 重定向到 /traffic/overview
/traffic/overview     # 交通总览：KPI卡片 + 压力分布饼图 + 时序曲线
/traffic/zones        # 区域排行：区域统计柱状图
/traffic/records      # 原始数据：分页数据表格
/xai/shap             # SHAP 解释：全局重要性 + 摘要散点图 + 单条水母图
/xai/lime             # LIME 解释：单条解释 + 可视化
/xai/compare          # SHAP vs LIME 对比
```

---

## 八、技术栈汇总

| 层次 | 技术选型 |
|------|---------|
| 后端 | Python 3.10+ / Django 5 / Django REST Framework |
| XAI 计算 | shap (KernelExplainer) / lime (LimeTabularExplainer) |
| 数据库 | MySQL 8.0（Django ORM） |
| 数据处理 | pandas / numpy / scikit-learn（线性回归，用于 LIME 近似） |
| 前端 | Vue 3 + Vite + JavaScript（ES6+） |
| 图表 | ECharts 5 |
| CSS | Tailwind CSS |
| 状态管理 | Pinia |
| HTTP 客户端 | Axios |
| 路由 | Vue Router 4 |
