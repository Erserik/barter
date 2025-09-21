import requests

GEONAMES_USERNAME = "yerko"  # замени на свой username с geonames.org

def get_cities_kz():
    url = "http://api.geonames.org/searchJSON"
    params = {
        "country": "KZ",
        "featureClass": "P",
        "maxRows": 50,
        "orderby": "population",
        "username": GEONAMES_USERNAME,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "status": "ok",
            "source": "GeoNames",
            "cities": [g["name"] for g in data.get("geonames", [])],
        }
    except Exception as e:
        return {"status": "error", "source": "GeoNames", "detail": str(e)}
