import requests

SOAP_URL = "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso"

def call_soap(action: str, body: str) -> str:
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": f"http://www.oorsprong.org/websamples.countryinfo/{action}",
    }
    envelope = f"""
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        {body}
      </soap:Body>
    </soap:Envelope>
    """
    resp = requests.post(SOAP_URL, data=envelope.strip(), headers=headers, timeout=10)
    return resp.text

def get_country_info(code="KZ"):
    try:
        capital_xml = call_soap(
            "CapitalCity",
            f"<CapitalCity xmlns='http://www.oorsprong.org/websamples.countryinfo'><sCountryISOCode>{code}</sCountryISOCode></CapitalCity>",
        )

        capital = None
        if "<m:CapitalCityResult>" in capital_xml:
            capital = capital_xml.split("<m:CapitalCityResult>")[1].split("</m:CapitalCityResult>")[0]

        return {
            "status": "ok",
            "source": "CountryInfoSOAP",
            "country": code,
            "capital": capital,
            "raw": capital_xml,  # можно убрать если не надо
        }
    except Exception as e:
        return {"status": "error", "source": "CountryInfoSOAP", "detail": str(e)}
