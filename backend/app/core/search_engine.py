"""
Stock Search & Company Name Resolver Engine with Fuzzy Typo Matching.
Provides instant fuzzy, substring, and real-time exchange search across NSE, BSE, and global equities.
"""

import io
import difflib
import requests
from typing import List, Dict

LOCAL_STOCK_MASTER: Dict[str, str] = {
    "PICCADIL.NS": "Piccadily Agro Industries Ltd",
    "PICCADIL.BO": "Piccadily Agro Industries Ltd",
    "PICCASUG.BO": "Piccadily Sugar & Allied Industries Ltd",
    "CONFIPET.NS": "Confidence Petroleum India Ltd",
    "CONFIPET.BO": "Confidence Petroleum India Ltd",
    "RELIANCE.NS": "Reliance Industries Ltd",
    "TCS.NS": "Tata Consultancy Services Ltd",
    "HDFCBANK.NS": "HDFC Bank Ltd",
    "ICICIBANK.NS": "ICICI Bank Ltd",
    "INFY.NS": "Infosys Ltd",
    "BHARTIARTL.NS": "Bharti Airtel Ltd",
    "SBIN.NS": "State Bank of India",
    "TATAMOTORS.NS": "Tata Motors Ltd",
    "TMCV.NS": "Tata Motors Commercial Vehicles Ltd",
    "TMPV.NS": "Tata Motors Passenger Vehicles Ltd",
    "BAJFINANCE.NS": "Bajaj Finance Ltd",
    "LT.NS": "Larsen & Toubro Ltd",
    "TRENT.NS": "Trent Ltd",
    "BEL.NS": "Bharat Electronics Ltd",
    "HAL.NS": "Hindustan Aeronautics Ltd",
    "ZOMATO.NS": "Zomato Ltd",
    "VBL.NS": "Varun Beverages Ltd",
    "DLF.NS": "DLF Ltd",
    "CHOLAFIN.NS": "Cholamandalam Investment and Finance Company",
    "TITAN.NS": "Titan Company Ltd",
    "SUNPHARMA.NS": "Sun Pharmaceutical Industries Ltd",
    "MARUTI.NS": "Maruti Suzuki India Ltd",
    "AXISBANK.NS": "Axis Bank Ltd",
    "NTPC.NS": "NTPC Ltd",
    "ONGC.NS": "Oil & Natural Gas Corporation Ltd",
    "M&M.NS": "Mahindra & Mahindra Ltd",
    "TATASTEEL.NS": "Tata Steel Ltd",
    "COALINDIA.NS": "Coal India Ltd",
    "HCLTECH.NS": "HCL Technologies Ltd",
    "KOTAKBANK.NS": "Kotak Mahindra Bank Ltd",
    "ITC.NS": "ITC Ltd",
    "HINDUNILVR.NS": "Hindustan Unilever Ltd",
    "ADANIENT.NS": "Adani Enterprises Ltd",
    "ADANIPORTS.NS": "Adani Ports and Special Economic Zone Ltd",
    "POWERGRID.NS": "Power Grid Corporation of India Ltd",
    "BAJAJFINSV.NS": "Bajaj Finserv Ltd",
    "ASIANPAINT.NS": "Asian Paints Ltd",
    "SIEMENS.NS": "Siemens Ltd",
    "ULTRACEMCO.NS": "UltraTech Cement Ltd",
    "JSWSTEEL.NS": "JSW Steel Ltd",
    "INDUSINDBK.NS": "IndusInd Bank Ltd",
    "TECHM.NS": "Tech Mahindra Ltd",
    "NESTLEIND.NS": "Nestle India Ltd",
    "WIPRO.NS": "Wipro Ltd",
    "GRASIM.NS": "Grasim Industries Ltd",
    "HINDALCO.NS": "Hindalco Industries Ltd",
    "DRREDDY.NS": "Dr. Reddy's Laboratories Ltd",
    "CIPLA.NS": "Cipla Ltd",
    "SBILIFE.NS": "SBI Life Insurance Company Ltd",
    "HDFCLIFE.NS": "HDFC Life Insurance Company Ltd",
    "BRITANNIA.NS": "Britannia Industries Ltd",
    "TATACONSUM.NS": "Tata Consumer Products Ltd",
    "EICHERMOT.NS": "Eicher Motors Ltd",
    "APOLLOHOSP.NS": "Apollo Hospitals Enterprise Ltd",
    "DIVISLAB.NS": "Divi's Laboratories Ltd",
    "HEROMOTOCO.NS": "Hero MotoCorp Ltd",
    "BPCL.NS": "Bharat Petroleum Corporation Ltd",
    "SHRIRAMFIN.NS": "Shriram Finance Ltd",
    "AUBANK.NS": "AU Small Finance Bank Ltd",
    "AWL.NS": "Adani Wilmar Ltd",
    "FACT.NS": "Fertilisers and Chemicals Travancore Ltd",
    "SAIL.NS": "Steel Authority of India Ltd",
    "GROWW.NS": "Groww (Billionbrains Garage)",
    "FIVESTAR.NS": "Five-Star Business Finance Ltd",
    "AADHARHFC.NS": "Aadhar Housing Finance Ltd",
    "ANGELONE.NS": "Angel One Ltd",
    "ASTERDM.NS": "Aster DM Healthcare Ltd",
    "KIMS.NS": "Krishna Institute of Medical Sciences Ltd",
    "CUMMINSIND.NS": "Cummins India Ltd",
    "SUNTV.NS": "Sun TV Network Ltd",
    "SHYAMMETL.NS": "Shyam Metalics and Energy Ltd",
    "STARHEALTH.NS": "Star Health and Allied Insurance Company Ltd",
    "AUROPHARMA.NS": "Aurobindo Pharma Ltd",
    "DEEPAKNTR.NS": "Deepak Nitrite Ltd",
    "NYKAA.NS": "FSN E-Commerce Ventures (Nykaa)",
    "GAIL.NS": "GAIL (India) Ltd",
    "ASHOKLEY.NS": "Ashok Leyland Ltd",
    "AIIL.NS": "Authum Investment & Infrastructure Ltd",
    "INDIANB.NS": "Indian Bank",
    "KEI.NS": "KEI Industries Ltd",
    "LTF.NS": "L&T Finance Ltd",
    "M&MFIN.NS": "Mahindra & Mahindra Financial Services Ltd",
    "OBEROIRLTY.NS": "Oberoi Realty Ltd",
    "UNOMINDA.NS": "Uno Minda Ltd",
    "ABDL.NS": "Allied Blenders and Distillers Ltd",
    "CUB.NS": "City Union Bank Ltd",
    "NUVAMA.NS": "Nuvama Wealth Management Ltd",
    "WOCKPHARMA.NS": "Wockhardt Ltd",
    "LALPATHLAB.NS": "Dr. Lal PathLabs Ltd",
    "MAZDOCK.NS": "Mazagon Dock Shipbuilders Ltd",
    "PNB.NS": "Punjab National Bank",
    "UNIONBANK.NS": "Union Bank of India",
    "CONCOR.NS": "Container Corporation of India Ltd",
    "PETRONET.NS": "Petronet LNG Ltd",
    "IOC.NS": "Indian Oil Corporation Ltd",
    "HINDPETRO.NS": "Hindustan Petroleum Corporation Ltd",
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
    "GOOGL": "Alphabet Inc. (Google)",
    "AMZN": "Amazon.com Inc.",
    "META": "Meta Platforms Inc.",
    "TSLA": "Tesla Inc."
}


class SearchEngine:
    _master_populated = False

    @classmethod
    def _populate_from_nifty500(cls):
        if cls._master_populated:
            return
        try:
            url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(url, headers=headers, timeout=4)
            if resp.status_code == 200:
                import pandas as pd
                df = pd.read_csv(io.StringIO(resp.text))
                if "Symbol" in df.columns and "Company Name" in df.columns:
                    for _, row in df.iterrows():
                        sym = f"{str(row['Symbol']).strip()}.NS"
                        name = str(row['Company Name']).strip()
                        LOCAL_STOCK_MASTER[sym] = name
            cls._master_populated = True
        except Exception:
            cls._master_populated = True

    @classmethod
    def get_company_name(cls, symbol: str) -> str:
        """
        Returns the full registered company name for a given symbol.
        """
        cls._populate_from_nifty500()
        sym_clean = symbol.strip().upper()
        if sym_clean in LOCAL_STOCK_MASTER:
            return LOCAL_STOCK_MASTER[sym_clean]
        
        if not sym_clean.endswith(('.NS', '.BO')):
            if f"{sym_clean}.NS" in LOCAL_STOCK_MASTER:
                return LOCAL_STOCK_MASTER[f"{sym_clean}.NS"]
            if f"{sym_clean}.BO" in LOCAL_STOCK_MASTER:
                return LOCAL_STOCK_MASTER[f"{sym_clean}.BO"]
        
        bare = sym_clean.replace('.NS', '').replace('.BO', '')
        for s, n in LOCAL_STOCK_MASTER.items():
            if s.replace('.NS', '').replace('.BO', '') == bare:
                return n
                
        return sym_clean

    @classmethod
    def search(cls, query: str, limit: int = 8) -> List[Dict[str, str]]:
        """
        Searches across symbols and company names using exact, substring, fuzzy typo, and real-time exchange search.
        """
        if not query or len(query.strip()) < 1:
            return []

        cls._populate_from_nifty500()

        q = query.strip().lower()
        q_clean = q.replace(".ns", "").replace(".bo", "").replace(" ", "").replace("-", "")
        results = []
        seen_syms = set()

        # 1. Exact matches & direct starts-with in local master
        for sym, name in list(LOCAL_STOCK_MASTER.items()):
            sym_clean = sym.lower().replace(".ns", "").replace(".bo", "")
            if sym_clean == q or sym_clean == q_clean:
                results.append({
                    "symbol": sym,
                    "name": name,
                    "exchange": "NSE" if sym.endswith(".NS") else ("BSE" if sym.endswith(".BO") else "US"),
                    "score": 100
                })
                seen_syms.add(sym)

        # 2. Direct Substring Match in symbol or company name
        for sym, name in list(LOCAL_STOCK_MASTER.items()):
            if sym in seen_syms:
                continue
            sym_lower = sym.lower()
            name_lower = name.lower()

            if q in sym_lower or q_clean in sym_lower.replace(".ns", "").replace(".bo", ""):
                results.append({
                    "symbol": sym,
                    "name": name,
                    "exchange": "NSE" if sym.endswith(".NS") else ("BSE" if sym.endswith(".BO") else "US"),
                    "score": 90
                })
                seen_syms.add(sym)
            elif q in name_lower or q_clean in name_lower or any(word in name_lower for word in q_clean.split() if len(word) >= 3):
                results.append({
                    "symbol": sym,
                    "name": name,
                    "exchange": "NSE" if sym.endswith(".NS") else ("BSE" if sym.endswith(".BO") else "US"),
                    "score": 80
                })
                seen_syms.add(sym)

        # 3. Always Query Live Yahoo Finance Search API for unindexed or newly listed smallcaps
        try:
            search_term = q_clean if len(q_clean) >= 2 else query
            yf_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={requests.utils.quote(search_term)}&quotesCount=8&newsCount=0"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(yf_url, headers=headers, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                for quote in data.get("quotes", []):
                    sym = quote.get("symbol")
                    if not sym:
                        continue
                    shortname = quote.get("shortname") or quote.get("longname") or sym
                    exch = quote.get("exchDisp") or quote.get("exchange") or "NSE"
                    if sym not in seen_syms:
                        # Prioritize Indian (.NS / .BO) and US symbols
                        if sym.endswith((".NS", ".BO")) or "." not in sym:
                            results.append({
                                "symbol": sym,
                                "name": shortname,
                                "exchange": "NSE" if sym.endswith(".NS") else ("BSE" if sym.endswith(".BO") else exch),
                                "score": 85
                            })
                            seen_syms.add(sym)
                            LOCAL_STOCK_MASTER[sym] = shortname
        except Exception:
            pass

        # 4. Fuzzy Sequence Ratio Matching with difflib across entire master
        if len(results) < limit:
            scored_candidates = []
            for sym, name in list(LOCAL_STOCK_MASTER.items()):
                if sym in seen_syms:
                    continue
                name_clean = name.lower().replace("ltd", "").replace("limited", "").replace("corporation", "").replace("industries", "").replace("india", "").strip()
                sim_name = max(
                    difflib.SequenceMatcher(None, q, name_clean).ratio(),
                    difflib.SequenceMatcher(None, q_clean, name_clean).ratio(),
                    difflib.SequenceMatcher(None, q_clean, name_clean.split()[0] if name_clean else "").ratio()
                )
                sim_sym = difflib.SequenceMatcher(None, q_clean, sym.lower().replace(".ns", "").replace(".bo", "")).ratio()
                best_sim = max(sim_name, sim_sym)

                if best_sim >= 0.35:
                    scored_candidates.append((best_sim, sym, name))

            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            for sim, sym, name in scored_candidates[:limit - len(results)]:
                results.append({
                    "symbol": sym,
                    "name": name,
                    "exchange": "NSE" if sym.endswith(".NS") else ("BSE" if sym.endswith(".BO") else "US"),
                    "score": int(sim * 100)
                })
                seen_syms.add(sym)

        return results[:limit]
