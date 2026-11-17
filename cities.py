"""
城市数据库 - 主要贸易国家的中大型城市列表

结构: { 国家中文名: { "en": 英文名, "cities": [(中文, 英文), ...] } }
"""

from typing import Dict

COUNTRIES: Dict[str, dict] = {
    "美国": {
        "region": "北美洲",
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
        "region": "欧洲",
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
        "region": "欧洲",
        "en": "Germany",
        "code": "DE",
        "cities": [
            ("柏林", "Berlin"), ("汉堡", "Hamburg"),
            ("慕尼黑", "Munich"), ("科隆", "Cologne"),
            ("法兰克福", "Frankfurt"), ("斯图加特", "Stuttgart"),
            ("杜塞尔多夫", "Dusseldorf"), ("纽伦堡", "Nuremberg"),
            ("汉诺威", "Hanover"), ("莱比锡", "Leipzig"),
            ("德累斯顿", "Dresden"), ("多特蒙德", "Dortmund"),
        ],
    },
    "法国": {
        "region": "欧洲",
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
        "region": "亚洲",
        "en": "Japan",
        "code": "JP",
        "cities": [
            ("东京", "Tokyo"), ("大阪", "Osaka"),
            ("横滨", "Yokohama"), ("名古屋", "Nagoya"),
            ("札幌", "Sapporo"), ("神户", "Kobe"),
            ("京都", "Kyoto"), ("福冈", "Fukuoka"),
            ("川崎", "Kawasaki"), ("广岛", "Hiroshima"),
            ("千叶", "Chiba"), ("仙台", "Sendai"),
        ],
    },
    "韩国": {
        "region": "亚洲",
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
        "region": "大洋洲",
        "en": "Australia",
        "code": "AU",
        "cities": [
            ("悉尼", "Sydney"), ("墨尔本", "Melbourne"),
            ("布里斯班", "Brisbane"), ("珀斯", "Perth"),
            ("阿德莱德", "Adelaide"), ("堪培拉", "Canberra"),
            ("黄金海岸", "Gold Coast"), ("达尔文", "Darwin"),
            ("凯恩斯", "Cairns"), ("汤斯维尔", "Townsville"),
        ],
    },
    "加拿大": {
        "region": "北美洲",
        "en": "Canada",
        "code": "CA",
        "cities": [
            ("多伦多", "Toronto"), ("蒙特利尔", "Montreal"),
            ("温哥华", "Vancouver"), ("卡尔加里", "Calgary"),
            ("渥太华", "Ottawa"), ("埃德蒙顿", "Edmonton"),
            ("魁北克城", "Quebec City"), ("温尼伯", "Winnipeg"),
            ("哈利法克斯", "Halifax"),
        ],
    },
    "巴西": {
        "region": "南美洲",
        "en": "Brazil",
        "code": "BR",
        "cities": [
            ("圣保罗", "Sao Paulo"), ("里约热内卢", "Rio de Janeiro"),
            ("巴西利亚", "Brasilia"), ("萨尔瓦多", "Salvador"),
            ("福塔莱萨", "Fortaleza"), ("贝洛奥里藏特", "Belo Horizonte"),
            ("马瑙斯", "Manaus"), ("库里蒂巴", "Curitiba"),
            ("累西腓", "Recife"), ("阿雷格里港", "Porto Alegre"),
            ("戈亚尼亚", "Goiania"),
        ],
    },
    "印度": {
        "region": "亚洲",
        "en": "India",
        "code": "IN",
        "cities": [
            ("孟买", "Mumbai"), ("德里", "Delhi"),
            ("班加罗尔", "Bangalore"), ("海得拉巴", "Hyderabad"),
            ("金奈", "Chennai"), ("加尔各答", "Kolkata"),
            ("浦那", "Pune"), ("艾哈迈达巴德", "Ahmedabad"),
            ("斋浦尔", "Jaipur"), ("勒克瑙", "Lucknow"),
            ("特里凡得琅", "Thiruvananthapuram"), ("维沙卡帕特南", "Visakhapatnam"),
            ("科钦", "Kochi"),
        ],
    },
    "俄罗斯": {
        "region": "欧洲",
        "en": "Russia",
        "code": "RU",
        "cities": [
            ("莫斯科", "Moscow"), ("圣彼得堡", "Saint Petersburg"),
            ("新西伯利亚", "Novosibirsk"), ("叶卡捷琳堡", "Yekaterinburg"),
            ("喀山", "Kazan"), ("下诺夫哥罗德", "Nizhny Novgorod"),
            ("符拉迪沃斯托克", "Vladivostok"), ("索契", "Sochi"),
            ("罗斯托夫", "Rostov-on-Don"), ("彼尔姆", "Perm"),
            ("萨马拉", "Samara"), ("伊尔库茨克", "Irkutsk"),
        ],
    },
    "阿联酋": {
        "region": "中东",
        "en": "United Arab Emirates",
        "code": "AE",
        "cities": [
            ("迪拜", "Dubai"), ("阿布扎比", "Abu Dhabi"),
            ("沙迦", "Sharjah"), ("阿治曼", "Ajman"),
            ("富查伊拉", "Fujairah"), ("哈伊马角", "Ras Al Khaimah"),
        ],
    },
    "沙特": {
        "region": "中东",
        "en": "Saudi Arabia",
        "code": "SA",
        "cities": [
            ("利雅得", "Riyadh"), ("吉达", "Jeddah"),
            ("麦加", "Mecca"), ("达曼", "Dammam"),
            ("塔伊夫", "Taif"), ("阿西尔", "Abha"),
        ],
    },
    "泰国": {
        "region": "亚洲",
        "en": "Thailand",
        "code": "TH",
        "cities": [
            ("曼谷", "Bangkok"), ("清迈", "Chiang Mai"),
            ("普吉", "Phuket"), ("芭堤雅", "Pattaya"),
            ("孔敬", "Khon Kaen"), ("乌隆他尼", "Udon Thani"),
            ("大城府", "Ayutthaya"), ("春蓬", "Chumphon"),
            ("那空沙旺", "Nakhon Si Thammarat"),
        ],
    },
    "越南": {
        "region": "亚洲",
        "en": "Vietnam",
        "code": "VN",
        "cities": [
            ("胡志明市", "Ho Chi Minh City"), ("河内", "Hanoi"),
            ("岘港", "Da Nang"), ("海防", "Hai Phong"),
            ("芽庄", "Nha Trang"), ("芹苴", "Can Tho"),
            ("顺化", "Hue"), ("邦来", "Binh Duong"),
        ],
    },
    "印度尼西亚": {
        "region": "亚洲",
        "en": "Indonesia",
        "code": "ID",
        "cities": [
            ("雅加达", "Jakarta"), ("泗水", "Surabaya"),
            ("万隆", "Bandung"), ("棉兰", "Medan"),
            ("巴厘岛", "Bali"), ("日惹", "Yogyakarta"),
            ("巴淡岛", "Batam"), ("巴厘巴板", "Balikpapan"),
        ],
    },
    "马来西亚": {
        "region": "亚洲",
        "en": "Malaysia",
        "code": "MY",
        "cities": [
            ("吉隆坡", "Kuala Lumpur"), ("槟城", "Penang"),
            ("怡保", "Ipoh"), ("柔佛巴鲁", "Johor Bahru"),
            ("哥打京那巴鲁", "Kota Kinabalu"), ("古晋", "Kuching"),
        ],
    },
    "墨西哥": {
        "region": "北美洲",
        "en": "Mexico",
        "code": "MX",
        "cities": [
            ("墨西哥城", "Mexico City"), ("瓜达拉哈拉", "Guadalajara"),
            ("蒙特雷", "Monterrey"), ("普埃布拉", "Puebla"),
            ("坎昆", "Cancun"), ("蒂华纳", "Tijuana"),
            ("托卢卡", "Toluca"), ("梅里达", "Merida"),
        ],
    },
    "南非": {
        "region": "非洲",
        "en": "South Africa",
        "code": "ZA",
        "cities": [
            ("约翰内斯堡", "Johannesburg"), ("开普敦", "Cape Town"),
            ("德班", "Durban"), ("比勒陀利亚", "Pretoria"),
            ("伊丽莎白港", "Port Elizabeth"), ("布隆方丹", "Bloemfontein"),
        ],
    },
    "土耳其": {
        "region": "欧洲",
        "en": "Turkey",
        "code": "TR",
        "cities": [
            ("伊斯坦布尔", "Istanbul"), ("安卡拉", "Ankara"),
            ("伊兹密尔", "Izmir"), ("布尔萨", "Bursa"),
            ("安塔利亚", "Antalya"), ("阿达纳", "Adana"),
            ("加济安泰普", "Gaziantep"), ("特拉布宗", "Trabzon"),
        ],
    },
    "尼日利亚": {
        "region": "非洲",
        "en": "Nigeria",
        "code": "NG",
        "cities": [
            ("拉各斯", "Lagos"), ("阿布贾", "Abuja"),
            ("卡诺", "Kano"), ("伊巴丹", "Ibadan"),
            ("哈科特港", "Port Harcourt"), ("贝宁城", "Benin City"),
        ],
    },
    "肯尼亚": {
        "region": "非洲",
        "en": "Kenya",
        "code": "KE",
        "cities": [
            ("内罗毕", "Nairobi"), ("蒙巴萨", "Mombasa"),
            ("基苏木", "Kisumu"), ("纳库鲁", "Nakuru"),
            ("埃尔多雷特", "Eldoret"), ("马查科斯", "Machakos"),
        ],
    },
    "埃及": {
        "region": "非洲",
        "en": "Egypt",
        "code": "EG",
        "cities": [
            ("开罗", "Cairo"), ("亚历山大", "Alexandria"),
            ("吉萨", "Giza"), ("卢克索", "Luxor"),
            ("苏伊士", "Suez"), ("塞得港", "Port Said"),
            ("阿斯旺", "Aswan"),
        ],
    },
    "意大利": {
        "region": "欧洲",
        "en": "Italy",
        "code": "IT",
        "cities": [
            ("罗马", "Rome"), ("米兰", "Milan"),
            ("那不勒斯", "Naples"), ("都灵", "Turin"),
            ("佛罗伦萨", "Florence"), ("威尼斯", "Venice"),
            ("博洛尼亚", "Bologna"), ("热那亚", "Genoa"),
            ("巴勒莫", "Palermo"), ("巴里", "Bari"),
        ],
    },
    "西班牙": {
        "region": "欧洲",
        "en": "Spain",
        "code": "ES",
        "cities": [
            ("马德里", "Madrid"), ("巴塞罗那", "Barcelona"),
            ("瓦伦西亚", "Valencia"), ("塞维利亚", "Seville"),
            ("马拉加", "Malaga"), ("毕尔巴鄂", "Bilbao"),
            ("阿利坎特", "Alicante"), ("萨拉戈萨", "Zaragoza"),
        ],
    },
    "中国": {
        "region": "亚洲",
        "en": "China",
        "code": "CN",
        "cities": [
            ("北京", "Beijing"), ("上海", "Shanghai"),
            ("广州", "Guangzhou"), ("深圳", "Shenzhen"),
            ("成都", "Chengdu"), ("杭州", "Hangzhou"),
            ("武汉", "Wuhan"), ("南京", "Nanjing"),
            ("苏州", "Suzhou"), ("西安", "Xi'an"),
            ("重庆", "Chongqing"), ("青岛", "Qingdao"),
            ("天津", "Tianjin"), ("大连", "Dalian"),
            ("厦门", "Xiamen"), ("佛山", "Foshan"),
            ("东莞", "Dongguan"), ("长沙", "Changsha"),
        ],
    },

    "新加坡": {
        "region": "亚洲",
        "en": "Singapore",
        "code": "SG",
        "cities": [
            ("新加坡", "Singapore"),
        ],
    },

    "菲律宾": {
        "region": "亚洲",
        "en": "Philippines",
        "code": "PH",
        "cities": [
            ("马尼拉", "Manila"), ("宿务", "Cebu"),
            ("达沃", "Davao"), ("奎松城", "Quezon City"),
        ],
    },

    "巴基斯坦": {
        "region": "亚洲",
        "en": "Pakistan",
        "code": "PK",
        "cities": [
            ("卡拉奇", "Karachi"), ("拉合尔", "Lahore"),
            ("伊斯兰堡", "Islamabad"), ("费萨拉巴德", "Faisalabad"),
        ],
    },

    "孟加拉国": {
        "region": "亚洲",
        "en": "Bangladesh",
        "code": "BD",
        "cities": [
            ("达卡", "Dhaka"), ("吉大港", "Chittagong"),
            ("库尔纳", "Khulna"), ("锡尔赫特", "Sylhet"),
        ],
    },

    "斯里兰卡": {
        "region": "亚洲",
        "en": "Sri Lanka",
        "code": "LK",
        "cities": [
            ("科伦坡", "Colombo"), ("康提", "Kandy"),
            ("加勒", "Galle"), ("尼甘布", "Negombo"),
        ],
    },

    "缅甸": {
        "region": "亚洲",
        "en": "Myanmar",
        "code": "MM",
        "cities": [
            ("仰光", "Yangon"), ("曼德勒", "Mandalay"),
            ("内比都", "Naypyitaw"),
        ],
    },

    "柬埔寨": {
        "region": "亚洲",
        "en": "Cambodia",
        "code": "KH",
        "cities": [
            ("金边", "Phnom Penh"), ("暹粒", "Siem Reap"),
            ("西哈努克港", "Sihanoukville"),
        ],
    },

    "老挝": {
        "region": "亚洲",
        "en": "Laos",
        "code": "LA",
        "cities": [
            ("万象", "Vientiane"), ("琅勃拉邦", "Luang Prabang"),
        ],
    },

    "蒙古": {
        "region": "亚洲",
        "en": "Mongolia",
        "code": "MN",
        "cities": [
            ("乌兰巴托", "Ulaanbaatar"),
        ],
    },

    "以色列": {
        "region": "亚洲",
        "en": "Israel",
        "code": "IL",
        "cities": [
            ("特拉维夫", "Tel Aviv"), ("耶路撒冷", "Jerusalem"),
            ("海法", "Haifa"), ("贝谢瓦", "Beersheba"),
        ],
    },

    "伊朗": {
        "region": "亚洲",
        "en": "Iran",
        "code": "IR",
        "cities": [
            ("德黑兰", "Tehran"), ("伊斯法罕", "Isfahan"),
            ("设拉子", "Shiraz"), ("马什哈德", "Mashhad"),
        ],
    },

    "伊拉克": {
        "region": "亚洲",
        "en": "Iraq",
        "code": "IQ",
        "cities": [
            ("巴格达", "Baghdad"), ("巴士拉", "Basra"),
            ("埃尔比勒", "Erbil"), ("摩苏尔", "Mosul"),
        ],
    },

    "约旦": {
        "region": "亚洲",
        "en": "Jordan",
        "code": "JO",
        "cities": [
            ("安曼", "Amman"), ("扎卡", "Zarka"),
        ],
    },

    "黎巴嫩": {
        "region": "亚洲",
        "en": "Lebanon",
        "code": "LB",
        "cities": [
            ("贝鲁特", "Beirut"), ("的黎波里", "Tripoli"),
        ],
    },

    "阿曼": {
        "region": "亚洲",
        "en": "Oman",
        "code": "OM",
        "cities": [
            ("马斯喀特", "Muscat"), ("萨拉拉", "Salalah"),
            ("苏尔", "Sur"),
        ],
    },

    "卡塔尔": {
        "region": "亚洲",
        "en": "Qatar",
        "code": "QA",
        "cities": [
            ("多哈", "Doha"),
        ],
    },

    "巴林": {
        "region": "亚洲",
        "en": "Bahrain",
        "code": "BH",
        "cities": [
            ("麦纳麦", "Manama"),
        ],
    },

    "科威特": {
        "region": "亚洲",
        "en": "Kuwait",
        "code": "KW",
        "cities": [
            ("科威特城", "Kuwait City"),
        ],
    },

    "乌兹别克斯坦": {
        "region": "亚洲",
        "en": "Uzbekistan",
        "code": "UZ",
        "cities": [
            ("塔什干", "Tashkent"), ("撒马尔罕", "Samarkand"),
            ("布哈拉", "Bukhara"),
        ],
    },

    "也门": {
        "region": "亚洲",
        "en": "Yemen",
        "code": "YE",
        "cities": [
            ("萨那", "Sanaa"), ("亚丁", "Aden"),
        ],
    },

    "荷兰": {
        "region": "欧洲",
        "en": "Netherlands",
        "code": "NL",
        "cities": [
            ("阿姆斯特丹", "Amsterdam"), ("鹿特丹", "Rotterdam"),
            ("海牙", "The Hague"), ("乌得勒支", "Utrecht"),
            ("埃因霍温", "Eindhoven"),
        ],
    },

    "比利时": {
        "region": "欧洲",
        "en": "Belgium",
        "code": "BE",
        "cities": [
            ("布鲁塞尔", "Brussels"), ("安特卫普", "Antwerp"),
            ("根特", "Ghent"), ("列日", "Liege"),
        ],
    },

    "瑞士": {
        "region": "欧洲",
        "en": "Switzerland",
        "code": "CH",
        "cities": [
            ("苏黎世", "Zurich"), ("日内瓦", "Geneva"),
            ("伯尔尼", "Bern"), ("巴塞尔", "Basel"),
        ],
    },

    "奥地利": {
        "region": "欧洲",
        "en": "Austria",
        "code": "AT",
        "cities": [
            ("维也纳", "Vienna"), ("格拉茨", "Graz"),
            ("林茨", "Linz"), ("萨尔茨堡", "Salzburg"),
        ],
    },

    "瑞典": {
        "region": "欧洲",
        "en": "Sweden",
        "code": "SE",
        "cities": [
            ("斯德哥尔摩", "Stockholm"), ("哥德堡", "Gothenburg"),
            ("马尔默", "Malmo"), ("于普萨拉", "Uppsala"),
        ],
    },

    "挪威": {
        "region": "欧洲",
        "en": "Norway",
        "code": "NO",
        "cities": [
            ("奥斯陆", "Oslo"), ("卑尔根", "Bergen"),
            ("特隆赫姆", "Trondheim"), ("斯塔万格", "Stavanger"),
        ],
    },

    "丹麦": {
        "region": "欧洲",
        "en": "Denmark",
        "code": "DK",
        "cities": [
            ("哥本哈根", "Copenhagen"), ("奥胡斯", "Aarhus"),
            ("欧登塞", "Odense"),
        ],
    },

    "芬兰": {
        "region": "欧洲",
        "en": "Finland",
        "code": "FI",
        "cities": [
            ("赫尔辛基", "Helsinki"), ("埃斯波", "Espoo"),
            ("坦佩雷", "Tampere"), ("图尔库", "Turku"),
        ],
    },

    "波兰": {
        "region": "欧洲",
        "en": "Poland",
        "code": "PL",
        "cities": [
            ("华沙", "Warsaw"), ("克拉科夫", "Krakow"),
            ("弗罗茨瓦夫", "Wroclaw"), ("格但斯克", "Gdansk"),
        ],
    },

    "葡萄牙": {
        "region": "欧洲",
        "en": "Portugal",
        "code": "PT",
        "cities": [
            ("里斯本", "Lisbon"), ("波尔图", "Porto"),
            ("布拉加", "Braga"), ("法鲁", "Faro"),
        ],
    },

    "爱尔兰": {
        "region": "欧洲",
        "en": "Ireland",
        "code": "IE",
        "cities": [
            ("都柏林", "Dublin"), ("科克", "Cork"),
            ("戈尔韦", "Galway"),
        ],
    },

    "希腊": {
        "region": "欧洲",
        "en": "Greece",
        "code": "GR",
        "cities": [
            ("雅典", "Athens"), ("塞萨洛尼基", "Thessaloniki"),
            ("帕特雷", "Patras"), ("伊拉克利翁", "Heraklion"),
        ],
    },

    "捷克": {
        "region": "欧洲",
        "en": "Czechia",
        "code": "CZ",
        "cities": [
            ("布拉格", "Prague"), ("布尔诺", "Brno"),
            ("奥斯特拉瓦", "Ostrava"),
        ],
    },

    "匈牙利": {
        "region": "欧洲",
        "en": "Hungary",
        "code": "HU",
        "cities": [
            ("布达佩斯", "Budapest"), ("德布勒森", "Debrecen"),
            ("塞格德", "Szeged"),
        ],
    },

    "罗马尼亚": {
        "region": "欧洲",
        "en": "Romania",
        "code": "RO",
        "cities": [
            ("布加勒斯特", "Bucharest"), ("克卢日", "Cluj"),
            ("蒂米索瓦拉", "Timisoara"), ("雅西", "Iasi"),
        ],
    },

    "保加利亚": {
        "region": "欧洲",
        "en": "Bulgaria",
        "code": "BG",
        "cities": [
            ("索非亚", "Sofia"), ("普罗夫迪夫", "Plovdiv"),
            ("瓦尔纳", "Varna"),
        ],
    },

    "克罗地亚": {
        "region": "欧洲",
        "en": "Croatia",
        "code": "HR",
        "cities": [
            ("萨格勒布", "Zagreb"), ("斯普利特", "Split"),
            ("杜布罗夫尼克", "Dubrovnik"),
        ],
    },

    "斯洛伐克": {
        "region": "欧洲",
        "en": "Slovakia",
        "code": "SK",
        "cities": [
            ("布拉迪斯拉发", "Bratislava"), ("科希策", "Kosice"),
        ],
    },

    "斯洛文尼亚": {
        "region": "欧洲",
        "en": "Slovenia",
        "code": "SI",
        "cities": [
            ("卢布尔雅那", "Ljubljana"), ("马里博尔", "Maribor"),
        ],
    },

    "乌克兰": {
        "region": "欧洲",
        "en": "Ukraine",
        "code": "UA",
        "cities": [
            ("基辅", "Kyiv"), ("哈尔科夫", "Kharkiv"),
            ("利沃夫", "Lviv"), ("敖德萨", "Odesa"),
        ],
    },

    "塞尔维亚": {
        "region": "欧洲",
        "en": "Serbia",
        "code": "RS",
        "cities": [
            ("贝尔格莱德", "Belgrade"), ("诺维萨德", "Novi Sad"),
            ("尼什", "Nis"),
        ],
    },

    "波黑": {
        "region": "欧洲",
        "en": "Bosnia and Herzegovina",
        "code": "BA",
        "cities": [
            ("萨拉热窝", "Sarajevo"),
        ],
    },

    "爱沙尼亚": {
        "region": "欧洲",
        "en": "Estonia",
        "code": "EE",
        "cities": [
            ("塔林", "Tallinn"),
        ],
    },

    "拉脱维亚": {
        "region": "欧洲",
        "en": "Latvia",
        "code": "LV",
        "cities": [
            ("里加", "Riga"),
        ],
    },

    "立陶宛": {
        "region": "欧洲",
        "en": "Lithuania",
        "code": "LT",
        "cities": [
            ("维尔纽斯", "Vilnius"), ("考纳斯", "Kaunas"),
        ],
    },

    "冰岛": {
        "region": "欧洲",
        "en": "Iceland",
        "code": "IS",
        "cities": [
            ("雷克雅未克", "Reykjavik"),
        ],
    },

    "卢森堡": {
        "region": "欧洲",
        "en": "Luxembourg",
        "code": "LU",
        "cities": [
            ("卢森堡城", "Luxembourg City"),
        ],
    },

    "马耳他": {
        "region": "欧洲",
        "en": "Malta",
        "code": "MT",
        "cities": [
            ("瓦莱塔", "Valletta"), ("斯利马", "Sliema"),
        ],
    },

    "巴拿马": {
        "region": "北美洲",
        "en": "Panama",
        "code": "PA",
        "cities": [
            ("巴拿马城", "Panama City"),
        ],
    },

    "哥斯达黎加": {
        "region": "北美洲",
        "en": "Costa Rica",
        "code": "CR",
        "cities": [
            ("圣何塞", "San Jose"), ("阿拉胡埃拉", "Alajuela"),
        ],
    },

    "危地马拉": {
        "region": "北美洲",
        "en": "Guatemala",
        "code": "GT",
        "cities": [
            ("危地马拉城", "Guatemala City"), ("安提瓜", "Antigua"),
        ],
    },

    "洪都拉斯": {
        "region": "北美洲",
        "en": "Honduras",
        "code": "HN",
        "cities": [
            ("特古西加尔巴", "Tegucigalpa"), ("圣佩德罗苏拉", "San Pedro Sula"),
        ],
    },

    "多米尼加": {
        "region": "北美洲",
        "en": "Dominican Republic",
        "code": "DO",
        "cities": [
            ("圣多明各", "Santo Domingo"),
        ],
    },

    "古巴": {
        "region": "北美洲",
        "en": "Cuba",
        "code": "CU",
        "cities": [
            ("哈瓦那", "Havana"), ("关塔那摩", "Guantanamo"),
            ("圣地亚哥德古巴", "Santiago de Cuba"),
        ],
    },

    "牙买加": {
        "region": "北美洲",
        "en": "Jamaica",
        "code": "JM",
        "cities": [
            ("金斯顿", "Kingston"), ("蒙特哥贝", "Montego Bay"),
        ],
    },

    "特立尼达和多巴哥": {
        "region": "北美洲",
        "en": "Trinidad and Tobago",
        "code": "TT",
        "cities": [
            ("西班牙港", "Port of Spain"), ("阿瑞玛", "Arima"),
        ],
    },

    "伯利兹": {
        "region": "北美洲",
        "en": "Belize",
        "code": "BZ",
        "cities": [
            ("贝尔莫潘", "Belmopan"), ("圣伊格纳西奥", "San Ignacio"),
        ],
    },

    "阿根廷": {
        "region": "南美洲",
        "en": "Argentina",
        "code": "AR",
        "cities": [
            ("布宜诺斯艾利斯", "Buenos Aires"), ("科尔多瓦", "Cordoba"),
            ("罗萨里奥", "Rosario"), ("门多萨", "Mendoza"),
        ],
    },

    "智利": {
        "region": "南美洲",
        "en": "Chile",
        "code": "CL",
        "cities": [
            ("圣地亚哥", "Santiago"), ("瓦尔帕莱索", "Valparaiso"),
            ("康塞普西翁", "Concepcion"), ("安托法加斯塔", "Antofagasta"),
        ],
    },

    "哥伦比亚": {
        "region": "南美洲",
        "en": "Colombia",
        "code": "CO",
        "cities": [
            ("波哥大", "Bogota"), ("麦德林", "Medellin"),
            ("卡利", "Cali"),
        ],
    },

    "秘鲁": {
        "region": "南美洲",
        "en": "Peru",
        "code": "PE",
        "cities": [
            ("利马", "Lima"), ("阿雷基帕", "Arequipa"),
            ("库斯科", "Cusco"), ("特鲁希略", "Trujillo"),
        ],
    },

    "厄瓜多尔": {
        "region": "南美洲",
        "en": "Ecuador",
        "code": "EC",
        "cities": [
            ("基多", "Quito"), ("瓜亚基尔", "Guayaquil"),
            ("马纳比", "Manta"),
        ],
    },

    "委内瑞拉": {
        "region": "南美洲",
        "en": "Venezuela",
        "code": "VE",
        "cities": [
            ("加拉加斯", "Caracas"), ("马拉开波", "Maracaibo"),
            ("瓦伦西亚", "Valencia"),
        ],
    },

    "玻利维亚": {
        "region": "南美洲",
        "en": "Bolivia",
        "code": "BO",
        "cities": [
            ("拉巴斯", "La Paz"), ("圣克鲁斯", "Santa Cruz"),
            ("科恰班巴", "Cochabamba"),
        ],
    },

    "乌拉圭": {
        "region": "南美洲",
        "en": "Uruguay",
        "code": "UY",
        "cities": [
            ("蒙得维的亚", "Montevideo"), ("马尔多纳多", "Maldonado"),
        ],
    },

    "巴拉圭": {
        "region": "南美洲",
        "en": "Paraguay",
        "code": "PY",
        "cities": [
            ("亚松森", "Asuncion"), ("卢克", "Luque"),
        ],
    },

    "苏里南": {
        "region": "南美洲",
        "en": "Suriname",
        "code": "SR",
        "cities": [
            ("帕拉马里博", "Paramaribo"),
        ],
    },

    "圭亚那": {
        "region": "南美洲",
        "en": "Guyana",
        "code": "GY",
        "cities": [
            ("乔治敦", "Georgetown"),
        ],
    },

    "摩洛哥": {
        "region": "非洲",
        "en": "Morocco",
        "code": "MA",
        "cities": [
            ("卡萨布兰卡", "Casablanca"), ("拉巴特", "Rabat"),
            ("马拉喀什", "Marrakesh"), ("丹吉尔", "Tangier"),
        ],
    },

    "阿尔及利亚": {
        "region": "非洲",
        "en": "Algeria",
        "code": "DZ",
        "cities": [
            ("阿尔及尔", "Algiers"), ("奥兰", "Oran"),
            ("君士坦丁", "Constantine"),
        ],
    },

    "突尼斯": {
        "region": "非洲",
        "en": "Tunisia",
        "code": "TN",
        "cities": [
            ("突尼斯城", "Tunis"), ("斯法克斯", "Sfax"),
            ("苏塞", "Sousse"),
        ],
    },

    "埃塞俄比亚": {
        "region": "非洲",
        "en": "Ethiopia",
        "code": "ET",
        "cities": [
            ("亚的斯亚贝巴", "Addis Ababa"), ("迪雷达瓦", "Dire Dawa"),
            ("巴赫尔达尔", "Bahir Dar"),
        ],
    },

    "坦桑尼亚": {
        "region": "非洲",
        "en": "Tanzania",
        "code": "TZ",
        "cities": [
            ("达累斯萨拉姆", "Dar es Salaam"), ("阿鲁沙", "Arusha"),
            ("姆万扎", "Mwanza"), ("桑给巴尔", "Zanzibar"),
        ],
    },

    "加纳": {
        "region": "非洲",
        "en": "Ghana",
        "code": "GH",
        "cities": [
            ("阿克拉", "Accra"), ("库马西", "Kumasi"),
            ("塔科拉迪", "Takoradi"),
        ],
    },

    "塞内加尔": {
        "region": "非洲",
        "en": "Senegal",
        "code": "SN",
        "cities": [
            ("达喀尔", "Dakar"), ("蒂耶斯", "Thies"),
            ("圣路易", "Saint-Louis"),
        ],
    },

    "莫桑比克": {
        "region": "非洲",
        "en": "Mozambique",
        "code": "MZ",
        "cities": [
            ("马普托", "Maputo"), ("贝拉", "Beira"),
        ],
    },

    "喀麦隆": {
        "region": "非洲",
        "en": "Cameroon",
        "code": "CM",
        "cities": [
            ("杜阿拉", "Douala"), ("雅温得", "Yaounde"),
        ],
    },

    "津巴布韦": {
        "region": "非洲",
        "en": "Zimbabwe",
        "code": "ZW",
        "cities": [
            ("哈拉雷", "Harare"), ("布拉瓦约", "Bulawayo"),
        ],
    },

    "乌干达": {
        "region": "非洲",
        "en": "Uganda",
        "code": "UG",
        "cities": [
            ("坎帕拉", "Kampala"), ("金贾", "Jinja"),
        ],
    },

    "利比亚": {
        "region": "非洲",
        "en": "Libya",
        "code": "LY",
        "cities": [
            ("的黎波里", "Tripoli"), ("班加西", "Benghazi"),
        ],
    },

    "科特迪瓦": {
        "region": "非洲",
        "en": "Ivory Coast",
        "code": "CI",
        "cities": [
            ("阿比让", "Abidjan"), ("布阿基", "Bouake"),
        ],
    },

    "毛里求斯": {
        "region": "非洲",
        "en": "Mauritius",
        "code": "MU",
        "cities": [
            ("路易港", "Port Louis"),
        ],
    },

    "新西兰": {
        "region": "大洋洲",
        "en": "New Zealand",
        "code": "NZ",
        "cities": [
            ("奥克兰", "Auckland"), ("惠灵顿", "Wellington"),
            ("基督城", "Christchurch"), ("皇后镇", "Queenstown"),
        ],
    },
}


def get_country_list() -> list:
    """返回支持的国家中文名列表"""
    return list(COUNTRIES.keys())


# 大陆/区域 → 国家中文名（按 COUNTRIES 里的 region 字段动态生成，避免手工维护两份）
def get_regions() -> list:
    """返回支持的大陆/区域中文名列表（固定顺序）"""
    order = ["亚洲", "欧洲", "北美洲", "南美洲", "非洲", "中东", "大洋洲"]
    present = {c.get("region") for c in COUNTRIES.values()}
    return [r for r in order if r in present]


def get_countries_by_region(region_zh: str) -> list:
    """返回某大陆下支持的国家中文名列表（按 COUNTRIES 顺序）"""
    return [k for k, v in COUNTRIES.items() if v.get("region") == region_zh]


REGION_EN = {
    "亚洲": "Asia", "欧洲": "Europe", "北美洲": "North America",
    "南美洲": "South America", "非洲": "Africa",
    "中东": "Middle East", "大洋洲": "Oceania",
}


def get_region_en(region_zh: str) -> str:
    return REGION_EN.get(region_zh, region_zh)


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

# ===== 主要城市扩充库（同名国家整体覆盖基础列表）=====
from cities_extra import EXTRA_CITIES

for _c, _cities in EXTRA_CITIES.items():
    if _c in COUNTRIES:
        COUNTRIES[_c]["cities"] = _cities
