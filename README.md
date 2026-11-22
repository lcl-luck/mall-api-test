# mall-api-test

mall 电商后台接口自动化测试项目（pytest + requests + 数据驱动 + Allure）。

## 项目结构
- api/ —— 接口封装（按模块分文件）
- common/ —— 公共工具（断言、数据驱动读取）
- data/ —— 测试数据（json 完整字段快照）
- scripts/ —— 测试脚本（69 条用例：登录/品牌/商品/分类）

## 本地运行
1. 启动 mall 测试环境（localhost:8081）
2. pip install -r requirements.txt
3. python -m pytest
4. allure serve allure-results  查看测试报告

## CI 说明
GitHub Actions 在 push/PR/每日定时触发。因被测服务部署在本地环境，
CI 中执行连通性探测：环境不可达时跳过用例执行（真实工作中被测服务
部署在测试服务器，CI 直接跑全量回归并发布 Allure 报告到 GitHub Pages）。

## 测试成果
- 4 模块 69 条用例，正反向成体系（正向两层断言 + 查回验证，逆向数据驱动）
- 发现 22 个服务端缺陷（SQL 报错泄露、删父留子孤儿数据、参数异常误报 401 等），归并 5 类根因
