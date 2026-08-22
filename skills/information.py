"""
Layra Information Module
=====================================
Stock prices, currency conversion, translation, and OCR.
"""

import logging
import subprocess
import urllib.request
import urllib.parse
import json

logger = logging.getLogger("layra.information")


class InformationManager:
    """Stock prices, currency, translation, and OCR tools."""

    # ==========================================
    # Stock Prices
    # ==========================================

    @staticmethod
    def get_stock_price(symbol: str) -> str:
        """Get real-time stock price using Yahoo Finance API."""
        try:
            symbol = symbol.upper().strip()
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            })
            response = urllib.request.urlopen(req, timeout=6)
            data = json.loads(response.read())

            result = data['chart']['result'][0]
            meta = result['meta']
            price = meta.get('regularMarketPrice', 0)
            prev_close = meta.get('previousClose', price)
            change = price - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0
            currency = meta.get('currency', 'USD')
            name = meta.get('longName') or meta.get('shortName') or symbol

            direction = "📈" if change >= 0 else "📉"
            sign = "+" if change >= 0 else ""
            return (
                f"{direction} {name} ({symbol})\n"
                f"Price: {currency} {price:.2f}\n"
                f"Change: {sign}{change:.2f} ({sign}{change_pct:.2f}%)"
            )
        except Exception as e:
            logger.warning(f"Stock lookup failed for {symbol}: {e}")
            return f"Could not fetch stock data for '{symbol}'. Try a valid ticker like AAPL, TSLA, RELIANCE.NS"

    @staticmethod
    def get_multiple_stocks(symbols: str) -> str:
        """Get prices for multiple stocks (comma-separated symbols)."""
        results = []
        for sym in symbols.split(','):
            sym = sym.strip()
            if sym:
                results.append(InformationManager.get_stock_price(sym))
        return "\n\n".join(results)

    # ==========================================
    # Currency Conversion
    # ==========================================

    @staticmethod
    def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
        """Convert currency using free Exchange Rate API."""
        try:
            from_currency = from_currency.upper().strip()
            to_currency = to_currency.upper().strip()

            # Use exchangerate-api (free tier, no key needed for basic)
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=6)
            data = json.loads(response.read())

            rates = data.get('rates', {})
            if to_currency not in rates:
                return f"Currency '{to_currency}' not found."

            rate = rates[to_currency]
            converted = amount * rate

            logger.info(f"💱 {amount} {from_currency} = {converted:.2f} {to_currency}")
            return (
                f"💱 Currency Conversion\n"
                f"{amount:,.2f} {from_currency} = {converted:,.2f} {to_currency}\n"
                f"Rate: 1 {from_currency} = {rate:.4f} {to_currency}"
            )
        except Exception as e:
            logger.warning(f"Currency conversion failed: {e}")
            return f"Currency conversion failed. Please check the currency codes (e.g., USD, INR, EUR)."

    @staticmethod
    def get_inr_rates() -> str:
        """Get common currency rates against Indian Rupee."""
        try:
            url = "https://api.exchangerate-api.com/v4/latest/INR"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=6).read())
            rates = data.get('rates', {})

            currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AED', 'SGD', 'CAD', 'AUD']
            lines = ["💹 INR Exchange Rates:"]
            for c in currencies:
                if c in rates:
                    inv_rate = 1 / rates[c]
                    lines.append(f"  1 {c} = ₹{inv_rate:.2f}")
            return "\n".join(lines)
        except Exception as e:
            return f"Could not fetch INR rates: {e}"

    # ==========================================
    # Translation
    # ==========================================

    @staticmethod
    def translate_text(text: str, target_language: str = "Hindi", gemini_brain=None) -> str:
        """Translate text using Gemini AI."""
        if gemini_brain:
            try:
                prompt = f'Translate this text to {target_language}. Only return the translated text, nothing else:\n\n"{text}"'
                import google.generativeai as genai
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                response = model.generate_content(prompt)
                translated = response.text.strip()
                logger.info(f"🌐 Translated to {target_language}")
                return f"Translation ({target_language}):\n{translated}"
            except Exception as e:
                logger.error(f"Translation error: {e}")
                return f"Translation failed: {e}"
        else:
            return "Translation requires AI brain connection."

    # ==========================================
    # Screen OCR (Read text from screen)
    # ==========================================

    @staticmethod
    def read_screen_text(region: str = "full") -> str:
        """Capture screen and extract text using macOS Vision framework."""
        try:
            import tempfile, os

            # Take screenshot
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_path = f.name

            subprocess.run(['screencapture', '-x', temp_path], check=True, timeout=5)

            # Use macOS Vision via Python (if available)
            try:
                import Vision
                # Vision framework approach
                pass
            except ImportError:
                pass

            # Fallback: Try pytesseract if installed
            try:
                from PIL import Image
                import pytesseract
                img = Image.open(temp_path)
                text = pytesseract.image_to_string(img)
                os.unlink(temp_path)
                if text.strip():
                    return f"Text found on screen:\n{text[:1000]}"
                return "No readable text found on screen."
            except ImportError:
                pass

            # Fallback: Use macOS built-in shortcuts via swift CLI
            swift_ocr = '''
import Vision
import AppKit

let imageURL = URL(fileURLWithPath: "TEMP_PATH")
let requestHandler = VNImageRequestHandler(url: imageURL)
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
try? requestHandler.perform([request])
let texts = request.results?.compactMap { $0.topCandidates(1).first?.string } ?? []
print(texts.joined(separator: " "))
'''.replace('TEMP_PATH', temp_path)

            with tempfile.NamedTemporaryFile(suffix='.swift', mode='w', delete=False) as sf:
                sf.write(swift_ocr)
                swift_path = sf.name

            result = subprocess.run(
                ['swift', swift_path],
                capture_output=True, text=True, timeout=15
            )
            os.unlink(swift_path)
            os.unlink(temp_path)

            if result.stdout.strip():
                logger.info("📷 OCR completed via Swift/Vision")
                return f"Text on screen:\n{result.stdout.strip()[:1000]}"

            return "Could not extract text. Install pytesseract for better OCR: pip install pytesseract"

        except Exception as e:
            logger.error(f"OCR error: {e}")
            return f"Screen OCR failed: {e}"

    # ==========================================
    # Wikipedia Quick Summary
    # ==========================================

    @staticmethod
    def get_wikipedia_summary(topic: str) -> str:
        """Get a quick Wikipedia summary for any topic."""
        try:
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
            req = urllib.request.Request(search_url, headers={'User-Agent': 'Layra/1.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=8).read())
            title = data.get('title', topic)
            extract = data.get('extract', 'No summary found.')
            # Limit to 3 sentences
            sentences = extract.split('. ')
            summary = '. '.join(sentences[:3]) + ('.' if len(sentences) > 3 else '')
            logger.info(f"📚 Wikipedia: {title}")
            return f"📚 {title}:\n{summary}"
        except Exception as e:
            return f"Wikipedia lookup failed for '{topic}': {e}"

    # ==========================================
    # Sports Scores
    # ==========================================

    @staticmethod
    def get_cricket_score() -> str:
        """Get live cricket score from Cricbuzz API."""
        try:
            # Using free CricAPI
            url = "https://api.cricapi.com/v1/currentMatches?apikey=free&offset=0"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=6).read())

            matches = data.get('data', [])[:3]
            if not matches:
                return "No live cricket matches found right now."

            results = ["🏏 Live Cricket:"]
            for m in matches:
                name = m.get('name', 'Unknown')
                status = m.get('status', '')
                score = m.get('score', [])
                score_str = " | ".join(
                    f"{s.get('inning','')}: {s.get('r','0')}/{s.get('w','0')} ({s.get('o','0')} ov)"
                    for s in score[:2]
                ) if score else "Score N/A"
                results.append(f"\n{name}\n{score_str}\n{status}")

            return "\n".join(results)
        except Exception as e:
            logger.warning(f"Cricket score fetch failed: {e}")
            return "Live cricket scores unavailable. Check cricbuzz.com for updates."
