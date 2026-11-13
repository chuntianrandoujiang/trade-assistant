# -*- coding: utf-8 -*-
"""90 天增长计划生成器

基于用户输入的产品、售价、毛利率、预算、阶段等信息，
生成 90 天海外市场增长计划（含单位经济、渠道选择、三阶段执行方案）。
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

# 当前语言（由 generate_growth_plan 设置，各函数据此返回中/英文）
_LANG = "zh"

# 文案（中英）
_T = {
    # 渠道
    "ch_meta": ("Meta 广告", "Meta Ads"),
    "ch_meta_r": ("适合视觉化、冲动消费型产品，快速测试素材和人群",
                  "Great for visual, impulse-buy products; fast creative & audience testing"),
    "ch_google": ("Google 搜索/购物广告", "Google Search / Shopping Ads"),
    "ch_google_r": ("用户在主动搜索解决方案，意图明确，转化率高",
                    "Users actively search for solutions; clear intent, high conversion"),
    "ch_b2b": ("冷邮件 / 开发信", "Cold Email / Outreach"),
    "ch_b2b_r": ("B2B 决策周期长，需要多次触达和关系建立",
                 "Long B2B sales cycle; needs multiple touches and relationship building"),
    "ch_tiktok": ("TikTok 广告 + 达人", "TikTok Ads + Creators"),
    "ch_tiktok_r": ("35岁以下人群、适合演示的产品，先做内容再投流",
                    "Under-35 audience, demo-friendly products; build content first, then scale ads"),
    # 预算分配
    "alloc_validate": ("验证渠道", "Validate Channel"),
    "alloc_test": ("测试素材和人群", "Test Creatives & Audiences"),
    "alloc_new": ("试新渠道", "Try New Channel"),
    # 阶段
    "ph1": ("验证阶段", "Validation"),
    "ph1_days": ("1-30 天", "Days 1-30"),
    "ph1_goal": ("跑通一个主渠道，找到赢的素材", "Get one main channel working; find winning creatives"),
    "ph1_kpi": ("找到 CPA < ${cpa} 的素材", "Find creatives with CPA < ${cpa}"),
    "ph2": ("优化阶段", "Optimization"),
    "ph2_days": ("31-60 天", "Days 31-60"),
    "ph2_goal": ("优化素材和人群，提高 ROAS", "Optimize creatives and audiences; raise ROAS"),
    "ph3": ("放量阶段", "Scaling"),
    "ph3_days": ("61-90 天", "Days 61-90"),
    "ph3_goal": ("加大预算，拓展新渠道", "Raise budget; expand to new channels"),
    "ph3_kpi": ("月销售额 > ${sales}（100 单）", "Monthly sales > ${sales} (100 orders)"),
}


def _t(key, **kw):
    """取文案并格式化"""
    pair = _T.get(key)
    if pair is None:
        return key
    s = pair[1] if _LANG == "en" else pair[0]
    if kw:
        s = s.format(**kw)
    return s

@dataclass
class GrowthPlanInput:
    """增长计划输入参数"""
    product: str
    price: float
    cost: float
    gross_margin: float  # 0-1 之间的小数
    budget_monthly: float  # 每月预算（美元）
    stage: str  # "idea" / "early_sales" / "scaling"
    business_type: str  # "impulse_b2c" / "decision_b2c" / "b2b"
    target_market: str = "美国"  # 默认美国
    shipping_cost: float = 0.0  # 运费
    tariff_cost: float = 0.0  # 关税
    payment_fee_rate: float = 0.03  # 支付手续费率（约 3%）
    return_rate: float = 0.05  # 退货预留率（默认 5%）


@dataclass
class UnitEconomics:
    """单位经济计算结果"""
    price: float
    total_cost: float
    gross_profit: float
    gross_margin: float
    breakeven_roas: float
    target_cpa: float
    target_roas: float


@dataclass
class ChannelRecommendation:
    """渠道推荐"""
    channel: str
    reason: str
    skill_ref: str


@dataclass
class PhasePlan:
    """三阶段计划"""
    phase: str
    days: str
    goal: str
    actions: List[str]
    budget_pct: float
    kpi: str


@dataclass
class GrowthPlan:
    """完整的增长计划"""
    input_params: GrowthPlanInput
    unit_economics: UnitEconomics
    channel_recommendation: ChannelRecommendation
    budget_allocation: Dict[str, float]  # {"验证": 0.7, "测试": 0.2, "新渠道": 0.1}
    phases: List[PhasePlan]
    top_3_actions: List[str]  # 本周要做的前三件事
    market_research_checklist: List[str]  # 市场调研清单
    compliance_notes: List[str]  # 合规提示

    def to_dict(self):
        return asdict(self)


def calculate_unit_economics(params: GrowthPlanInput) -> UnitEconomics:
    """计算单位经济：售价、成本、毛利、保本 ROAS、目标 CPA"""
    # 总成本 = 产品成本 + 运费 + 关税 + 支付手续费 + 退货预留
    payment_fee = params.price * params.payment_fee_rate
    return_reserve = params.price * params.return_rate
    total_cost = (
        params.cost
        + params.shipping_cost
        + params.tariff_cost
        + payment_fee
        + return_reserve
    )

    # 毛利 = 售价 - 总成本
    gross_profit = params.price - total_cost

    # 实际毛利率
    actual_margin = gross_profit / params.price if params.price > 0 else 0

    # 保本 ROAS = 1 / 毛利率
    breakeven_roas = 1 / actual_margin if actual_margin > 0 else float("inf")

    # 目标 CPA（按保本 ROAS 反推）
    target_cpa = params.price / breakeven_roas if breakeven_roas > 0 else 0

    # 目标 ROAS（建议比保本高 30%）
    target_roas = breakeven_roas * 1.3

    return UnitEconomics(
        price=params.price,
        total_cost=round(total_cost, 2),
        gross_profit=round(gross_profit, 2),
        gross_margin=round(actual_margin, 2),
        breakeven_roas=round(breakeven_roas, 2),
        target_cpa=round(target_cpa, 2),
        target_roas=round(target_roas, 2),
    )


def recommend_channel(business_type: str, product: str) -> ChannelRecommendation:
    """根据业务类型推荐主渠道"""
    if business_type == "impulse_b2c":
        return ChannelRecommendation(
            channel=_t("ch_meta"),
            reason=_t("ch_meta_r"),
            skill_ref="paid-ads (meta-ads)",
        )
    elif business_type == "decision_b2c":
        return ChannelRecommendation(
            channel=_t("ch_google"),
            reason=_t("ch_google_r"),
            skill_ref="paid-ads (google-ads)",
        )
    elif business_type == "b2b":
        return ChannelRecommendation(
            channel=_t("ch_b2b"),
            reason=_t("ch_b2b_r"),
            skill_ref="cold-outreach (cold-email-setup)",
        )
    else:
        return ChannelRecommendation(
            channel=_t("ch_tiktok"),
            reason=_t("ch_tiktok_r"),
            skill_ref="paid-ads (tiktok-ads) + ugc-video",
        )


def generate_budget_allocation(stage: str) -> Dict[str, float]:
    """根据阶段分配预算"""
    v, te, n = _t("alloc_validate"), _t("alloc_test"), _t("alloc_new")
    if stage == "idea":
        # 想法阶段：先测试，大量预算给素材和人群测试
        return {v: 0.5, te: 0.4, n: 0.1}
    elif stage == "early_sales":
        # 早期销量：验证渠道优先，但要持续测试
        return {v: 0.6, te: 0.3, n: 0.1}
    else:  # scaling
        # 放量阶段：主要预算给已验证渠道
        return {v: 0.7, te: 0.2, n: 0.1}


def generate_90day_plan(
    params: GrowthPlanInput,
    unit_econ: UnitEconomics,
    channel: ChannelRecommendation,
    budget_alloc: Dict[str, float],
) -> List[PhasePlan]:
    """生成 90 天三阶段计划"""
    monthly_budget = params.budget_monthly

    phase1_budget = monthly_budget * budget_alloc[_t("alloc_validate")]
    phase2_budget = monthly_budget * budget_alloc[_t("alloc_test")]
    phase3_budget = monthly_budget * budget_alloc[_t("alloc_new")]

    if _LANG == "en":
        phases = [
            PhasePlan(
                phase=_t("ph1"),
                days=_t("ph1_days"),
                goal=_t("ph1_goal"),
                actions=[
                    f"1. Launch 5-10 creatives on {channel.channel} for testing",
                    f"2. Set daily budget ${phase1_budget / 30:.0f}, run 7 days and review",
                    "3. Scale creatives with CPA below breakeven",
                    "4. Track pixel setup, site speed, landing page conversion",
                    "5. Log CPA, ROAS and conversion rate for each creative",
                ],
                budget_pct=budget_alloc[_t("alloc_validate")],
                kpi=_t("ph1_kpi", cpa=f"{unit_econ.target_cpa:.2f}"),
            ),
            PhasePlan(
                phase=_t("ph2"),
                days=_t("ph2_days"),
                goal=_t("ph2_goal"),
                actions=[
                    "1. Duplicate winning creatives into 3-5 variants",
                    "2. Build Lookalike and retargeting audiences",
                    "3. Optimize landing page: headline, offer, CTA",
                    "4. Test offers: free shipping, discount, bundle",
                    "5. Weekly review; pause losing ad sets",
                ],
                budget_pct=budget_alloc[_t("alloc_test")],
                kpi=f"ROAS > {unit_econ.target_roas:.1f}",
            ),
            PhasePlan(
                phase=_t("ph3"),
                days=_t("ph3_days"),
                goal=_t("ph3_goal"),
                actions=[
                    "1. Raise validated channel budget to daily cap",
                    "2. Expand winners to a second channel (e.g. TikTok)",
                    "3. Launch email automation (abandoned cart, welcome)",
                    "4. Prep Q4 creatives (if it's Sep-Oct)",
                    "5. Consider UGC creators or affiliate marketing",
                ],
                budget_pct=budget_alloc[_t("alloc_new")],
                kpi=_t("ph3_kpi", sales=f"{params.price * 100:.0f}"),
            ),
        ]
        return phases

    # 中文版
    phases = [
        PhasePlan(
            phase=_t("ph1"),
            days=_t("ph1_days"),
            goal=_t("ph1_goal"),
            actions=[
                f"1. 在 {channel.channel} 上线 5-10 个素材测试",
                f"2. 设定日预算 ${phase1_budget / 30:.0f}，跑 7 天看数据",
                "3. 找到 CPA < 保本线的素材，加大预算",
                "4. 跟踪像素安装、网站速度、落地页转化率",
                "5. 记录每条素材的 CPA、ROAS、转化率",
            ],
            budget_pct=budget_alloc[_t("alloc_validate")],
            kpi=_t("ph1_kpi", cpa=f"{unit_econ.target_cpa:.2f}"),
        ),
        PhasePlan(
            phase=_t("ph2"),
            days=_t("ph2_days"),
            goal=_t("ph2_goal"),
            actions=[
                "1. 复制赢的素材，做 3-5 个变体测试",
                "2. 建相似受众（Lookalike）和再营销受众",
                "3. 优化落地页：标题、报价、行动号召",
                "4. 测试不同报价：包邮、折扣、赠品",
                "5. 每周复盘数据，关掉亏损广告组",
            ],
            budget_pct=budget_alloc[_t("alloc_test")],
            kpi=f"ROAS > {unit_econ.target_roas:.1f}",
        ),
        PhasePlan(
            phase=_t("ph3"),
            days=_t("ph3_days"),
            goal=_t("ph3_goal"),
            actions=[
                "1. 把验证渠道的预算提到日预算上限",
                "2. 用赢的素材拓展到第二个渠道（如 TikTok）",
                "3. 启动邮件自动化（ abandoned cart、welcome序列）",
                "4. 准备 Q4 素材（如果是 9-10 月）",
                "5. 考虑招 UGC 达人或做联盟营销",
            ],
            budget_pct=budget_alloc[_t("alloc_new")],
            kpi=_t("ph3_kpi", sales=f"{params.price * 100:.0f}"),
        ),
    ]

    return phases


def generate_top_3_actions(
    params: GrowthPlanInput, unit_econ: UnitEconomics, channel: ChannelRecommendation
) -> List[str]:
    """生成本周要做的前三件事"""
    actions = []

    if params.stage == "idea":
        if _LANG == "en":
            actions = [
                f"1. Check tracking: install {channel.channel} pixel, test conversion events",
                "2. Prep landing page: clear offer, pain-point headline, CTA",
                f"3. Prep 5 creatives: 3 video + 2 image, test on {channel.channel}",
            ]
        else:
            actions = [
                f"1. 检查追踪：安装 {channel.channel} 像素，测试转化事件",
                "2. 准备落地页：清晰的报价、痛点标题、行动号召",
                f"3. 准备 5 个素材：3 个视频 + 2 个图片，测试 {channel.channel}",
            ]
    elif params.stage == "early_sales":
        if _LANG == "en":
            actions = [
                f"1. Review live ads: scale those with CPA < ${unit_econ.target_cpa:.2f}",
                "2. Duplicate winning creatives into 3 variants",
                "3. Optimize landing page CVR (target > 2%)",
            ]
        else:
            actions = [
                f"1. 复盘现有广告：CPA < ${unit_econ.target_cpa:.2f} 的加大预算",
                "2. 复制赢的素材做 3 个变体",
                "3. 优化落地页转化率（目标 > 2%）",
            ]
    else:  # scaling
        if _LANG == "en":
            actions = [
                f"1. Raise validated channel daily budget to ${params.budget_monthly * 0.7 / 30:.0f}",
                "2. Expand to a second channel (TikTok or Google)",
                "3. Launch email automation (abandoned cart series)",
            ]
        else:
            actions = [
                f"1. 把验证渠道日预算提到 ${params.budget_monthly * 0.7 / 30:.0f}",
                "2. 拓展第二个渠道（TikTok 或 Google）",
                "3. 启动邮件自动化（abandoned cart 序列）",
            ]

    return actions


def generate_market_research_checklist(product: str, target_market: str) -> List[str]:
    """生成市场调研清单"""
    if _LANG == "en":
        return [
            f"1. Search volume & trend: check '{product}' trends on Google Trends in {target_market}",
            f"2. Amazon research: check '{product}' BSR rank, review count, price range",
            f"3. Meta Ad Library: search '{product}', see how many brands run ads and for how long",
            f"4. TikTok Creative Center: view top ads related to '{product}'",
            f"5. Reddit / forums: search '{product}' for discussions and complaints",
            "6. Competitor analysis: list 5-10 competitors with price, positioning, review keywords",
            "7. Price band: where do competitors cluster; any gaps?",
            f"8. Compliance: regulations in {target_market} (FDA/FCC/CPSC)",
        ]
    return [
        f"1. 搜索量与趋势：Google Trends 查 '{product}' 在 {target_market} 的趋势",
        f"2. 亚马逊调研：查 '{product}' 的 BSR 排名、评论数、价格区间",
        f"3. Meta 广告库：搜 '{product}'，看有多少品牌在投、投多久",
        f"4. TikTok 创意中心：看 '{product}' 相关的热门广告",
        f"5. Reddit / 论坛：搜 '{product}' 的讨论和抱怨",
        f"6. 竞品分析：列出 5-10 个竞品，记录价格、定位、评论关键词",
        f"7. 价格区间：竞品集中在哪个价位，有没有空位",
        f"8. 合规检查：{target_market} 的相关法规（FDA/FCC/CPSC）",
    ]


def generate_compliance_notes(target_market: str) -> List[str]:
    """生成合规提示"""
    if _LANG == "en":
        return [
            "Electronics: must meet FCC certification (US)",
            "Children's products: must meet CPSC standards (US)",
            "Food / supplements / cosmetics: must meet FDA regulations (US)",
            "US tariffs: confirm the latest HTS code tax rate",
            "Sales tax: varies by state; register a tax ID",
        ]
    notes = [
        "电子产品：需符合 FCC 认证（美国）",
        "儿童产品：需符合 CPSC 标准（美国）",
        "食品/保健品/化妆品：需符合 FDA 规定（美国）",
        "美国关税：确认产品 HTS 编码的最新税率",
        "销售税：各州政策不同，需注册税务 ID",
    ]
    return notes


def generate_growth_plan(params: GrowthPlanInput, lang: str = "zh") -> GrowthPlan:
    """生成完整的 90 天增长计划"""
    global _LANG
    _LANG = lang

    # 1. 计算单位经济
    unit_econ = calculate_unit_economics(params)

    # 2. 推荐渠道
    channel = recommend_channel(params.business_type, params.product)

    # 3. 预算分配
    budget_alloc = generate_budget_allocation(params.stage)

    # 4. 生成 90 天计划
    phases = generate_90day_plan(params, unit_econ, channel, budget_alloc)

    # 5. 本周前三件事
    top_3 = generate_top_3_actions(params, unit_econ, channel)

    # 6. 市场调研清单
    research_checklist = generate_market_research_checklist(
        params.product, params.target_market
    )

    # 7. 合规提示
    compliance = generate_compliance_notes(params.target_market)

    return GrowthPlan(
        input_params=params,
        unit_economics=unit_econ,
        channel_recommendation=channel,
        budget_allocation=budget_alloc,
        phases=phases,
        top_3_actions=top_3,
        market_research_checklist=research_checklist,
        compliance_notes=compliance,
    )


if __name__ == "__main__":
    # 测试
    test_params = GrowthPlanInput(
        product="手机壳",
        price=15.0,
        cost=3.0,
        gross_margin=0.6,
        budget_monthly=5000.0,
        stage="idea",
        business_type="impulse_b2c",
        target_market="美国",
    )
    plan = generate_growth_plan(test_params)
    print(f"保本 ROAS: {plan.unit_economics.breakeven_roas}")
    print(f"目标 CPA: ${plan.unit_economics.target_cpa}")
    print(f"推荐渠道: {plan.channel_recommendation.channel}")
    print(f"本周前三件事:\n" + "\n".join(plan.top_3_actions))
