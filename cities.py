"""
城市数据库 - 主要贸易国家的中大型城市列表

结构: { 国家中文名: { "en": 英文名, "cities": [(中文, 英文), ...] } }
"""

from typing import Dict

COUNTRIES: Dict[str, dict] = {
    "美国": {
        "en": "United States",
        "code": "US",
        "cities": [
            ("纽约", "New York"), ("洛杉矶", "Los Angeles"),
            ("芝加哥", "Chicago"), ("休斯顿", "Houston"),
            ("凤凰城", "Phoenix"), ("费城", "Philadelphia"),
            ("圣安东尼奥", "San Antonio"), ("圣地亚哥", "San Diego"),
            ("达拉斯", "Dallas"), ("圣何塞", "San Jose"),
            ("旧金山", "San Francisco"), ("西雅图", "Seattle"),
            ("迈阿密", "Miami"), ("亚特兰大", "Atlanta"),
            ("波士顿", "Boston"), ("丹佛", "Denver"),
            # 全部 50 个州（按州名拼音/英文字母顺序）
            ("亚拉巴马", "Alabama"), ("阿拉斯加", "Alaska"),
            ("亚利桑那", "Arizona"), ("阿肯色", "Arkansas"),
            ("加利福尼亚", "California"), ("科罗拉多", "Colorado"),
            ("康涅狄格", "Connecticut"), ("特拉华", "Delaware"),
            ("佛罗里达", "Florida"), ("佐治亚", "Georgia"),
            ("夏威夷", "Hawaii"), ("爱达荷", "Idaho"),
            ("伊利诺伊", "Illinois"), ("印第安纳", "Indiana"),
            ("艾奥瓦", "Iowa"), ("堪萨斯", "Kansas"),
            ("肯塔基", "Kentucky"), ("路易斯安那", "Louisiana"),
            ("缅因", "Maine"), ("马里兰", "Maryland"),
            ("马萨诸塞", "Massachusetts"), ("密歇根", "Michigan"),
            ("明尼苏达", "Minnesota"), ("密西西比", "Mississippi"),
            ("密苏里", "Missouri"), ("蒙大拿", "Montana"),
            ("内布拉斯加", "Nebraska"), ("内华达", "Nevada"),
            ("新罕布什尔", "New Hampshire"), ("新泽西", "New Jersey"),
            ("新墨西哥", "New Mexico"), ("纽约州", "New York State"),
            ("北卡罗来纳", "North Carolina"), ("北达科他", "North Dakota"),
            ("俄亥俄", "Ohio"), ("俄克拉何马", "Oklahoma"),
            ("俄勒冈", "Oregon"), ("宾夕法尼亚", "Pennsylvania"),
            ("罗得岛", "Rhode Island"), ("南卡罗来纳", "South Carolina"),
            ("南达科他", "South Dakota"), ("田纳西", "Tennessee"),
            ("得克萨斯", "Texas"), ("犹他", "Utah"),
            ("佛蒙特", "Vermont"), ("弗吉尼亚", "Virginia"),
            ("华盛顿州", "Washington State"), ("西弗吉尼亚", "West Virginia"),
            ("威斯康星", "Wisconsin"), ("怀俄明", "Wyoming"),
        ],
    },
    "英国": {
        "en": "United Kingdom",
        "code": "GB",
        "cities": [
            ("伦敦", "London"), ("伯明翰", "Birmingham"),
            ("曼彻斯特", "Manchester"), ("爱丁堡", "Edinburgh"),
            ("利兹", "Leeds"), ("格拉斯哥", "Glasgow"),
            ("利物浦", "Liverpool"), ("布里斯托尔", "Bristol"),
            ("谢菲尔德", "Sheffield"), ("诺丁汉", "Nottingham"),
            ("纽卡斯尔", "Newcastle"), ("莱斯特", "Leicester"),
        ],
    },
    "德国": {
        "en": "Germany",
        "code": "DE",
        "cities": [
            ("柏林", "Berlin"), ("汉堡", "Hamburg"),
            ("慕尼黑", "Munich"), ("科隆", "Cologne"),
            ("法兰克福", "Frankfurt"), ("斯图加特", "Stuttgart"),
            ("杜塞尔多夫", "Düsseldorf"), ("纽伦堡", "Nuremberg"),
            ("汉诺威", "Hanover"), ("莱比锡", "Leipzig"),
            ("德累斯顿", "Dresden"), ("波恩", "Bonn"),
        ],
    },
    "法国": {
        "en": "France",
        "code": "FR",
        "cities": [
            ("巴黎", "Paris"), ("马赛", "Marseille"),
            ("里昂", "Lyon"), ("图卢兹", "Toulouse"),
            ("尼斯", "Nice"), ("南特", "Nantes"),
            ("蒙彼利埃", "Montpellier"), ("斯特拉斯堡", "Strasbourg"),
            ("波尔多", "Bordeaux"), ("里尔", "Lille"),
        ],
    },
    "日本": {
        "en": "Japan",
        "code": "JP",
        "cities": [
            ("东京", "Tokyo"), ("大阪", "Osaka"),
            ("横滨", "Yokohama"), ("名古屋", "Nagoya"),
            ("札幌", "Sapporo"), ("神户", "Kobe"),
            ("京都", "Kyoto"), ("福冈", "Fukuoka"),
            ("川崎", "Kawasaki"), ("广岛", "Hiroshima"),
        ],
    },
    "韩国": {
        "en": "South Korea",
        "code": "KR",
        "cities": [
            ("首尔", "Seoul"), ("釜山", "Busan"),
            ("仁川", "Incheon"), ("大邱", "Daegu"),
            ("大田", "Daejeon"), ("光州", "Gwangju"),
            ("蔚山", "Ulsan"), ("济州", "Jeju"),
        ],
    },
    "澳大利亚": {
        "en": "Australia",
        "code": "AU",
        "cities": [
            ("悉尼", "Sydney"), ("墨尔本", "Melbourne"),
            ("布里斯班", "Brisbane"), ("珀斯", "Perth"),
            ("阿德莱德", "Adelaide"), ("堪培拉", "Canberra"),
            ("黄金海岸", "Gold Coast"), ("达尔文", "Darwin"),
        ],
    },
    "加拿大": {
        "en": "Canada",
        "code": "CA",
        "cities": [
            ("多伦多", "Toronto"), ("蒙特利尔", "Montreal"),
            ("温哥华", "Vancouver"), ("卡尔加里", "Calgary"),
            ("渥太华", "Ottawa"), ("埃德蒙顿", "Edmonton"),
            ("魁北克城", "Quebec City"), ("温尼伯", "Winnipeg"),
        ],
    },
    "巴西": {
        "en": "Brazil",
        "code": "BR",
        "cities": [
            ("圣保罗", "São Paulo"), ("里约热内卢", "Rio de Janeiro"),
            ("巴西利亚", "Brasília"), ("萨尔瓦多", "Salvador"),
            ("福塔莱萨", "Fortaleza"), ("贝洛奥里藏特", "Belo Horizonte"),
            ("马瑙斯", "Manaus"), ("库里蒂巴", "Curitiba"),
            ("累西腓", "Recife"), ("阿雷格里港", "Porto Alegre"),
        ],
    },
    "印度": {
        "en": "India",
        "code": "IN",
        "cities": [
            ("孟买", "Mumbai"), ("德里", "Delhi"),
            ("班加罗尔", "Bangalore"), ("海得拉巴", "Hyderabad"),
            ("金奈", "Chennai"), ("加尔各答", "Kolkata"),
            ("浦那", "Pune"), ("艾哈迈达巴德", "Ahmedabad"),
            ("斋浦尔", "Jaipur"), ("勒克瑙", "Lucknow"),
        ],
    },
    "俄罗斯": {
        "en": "Russia",
        "code": "RU",
        "cities": [
            ("莫斯科", "Moscow"), ("圣彼得堡", "Saint Petersburg"),
            ("新西伯利亚", "Novosibirsk"), ("叶卡捷琳堡", "Yekaterinburg"),
            ("喀山", "Kazan"), ("下诺夫哥罗德", "Nizhny Novgorod"),
            ("符拉迪沃斯托克", "Vladivostok"), ("索契", "Sochi"),
        ],
    },
    "阿联酋": {
        "en": "United Arab Emirates",
        "code": "AE",
        "cities": [
            ("迪拜", "Dubai"), ("阿布扎比", "Abu Dhabi"),
            ("沙迦", "Sharjah"), ("阿治曼", "Ajman"),
            ("富查伊拉", "Fujairah"), ("哈伊马角", "Ras Al Khaimah"),
        ],
    },
    "沙特": {
        "en": "Saudi Arabia",
        "code": "SA",
        "cities": [
            ("利雅得", "Riyadh"), ("吉达", "Jeddah"),
            ("麦加", "Mecca"), ("达曼", "Dammam"),
            ("塔伊夫", "Taif"), ("阿西尔", "Abha"),
        ],
    },
    "泰国": {
        "en": "Thailand",
        "code": "TH",
        "cities": [
            ("曼谷", "Bangkok"), ("清迈", "Chiang Mai"),
            ("普吉", "Phuket"), ("芭堤雅", "Pattaya"),
            ("孔敬", "Khon Kaen"), ("乌隆他尼", "Udon Thani"),
        ],
    },
    "越南": {
        "en": "Vietnam",
        "code": "VN",
        "cities": [
            ("胡志明市", "Ho Chi Minh City"), ("河内", "Hanoi"),
            ("岘港", "Da Nang"), ("海防", "Hai Phong"),
            ("芽庄", "Nha Trang"), ("芹苴", "Can Tho"),
        ],
    },
    "印度尼西亚": {
        "en": "Indonesia",
        "code": "ID",
        "cities": [
            ("雅加达", "Jakarta"), ("泗水", "Surabaya"),
            ("万隆", "Bandung"), ("棉兰", "Medan"),
            ("巴厘岛", "Bali"), ("日惹", "Yogyakarta"),
        ],
    },
    "马来西亚": {
        "en": "Malaysia",
        "code": "MY",
        "cities": [
            ("吉隆坡", "Kuala Lumpur"), ("槟城", "Penang"),
            ("怡保", "Ipoh"), ("柔佛巴鲁", "Johor Bahru"),
            ("哥打京那巴鲁", "Kota Kinabalu"), ("古晋", "Kuching"),
        ],
    },
    "墨西哥": {
        "en": "Mexico",
        "code": "MX",
        "cities": [
            ("墨西哥城", "Mexico City"), ("瓜达拉哈拉", "Guadalajara"),
            ("蒙特雷", "Monterrey"), ("普埃布拉", "Puebla"),
            ("坎昆", "Cancun"), ("蒂华纳", "Tijuana"),
        ],
    },
    "南非": {
        "en": "South Africa",
        "code": "ZA",
        "cities": [
            ("约翰内斯堡", "Johannesburg"), ("开普敦", "Cape Town"),
            ("德班", "Durban"), ("比勒陀利亚", "Pretoria"),
            ("伊丽莎白港", "Port Elizabeth"), ("布隆方丹", "Bloemfontein"),
        ],
    },
    "土耳其": {
        "en": "Turkey",
        "code": "TR",
        "cities": [
            ("伊斯坦布尔", "Istanbul"), ("安卡拉", "Ankara"),
            ("伊兹密尔", "Izmir"), ("布尔萨", "Bursa"),
            ("安塔利亚", "Antalya"), ("阿达纳", "Adana"),
        ],
    },
    "尼日利亚": {
        "en": "Nigeria",
        "code": "NG",
        "cities": [
            ("拉各斯", "Lagos"), ("阿布贾", "Abuja"),
            ("卡诺", "Kano"), ("伊巴丹", "Ibadan"),
            ("哈科特港", "Port Harcourt"), ("贝宁城", "Benin City"),
        ],
    },
    "肯尼亚": {
        "en": "Kenya",
        "code": "KE",
        "cities": [
            ("内罗毕", "Nairobi"), ("蒙巴萨", "Mombasa"),
            ("基苏木", "Kisumu"), ("纳库鲁", "Nakuru"),
            ("埃尔多雷特", "Eldoret"), ("马查科斯", "Machakos"),
        ],
    },
    "埃及": {
        "en": "Egypt",
        "code": "EG",
        "cities": [
            ("开罗", "Cairo"), ("亚历山大", "Alexandria"),
            ("吉萨", "Giza"), ("卢克索", "Luxor"),
            ("苏伊士", "Suez"), ("塞得港", "Port Said"),
        ],
    },
    "意大利": {
        "en": "Italy",
        "code": "IT",
        "cities": [
            ("罗马", "Rome"), ("米兰", "Milan"),
            ("那不勒斯", "Naples"), ("都灵", "Turin"),
            ("佛罗伦萨", "Florence"), ("威尼斯", "Venice"),
            ("博洛尼亚", "Bologna"), ("热那亚", "Genoa"),
        ],
    },
    "西班牙": {
        "en": "Spain",
        "code": "ES",
        "cities": [
            ("马德里", "Madrid"), ("巴塞罗那", "Barcelona"),
            ("瓦伦西亚", "Valencia"), ("塞维利亚", "Seville"),
            ("马拉加", "Malaga"), ("毕尔巴鄂", "Bilbao"),
        ],
    },
}


def get_country_list() -> list:
    """返回支持的国家中文名列表"""
    return list(COUNTRIES.keys())


def get_cities(country_zh: str) -> list:
    """
    获取指定国家的城市列表
    :param country_zh: 国家中文名
    :return: [(中文, 英文), ...] 或 []
    """
    c = COUNTRIES.get(country_zh)
    return c["cities"] if c else []


def get_country_en(country_zh: str) -> str:
    """获取国家英文名"""
    c = COUNTRIES.get(country_zh)
    return c["en"] if c else country_zh


def get_country_code(country_zh: str) -> str:
    """获取国家代码"""
    c = COUNTRIES.get(country_zh)
    return c["code"] if c else ""
