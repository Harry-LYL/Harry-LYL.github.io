#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 alaric.it.com 镜像替换为李彦龙的内容。JS chunk 与 HTML 双改。v2"""
import re, html as htmllib

JS_PATH = '_next/static/chunks/0ccz6j2vqtl32.js'
HTML_PATH = 'index.html'
NBSP = '\xa0'

js = open(JS_PATH, encoding='utf-8').read()
ht = open(HTML_PATH, encoding='utf-8').read()

errors = []
ht_pairs = []  # (old, new) 统一最后按长度降序应用

def region_bounds(text, anchor):
    s = text.find(anchor)
    assert s >= 0, anchor
    b = text.find('[', s)
    depth = 0
    for i in range(b, len(text)):
        c = text[i]
        if c in '[{(': depth += 1
        elif c in ']})':
            depth -= 1
            if depth == 0:
                return b, i + 1
    raise ValueError(anchor)

def sub_zhen(old_zh, new_zh, new_en):
    """JS: 替换 zh/en 对(兼容单双引号定界);HTML: 记录 zh 对。"""
    global js
    pat = re.compile(r'zh:(?P<q>["\'])' + re.escape(old_zh) + r'(?P=q),en:(?P<q2>["\'])(?:[^"\']|\\.)*(?P=q2)')
    rep = 'zh:"' + new_zh + '",en:"' + new_en + '"'
    js, n = pat.subn(lambda m: rep, js)
    if n == 0:
        errors.append(f'[JS zhen] MISS: {old_zh[:30]}')
    ht_pairs.append((old_zh, new_zh))

def sub_cond(old_zh, new_zh, new_en):
    global js
    pat = re.compile(r'"zh"===e\?(?P<q>["\'])' + re.escape(old_zh) + r'(?P=q):(?P<q2>["\'])(?:[^"\']|\\.)*(?P=q2)')
    rep = '"zh"===e?"' + new_zh + '":"' + new_en + '"'
    js, n = pat.subn(lambda m: rep, js)
    if n == 0:
        errors.append(f'[JS cond] MISS: {old_zh[:30]}')
    ht_pairs.append((old_zh, new_zh))

def js_pair(old, new, tag='JS'):
    global js
    n = js.count(old)
    if n == 0:
        errors.append(f'[{tag}] MISS: {old[:40]}')
    js = js.replace(old, new)

# ============================================================
# 1. LETTERS 区域(JS 位置化整体替换 42 个值)
# ============================================================
letters_new = [
 "01","H","Hands-on","0→1 的独立操盘手。","A hands-on 0-to-1 owner.",
 "从「孙武」虚拟员工平台到东来双平台,习惯一个人把产品从规划扛到上线验收。",
 "From the Sunwu virtual-employee platform to Donglai's AI platforms, I carry products from planning all the way to launch.",
 "02","A","AI Native","用 AI 原生的方式做产品。","Build products the AI-native way.",
 "Claude Code 加 20+ 自研 Skills 加多 Agent 并行,高保真原型与方案验证一个人跑通。",
 "Claude Code, 20+ self-built Skills, and multi-agent parallel runs let me ship hi-fi prototypes and validate solutions solo.",
 "03","R","Retail","零售 AI 的实战派。","Battle-tested in retail AI.",
 "7 门店、10 类客诉、4+1 渠道,有效会话采纳率从 50% 做到 80%,在真实业务里验证 AI 价值。",
 "7 stores, 10 complaint categories, 5 channels. Session adoption rose from 50% to 80%, proven in real operations.",
 "04","R","Rigorous","用评测让 AI 可靠。","Make AI reliable through evaluation.",
 "Golden Case 评测集、数据飞轮、「训练态/使用态解耦」——效果不靠感觉,靠可复盘的证据。",
 "Golden Case sets, data flywheels, and decoupled tuning-versus-usage states. Results rest on auditable evidence, not gut feel.",
 "05","Y","Yield","让每一分 AI 投入看见产出。","Make every AI investment visible.",
 "组织级 AI 效能度量:人天系数、成本自动统计、成熟度矩阵,把 AI 从工具做成基础设施。",
 "Org-level AI efficiency metrics, man-day coefficients, automated cost tracking, and a maturity matrix turn AI from tooling into infrastructure.",
 "06","+","Evolving","方法论持续沉淀。","Methodology keeps compounding.",
 "「存用分离」「伪功能规避」等产品范式开源于 GitHub,让一套能力复制到更多业务场景。",
 "Product paradigms like storage-use separation and pseudo-feature avoidance are open-sourced on GitHub, replicating one capability across many scenarios.",
]
a, b = region_bounds(js, '[{index:"01",letter:')
seg = js[a:b]
vals = list(re.finditer(r'[:\[]"((?:[^"\\]|\\.)*)"', seg))
assert len(vals) == len(letters_new), f'letters count {len(vals)}'
letters_old_zh = []
out, last, vi = [], 0, 0
for m in vals:
    out.append(seg[last:m.start()])
    old_val = m.group(1)
    new_val = letters_new[vi]
    if vi % 7 in (3, 5):
        letters_old_zh.append((old_val, new_val))
    out.append(m.group(0)[0] + '"' + new_val + '"')
    last = m.end(); vi += 1
out.append(seg[last:])
js = js[:a] + ''.join(out) + js[b:]
ht_pairs.extend(letters_old_zh)

# ============================================================
# 2. zh/en 成对替换
# ============================================================
ZHEN = [
 ("数据训练", "Agent 产品设计", "Agent Product Design"),
 ("模型评测", "评测与质量体系", "Evaluation System"),
 ("工作流搭建", "企业知识架构", "Knowledge Architecture"),
 ("设计 & 摄影", "AI Native 工作流", "AI Native Workflow"),
 ("从数据标准、标注策略到质量闭环，把底层训练数据做得稳定、可用、可复盘。",
  "从信息架构到交互闭环,把虚拟员工、技能工坊、知识库做成能上线的企业级产品。",
  "From information architecture to interaction loops, I turn virtual employees, skill workshops, and knowledge bases into shippable enterprise products."),
 ("把评测目标拆成可执行规则与对比框架，让模型优劣不是感受，而是有依据的判断。",
  "Golden Case 评测集加数据飞轮,让模型效果不是感受,而是可复盘的证据。",
  "Golden Case sets plus data flywheels turn model quality from a feeling into auditable evidence."),
 ("把 LLM、RAG、多模态节点串成完整工作流，让 AI 能真正接进业务链路。",
  "三级知识库、存用分离、非结构化两层架构,打通「文件 → 知识 → 训练用例」的数据飞轮。",
  "Three-tier knowledge bases, storage-use separation, and a two-layer unstructured data architecture connect the file-to-knowledge-to-training flywheel."),
 ("把品牌视觉、画面审美与摄影表达整合成统一而可感知的呈现，让结果不止正确，也足够动人。",
  "Claude Code 加多 Agent 并行加自研 Skills 体系,一个人跑通原型、验证与交付全链路。",
  "Claude Code, multi-agent parallelism, and a self-built Skills system let one person run the full prototype-validate-deliver loop."),
 ("AI Agent 端到端工作流", "「孙武 Fleet」虚拟员工平台", "Sunwu Fleet Virtual Employee Platform"),
 ("多模态模型评测体系搭建", "Golden Case 评测与训练闭环", "Golden Case Evaluation Loop"),
 ("高质量标注数据工程体系", "企业知识库与数据飞轮", "Enterprise Knowledge Flywheel"),
 ("模型的垂直专项评测", "组织级 AI 效能度量", "Org-Level AI Efficiency Metrics"),
 ("多模态图文理解评测", "东来 AI 运营平台", "Donglai AI Operations Platform"),
 ("品牌视觉 × AI 工具融合", "数字审核平台多 Agent 闭环", "Multi-Agent Compliance Review"),
 ("从 0 到 1 搭建商业闭环", "风筑小屋 · 员工情绪 AI 疏导", "Fengzhu: AI Emotional Support"),
 ("基于 Dify 搭建多模态 Agent 系统,把业务流程拆解成稳定的 LLM + RAG 节点链路。以图搜图、以款搜款、历史销售联动分析——让非技术团队也能跑通完整 AI 工作流。",
  "从 0 到 1 独立操盘 AI Agent 平台:Agent 工作台、Skill 技能工坊、企业知识库三板块,交付厨电客户方太并上线,10+ 虚拟员工在线承接客服、品控、运营岗位。",
  "Independently owned an AI agent platform from 0 to 1: agent workspace, skill workshop, and enterprise knowledge base. Delivered to Fotile and launched with 10+ virtual employees handling support, QA, and operations."),
 ("从零主导 I2V 模型的空间理解与物理推演专项评测,独立完成评测方法论定义、数据集构造、评分标准制定、标注协同到对比分析的全流程,为技术选型提供量化决策依据。",
  "建立 Golden Case 评测集与测试集规范,会话一键沉淀、批量跑测;「训练态/使用态解耦」让调试噪音不污染质量分析,非技术员工也能完成训练闭环。",
  "Built Golden Case evaluation standards with one-click test-set capture and batch runs. Decoupled tuning from real usage so non-technical staff can close the training loop."),
 ("定义四层级 Caption 质量标准,搭建\"机器预标 → 人工精修 → 自动质检\"混合产线。用视觉设计背景精标 5000+ 组审美增强型种子数据,驱动模型审美维度的升级。",
  "组织、部门、个人三级知识库,「知识订阅 → 知识条目」索引层替代全文召回;非结构化数据两层架构打通「文件 → 知识 → 训练用例」,为 Skill 进化供给原料。",
  "A three-tier knowledge base with a subscription-to-entry index layer replacing full-text recall. A two-layer unstructured data architecture feeds the file-to-knowledge-to-training flywheel."),
 ("参与设计\"解题过程质量五维评测标准\"——步骤完整性、学段适配性、错因分析精准度、语言可理解性、引导启发性。为教育场景大模型的迭代提供精准数据支撑。",
  "以帅、将、兵三层重构信息架构,为工作项设置人天系数,自动统计 AI 节省的人力成本;AI 成熟度矩阵让组织看见每一分 AI 投入的产出。",
  "Rebuilt information architecture across three org levels, assigning man-day coefficients to work items and auto-tracking saved labor costs. An AI maturity matrix shows the return on every AI investment."),
 ("构建 K12 全学段拍照解题评测数据集,落地\"感知 → 理解 → 推理\"三层评测框架。针对视觉幻觉深度归因,持续驱动模型在 OCR、图文对齐、多模态推理的优化。",
  "负责受理侧 4 模块,覆盖 7 门店、10 类客诉、4+1 渠道;以语义层落地智能问数,业务方自然语言秒级取数,临时取数工单下降约 65%,有效会话采纳率 50% → 80%。",
  "Owned 4 intake modules across 7 stores, 10 complaint categories, and 5 channels. Semantic-layer self-service analytics cut ad-hoc data tickets by about 65% and raised session adoption from 50% to 80%."),
 ("服务多领域包含但不限于餐饮连锁、时尚零售、地产文旅等核心客户,深研 Ai视觉模型提示词结构,把 AI 用到概念草图、风格探索、氛围预演,再叠加人工精修完成商业交付。",
  "独立设计多子 Agent 审核架构,建立「物料 - AI 初审 - 法条引用 - 人工复审」闭环:单条审核 2-3 天 → 4h,月处理 400 → 800 条,支撑重大舆情取证,被最高法评为 2025 年度十大案例。",
  "Designed a multi-agent review architecture with a material-to-AI-review-to-legal-citation-to-human-recheck loop. Review time dropped from 2-3 days to 4 hours and monthly volume doubled to 800. Cited by the Supreme Court as a 2025 top-ten case."),
 ("拥有线下门店从 0 到 1 的完整操盘经验。从选址算账到服务交付，这段经历没有宏大叙事，褪去了纸上谈兵的滤镜。它锻炼了我的管理能力，让我习惯站在真实的业务终端看问题，沉淀出从目标倒推、统筹落地的务实能力。",
  "从季度竞赛立项到门店 MVP:AI 即时疏导加情绪分类加高危预警加员工之家联动,24/7 支撑 2 家门店 200+ 员工灰度,沉淀可复制的 EAP SOP。",
  "From a quarterly competition entry to an in-store MVP: 24/7 AI counseling with emotion classification, high-risk alerts, and staff-club escalation, piloted by 200+ employees across 2 stores with a replicable EAP SOP."),
 ("思维副驾", "产品副驾", "Product Copilot"),
 ("文案 · 杂务", "调研杂务", "Research Hand"),
 ("视觉生成", "原型画板", "Prototype Board"),
 ("图像精修", "个人操作系统", "Personal AI OS"),
 ("动态叙事", "生态扩展", "Ecosystem"),
 ("生态与扩展", "开源沉淀", "Open Source"),
 ("想清楚一件事的对象。策略、文案、架构——我和它聊,它搭骨架,我给灵魂。",
  "PRD、高保真原型、方案验证——我说目标,它搭骨架,判断和品味归我。",
  "PRDs, hi-fi prototypes, solution validation. I set the goal, it builds the skeleton, judgment and taste stay with me."),
 ("前端脏活累活全包。我描述要什么,它把代码写出来,我审稿、调方向、验收。",
  "实现层的效率杠杆。我描述需求和验收标准,它写代码,我把关方向与质量。",
  "My leverage on implementation. I describe requirements and acceptance criteria, it writes the code, I guard direction and quality."),
 ("日常文本的批量处理器。邮件、翻译、纪要、摘要——琐碎交给它,我留给更高阶判断。",
  "JD 采集、竞品调研、翻译纪要——琐碎批量交给它,判断留给自己。",
  "JD collection, competitor research, translation and notes. Batch the trivial to it, keep the judgment to myself."),
 ("概念到画面的那一跃。Moodboard、定风格、快速出素材,比真拍摄快 20 倍。",
  "高保真原型的速写板。Pencil MCP 直连 Claude,从线框到交互一气呵成。",
  "My sketchpad for hi-fi prototypes. Pencil MCP connects straight into Claude, from wireframe to interaction in one flow."),
 ("AI 生成完的素材总需要手动打磨——抠图、调色、细节修复,我和像素最近的距离。",
  "20+ 可复用 Skill 覆盖 PRD、调研、知识沉淀,可配置、可组合的个人 AI 操作系统。",
  "20+ reusable Skills covering PRDs, research, and knowledge capture, a configurable personal AI operating system."),
 ("静态无法表达的节奏交给它。首屏视频、过场、Motion,每一帧都在这里调过。",
  "把工具接进 Agent 的标准接口,知识图谱、画板、协作流都在这里打通。",
  "The standard interface wiring tools into agents, where knowledge graphs, canvases, and collaboration flows connect."),
 ("每天写 prompt、文案、代码的地方。不只是编辑器,是我的第二大脑入口。",
  "每天写 PRD、Prompt、代码的地方。不只是编辑器,是我的第二大脑入口。",
  "Where I write PRDs, prompts, and code every day. More than an editor, it is the entrance to my second brain."),
 ("我的技术武器库。插件、MCP、Skills 在这里发现和调试,让我跟得上 AI 节奏。",
  "自研 AI 产品经理知识库开源于此,Skills、MCP、方法论在这里迭代和被复用。",
  "My self-built AI PM knowledge base is open-sourced here, where Skills, MCP tooling, and methodology iterate and get reused."),
]
for old_zh, new_zh, new_en in ZHEN:
    sub_zhen(old_zh, new_zh, new_en)

# ============================================================
# 3. intros(条件串)
# ============================================================
CONDS = [
 ("ALARIC 的六个字母，是关于我的六个关键词，让你更快了解我。",
  "HARRY 的五个字母,是关于我的五个关键词;最后一张「+」,留给持续进化的自己。",
  "The five letters of HARRY are five keywords about me. The final plus sign is reserved for who I am still becoming."),
 ("从底层数据训练、模型评测、到前端视觉呈现，提供多维度的专业能力储备。",
  "从 Agent 产品设计、评测体系到企业知识架构,提供 AI 产品全链路的能力储备。",
  "From agent product design and evaluation systems to enterprise knowledge architecture, I cover the full chain of AI product work."),
 ("不止于“单点突破”，更在于系统建构。七个维度，构成了我能力的全部。",
  "不止于「单点交付」,更在于体系沉淀。七个项目,构成了我能力的全部。",
  "What matters is not isolated deliveries, but compounding systems. These seven projects define the full range of what I do."),
]
for old_zh, new_zh, new_en in CONDS:
    sub_cond(old_zh, new_zh, new_en)

# ============================================================
# 4. capabilities tags 数组(JS 位置化)
# ============================================================
cap_tags_new = [
    'tags:["Agent","IA","0→1"]',
    'tags:["GoldenCase","Rubric","Flywheel"]',
    'tags:["RAG","Knowledge","Pipeline"]',
    'tags:["ClaudeCode","Skills","MCP"]',
]
a, b = region_bounds(js, '[{number:"01",title:')
seg = js[a:b]
tag_matches = list(re.finditer(r'tags:\[(?:[^\]\\]|\\.)*\]', seg))
assert len(tag_matches) == 4, f'cap tags {len(tag_matches)}'
out, last, vi = [], 0, 0
for m in tag_matches:
    out.append(seg[last:m.start()])
    out.append(cap_tags_new[vi])
    last = m.end(); vi += 1
out.append(seg[last:])
js = js[:a] + ''.join(out) + js[b:]

# ============================================================
# 5. projects subtitle + tags(整串对)
# ============================================================
PROJ_PAIRS = [
 ("AI · Agent Architecture", "AI · Agent Platform"),
 ("AI · Data Engineering", "AI · Knowledge Architecture"),
 ("AI · Reasoning Evaluation", "AI · Org Efficiency"),
 ("AI · Multi-modal Understanding", "Retail · AI Operations"),
 ("Brand · AI-Augmented Design", "Retail · Compliance Agent"),
 ("Business · Startup", "AI · EAP Product"),
 ("Dify · Multi-modal RAG · Workflow", "Agent · Skill Workshop · 0→1"),
 ("Methodology · Benchmark · Analysis", "GoldenCase · Eval · Decoupling"),
 ("SOP · Quality Gate · Data Flywheel", "RAG · Knowledge · Flywheel"),
 ("Education AI · 5D Rubric · Error Analysis", "Metrics · Maturity · Infra"),
 ("OCR · Visual Reasoning · Hallucination", "NL2SQL · FCR · Rollout"),
 ("Brand VI · Midjourney · Hybrid Workflow", "Multi-Agent · Compliance · SLA"),
 ("Startup · Ops · Team Management", "EAP · RAG · MVP"),
]
for old, new in PROJ_PAIRS:
    js_pair(old, new, 'JS proj')
ht_pairs.extend(PROJ_PAIRS)

# ============================================================
# 6. tools name / skills / tag
# ============================================================
SKILL_PAIRS = [
 ("Strategy · Writing · Architect", "PRD · Prototype · POC"),
 ("Copy · Translate · Research", "Research · Translate · Summary"),
 ("Image · Video · Concept", "Prototype · MCP · Hi-Fi"),
 ("Retouch · Composite · Color", "SKILL.md · Workflow · Reuse"),
 ("Motion · Comp · Export", "Protocol · Tools · Graph"),
 ("Plugins · MCP · Skills", "OpenSource · PM-KB · Notes"),
]
for old, new in SKILL_PAIRS:
    js_pair(old, new, 'JS skills')
ht_pairs.extend(SKILL_PAIRS)

NAME_PAIRS = [("Claude", "Claude Code"), ("Pixverse", "Pencil"),
              ("Photoshop", "Skills 体系"), ("After Effects", "MCP")]
for old, new in NAME_PAIRS:
    pat = re.compile(r'name:"' + re.escape(old) + r'"')
    js, n = pat.subn(lambda m: 'name:"' + new + '"', js)
    if n == 0:
        errors.append(f'[JS name] MISS: {old}')
    ht_pairs.append(('>' + old + '<', '>' + new + '<'))
# tool tag: 第 6 个 Craft → Infra
a, b = region_bounds(js, '[{label:"AI PARTNERS"')
seg = js[a:b]
tag_iter = list(re.finditer(r'tag:"((?:[^"\\]|\\.)*)"', seg))
assert len(tag_iter) == 8
m = tag_iter[5]
seg = seg[:m.start()] + 'tag:"Infra"' + seg[m.end():]
js = js[:a] + seg + js[b:]

# ============================================================
# 7. contact 区域(JS 位置化)
# ============================================================
contact_new = [
 "EMAIL","待补充","link","#",
 "PHONE","待补充","copy","待补充",
 "WECHAT","待补充","copy","待补充",
 "WECHAT QR","点击获取","Click to view","modal",
 "TELEGRAM","待补充","link","#",
 "WHATSAPP","待补充","link","#",
]
a, b = region_bounds(js, '[{label:"EMAIL"')
seg = js[a:b]
vals = list(re.finditer(r'[:\[]"((?:[^"\\]|\\.)*)"', seg))
assert len(vals) == len(contact_new), f'contact {len(vals)}'
out, last, vi = [], 0, 0
for m in vals:
    out.append(seg[last:m.start()])
    out.append(m.group(0)[0] + '"' + contact_new[vi] + '"')
    last = m.end(); vi += 1
out.append(seg[last:])
js = js[:a] + ''.join(out) + js[b:]
ht_pairs.extend([("zknking1@gmail.com", "待补充"), ("+86 17701355881", "待补充"),
                 ("17701355881", "待补充"), ("NIHILISM-OO", "待补充")])

# ============================================================
# 8. 横幅/标签/标题/页脚
# ============================================================
GLOBAL_PAIRS = [
 ("DECODING" + NBSP + "AESTHETICS · AI" + NBSP + "TRAINING" + NBSP + "LEAD · ALARIC ·" + NBSP,
  "AI" + NBSP + "NATIVE · AI" + NBSP + "PRODUCT" + NBSP + "MANAGER · LI" + NBSP + "YANLONG ·" + NBSP),
 ("ALIGNING" + NBSP + "VISION · DECODING" + NBSP + "AESTHETICS · ALIGNING" + NBSP + "VISION ·" + NBSP,
  "AGENT" + NBSP + "×" + NBSP + "PRODUCT · DATA" + NBSP + "FLYWHEEL · AI" + NBSP + "NATIVE ·" + NBSP),
 ("Decoding Aesthetics", "AI Native Builder"),
 ("Aligning Vision", "Agent × Product"),
 ("AI" + NBSP + "TRAINING" + NBSP + "LEAD", "AI" + NBSP + "PRODUCT" + NBSP + "MANAGER"),
 ("AI TRAINING LEAD", "AI PRODUCT MANAGER"),
 ("◤ ALARIC // CONCEPT ◢", "◤ LIYANLONG // AI PM ◢"),
 ("ALARIC concept portfolio", "LI YANLONG · AI Product Manager Portfolio"),
 ("© ZHANG KE NING", "© LI YANLONG"),
]
for old, new in GLOBAL_PAIRS:
    if js.count(old):
        js = js.replace(old, new)
ht_pairs.extend(GLOBAL_PAIRS)

# ============================================================
# 应用 HTML 对(按 old 长度降序,防短串污染长串)
# ============================================================
ht_pairs.sort(key=lambda p: len(p[0]), reverse=True)
for old, new in ht_pairs:
    variants = [old]
    esc = htmllib.escape(old, quote=True)
    if esc != old:
        variants.append(esc)
    n = sum(ht.count(v) for v in variants)
    if n == 0:
        errors.append(f'[HTML] MISS: {old[:40]}')
    for v in variants:
        ht = ht.replace(v, new)

# ============================================================
# 9. HTML:ABOUT 区字母与单词(位置化)
# ============================================================
s0 = ht.find('ABOUT ME')
s1 = ht.find('WHAT I CAN DO')
seg = ht[s0:s1]
char_matches = list(re.finditer(r'>([A-Z])<', seg))
old_seq = [m.group(1) for m in char_matches]
unit = ['A', 'L', 'A', 'R', 'I', 'C']
assert len(old_seq) % 6 == 0 and old_seq == unit * (len(old_seq) // 6), f'letters seq: {old_seq}'
new_unit = ['H', 'A', 'R', 'R', 'Y', '+']
out, last, vi = [], 0, 0
for m in char_matches:
    out.append(seg[last:m.start()])
    out.append('>' + new_unit[vi % 6] + '<')
    last = m.end(); vi += 1
out.append(seg[last:])
seg = ''.join(out)
WORD_MAP = {"Aesthetic": "Hands-on", "Leverage": "AI Native", "Aligned": "Retail",
            "Resonance": "Rigorous", "Integrated": "Yield", "Craft": "Evolving"}
seg = re.sub(r'>(Aesthetic|Leverage|Aligned|Resonance|Integrated|Craft)<',
             lambda m: '>' + WORD_MAP[m.group(1)] + '<', seg)
ht = ht[:s0] + seg + ht[s1:]

# ============================================================
# 10. HTML:capabilities tags 节点 + tools tag
# ============================================================
TAG_MAP = {"Caption": "Agent", "Quality": "IA", "SOP": "0→1",
           "Benchmark": "GoldenCase", "Compare": "Flywheel",
           "LLM": "RAG", "RAG": "Knowledge", "Workflow": "Pipeline",
           "Visual": "ClaudeCode", "Brand": "Skills", "Photo": "MCP"}
ht = re.sub(r'>(Caption|Quality|SOP|Benchmark|Compare|LLM|RAG|Workflow|Visual|Brand|Photo)<',
            lambda m: '>' + TAG_MAP.get(m.group(1), m.group(1)) + '<', ht)
ci = ht.find('CRAFT + INFRASTRUCTURE')
seg_end = ht.find('Showcase video', ci)
seg = ht[ci:seg_end]
crafts = [m.start() for m in re.finditer(r'>Craft<', seg)]
if crafts:
    p = crafts[-1]
    seg = seg[:p] + '>Infra<' + seg[p + 7:]
    ht = ht[:ci] + seg + ht[seg_end:]
else:
    errors.append('[HTML tool tag] Craft not found')

# ============================================================
# 写回 + 残留校验
# ============================================================
open(JS_PATH, 'w', encoding='utf-8').write(js)
open(HTML_PATH, 'w', encoding='utf-8').write(ht)

print('=== 替换完成 ===')
if errors:
    print('!! 未命中项:')
    for e in errors:
        print('  ', e)
else:
    print('所有映射均命中。')

LEFTOVER = ['ALARIC', 'Alaric', 'ZHANG', 'zknking', 'NIHILISM', '17701355881',
            'Dify', '审美', 'Aesthetic', 'Leverage', 'Pixverse', 'Photoshop',
            'TRAINING' + NBSP + 'LEAD', 'TRAINING LEAD', 'K12', 'I2V']
for f, text in [('JS', js), ('HTML', ht)]:
    for probe in LEFTOVER:
        n = text.count(probe)
        if n:
            print(f'残留 [{f}] {probe}: {n}')
