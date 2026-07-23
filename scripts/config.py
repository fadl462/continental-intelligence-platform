"""Shared config for the briefing generator. Keep in sync with the
CONTINENTS / INDICATORS objects in index.html if you add countries."""

# iso3: (name, continent)
COUNTRIES = {
    "GHA": ("Ghana", "Africa"), "NGA": ("Nigeria", "Africa"), "KEN": ("Kenya", "Africa"),
    "ZAF": ("South Africa", "Africa"), "EGY": ("Egypt", "Africa"), "ETH": ("Ethiopia", "Africa"),
    "CIV": ("Côte d'Ivoire", "Africa"), "MAR": ("Morocco", "Africa"),
    "DEU": ("Germany", "Europe"), "GBR": ("United Kingdom", "Europe"), "FRA": ("France", "Europe"),
    "POL": ("Poland", "Europe"), "ESP": ("Spain", "Europe"), "ITA": ("Italy", "Europe"),
    "SWE": ("Sweden", "Europe"), "NLD": ("Netherlands", "Europe"),
    "CHN": ("China", "Asia"), "IND": ("India", "Asia"), "JPN": ("Japan", "Asia"),
    "VNM": ("Vietnam", "Asia"), "IDN": ("Indonesia", "Asia"), "KOR": ("South Korea", "Asia"),
    "SAU": ("Saudi Arabia", "Asia"), "PAK": ("Pakistan", "Asia"),
    "USA": ("United States", "North America"), "CAN": ("Canada", "North America"),
    "MEX": ("Mexico", "North America"), "GTM": ("Guatemala", "North America"),
    "CUB": ("Cuba", "North America"), "DOM": ("Dominican Republic", "North America"),
    "CRI": ("Costa Rica", "North America"), "PAN": ("Panama", "North America"),
    "BRA": ("Brazil", "South America"), "ARG": ("Argentina", "South America"),
    "COL": ("Colombia", "South America"), "CHL": ("Chile", "South America"),
    "PER": ("Peru", "South America"), "VEN": ("Venezuela", "South America"),
    "ECU": ("Ecuador", "South America"), "BOL": ("Bolivia", "South America"),
    "AUS": ("Australia", "Oceania"), "NZL": ("New Zealand", "Oceania"),
    "PNG": ("Papua New Guinea", "Oceania"), "FJI": ("Fiji", "Oceania"),
    "WSM": ("Samoa", "Oceania"), "SLB": ("Solomon Islands", "Oceania"),
    "VUT": ("Vanuatu", "Oceania"), "TON": ("Tonga", "Oceania"),
}

# id: (source, source_code, label, unit) — the indicators fed into each briefing prompt
BRIEFING_INDICATORS = {
    "gdpPerCapita":       ("worldbank", "NY.GDP.PCAP.CD",       "GDP per capita",             "US$"),
    "gdpGrowth":          ("worldbank", "NY.GDP.MKTP.KD.ZG",    "GDP growth",                 "%/yr"),
    "inflation":          ("worldbank", "FP.CPI.TOTL.ZG",       "Inflation (CPI)",            "%/yr"),
    "unemployment":       ("worldbank", "SL.UEM.TOTL.ZS",       "Unemployment",                "% of labor force"),
    "lifeExp":            ("worldbank", "SP.DYN.LE00.IN",       "Life expectancy",            "years"),
    "population":         ("worldbank", "SP.POP.TOTL",          "Population",                  "people"),
    "ruleOfLaw":          ("worldbank", "RL.EST",               "Rule of Law (WGI)",           "score, -2.5 to 2.5"),
    "politicalStability": ("worldbank", "PV.EST",               "Political Stability (WGI)",   "score, -2.5 to 2.5"),
    "under5Mortality":    ("who",       "MDG_0000000007",       "Under-5 mortality (WHO)",     "per 1,000 live births"),
}
