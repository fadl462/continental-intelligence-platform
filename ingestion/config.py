"""
Single source of truth for which indicators/countries get ingested.
Keep this in sync with the INDICATORS / CONTINENTS objects in
continental_intelligence_platform.html if you add more.
"""

INDICATORS = {
    # id: (source, source_code, label, unit, module)
    "gdpPerCapita":       ("worldbank", "NY.GDP.PCAP.CD",        "GDP per capita",              "US$",                     "economic"),
    "gdpGrowth":          ("worldbank", "NY.GDP.MKTP.KD.ZG",     "GDP growth",                  "% / yr",                  "economic"),
    "inflation":          ("worldbank", "FP.CPI.TOTL.ZG",        "Inflation (CPI)",             "% / yr",                  "economic"),
    "unemployment":       ("worldbank", "SL.UEM.TOTL.ZS",        "Unemployment",                "% of labor force",       "economic"),
    "population":         ("worldbank", "SP.POP.TOTL",           "Population",                  "people",                  "human"),
    "lifeExp":            ("worldbank", "SP.DYN.LE00.IN",        "Life expectancy",             "years",                   "human"),
    "secEnroll":          ("worldbank", "SE.SEC.NENR",           "Secondary school enrollment", "% net",                   "human"),
    "matMortality":       ("worldbank", "SH.STA.MMRT",           "Maternal mortality ratio",    "per 100k births",         "human"),
    "internet":           ("worldbank", "IT.NET.USER.ZS",        "Internet users",              "% of population",         "environment"),
    "co2":                ("worldbank", "EN.GHG.CO2.PC.CE.AR5",  "CO2 emissions per capita",    "tCO2e",                   "environment"),
    "ruleOfLaw":          ("worldbank", "RL.EST",                "Rule of Law (WGI)",           "score, -2.5 to 2.5",      "governance"),
    "govEffectiveness":   ("worldbank", "GE.EST",                "Government Effectiveness (WGI)", "score, -2.5 to 2.5",   "governance"),
    "politicalStability": ("worldbank", "PV.EST",                "Political Stability (WGI)",   "score, -2.5 to 2.5",      "governance"),
    "corruption":         ("worldbank", "CC.EST",                "Control of Corruption (WGI)", "score, -2.5 to 2.5",      "governance"),
    "povertyRate":        ("worldbank", "SI.POV.DDAY",           "Poverty rate (SDG 1)",        "% below $2.15/day",       "governance"),
    "electricityAccess":  ("worldbank", "EG.ELC.ACCS.ZS",        "Electricity access (SDG 7)",  "% of population",         "governance"),
    "whoLifeExp":         ("who",       "WHOSIS_000001",         "Life expectancy (WHO)",       "years",                   "health"),
    "under5Mortality":    ("who",       "MDG_0000000007",        "Under-5 mortality (WHO)",     "per 1,000 live births",   "health"),
    "immunization":       ("who",       "WHS4_100",              "Measles immunization (WHO)",  "% of 1-year-olds",        "health"),
}

COUNTRIES = {
    # iso3: (name, region/continent)
    "GHA": ("Ghana", "Africa"), "NGA": ("Nigeria", "Africa"), "KEN": ("Kenya", "Africa"),
    "ZAF": ("South Africa", "Africa"), "EGY": ("Egypt", "Africa"), "ETH": ("Ethiopia", "Africa"),
    "CIV": ("Côte d'Ivoire", "Africa"), "MAR": ("Morocco", "Africa"),
    "DEU": ("Germany", "Europe"), "GBR": ("United Kingdom", "Europe"), "FRA": ("France", "Europe"),
    "POL": ("Poland", "Europe"), "ESP": ("Spain", "Europe"), "ITA": ("Italy", "Europe"),
    "SWE": ("Sweden", "Europe"), "NLD": ("Netherlands", "Europe"),
    "CHN": ("China", "Asia"), "IND": ("India", "Asia"), "JPN": ("Japan", "Asia"),
    "VNM": ("Vietnam", "Asia"), "IDN": ("Indonesia", "Asia"), "KOR": ("South Korea", "Asia"),
    "SAU": ("Saudi Arabia", "Asia"), "PAK": ("Pakistan", "Asia"),
    "USA": ("United States", "Americas"), "BRA": ("Brazil", "Americas"), "MEX": ("Mexico", "Americas"),
    "CAN": ("Canada", "Americas"), "ARG": ("Argentina", "Americas"), "COL": ("Colombia", "Americas"),
    "CHL": ("Chile", "Americas"), "PER": ("Peru", "Americas"),
    "AUS": ("Australia", "Oceania"), "NZL": ("New Zealand", "Oceania"),
    "PNG": ("Papua New Guinea", "Oceania"), "FJI": ("Fiji", "Oceania"),
}

SERIES_FROM_YEAR = 2005
SERIES_TO_YEAR = 2025
