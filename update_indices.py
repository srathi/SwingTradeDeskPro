from backend.app.core.index_manager import UNIVERSE_METADATA

# Add midcap 100 and smallcap 100/150/250 official endpoints
UNIVERSE_METADATA["NIFTY_MIDCAP_100"] = {
    "name": "Nifty Midcap 100",
    "exchange": "NSE",
    "url": "https://archives.nseindia.com/content/indices/ind_niftymidcap100list.csv",
    "fallback": [],
    "default_suffix": ".NS"
}

UNIVERSE_METADATA["NIFTY_SMALLCAP_100"] = {
    "name": "Nifty Smallcap 100",
    "exchange": "NSE",
    "url": "https://archives.nseindia.com/content/indices/ind_niftysmallcap100list.csv",
    "fallback": [],
    "default_suffix": ".NS"
}

UNIVERSE_METADATA["NIFTY_SMALLCAP_250"] = {
    "name": "Nifty Smallcap 250",
    "exchange": "NSE",
    "url": "https://archives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
    "fallback": [],
    "default_suffix": ".NS"
}

print("Indices metadata updated successfully.")
