import asyncio
import time
import feedparser
import httpx
import os
import json
from datetime import datetime
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ Critical Error: GEMINI_API_KEY environment variable is missing.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
SOURCES = [
    # -------------------------------------------------------------
    # 1. GENERAL & NATIONAL NEWS (ETHIOPIA, AFRICA, GLOBAL)
    # -------------------------------------------------------------
    {"category": "general", "name": "ENA", "url": "https://www.ena.et/web/eng/rss"},
    {"category": "general", "name": "Addis Fortune", "url": "https://addisfortune.news/feed/"},
    {"category": "general", "name": "Reporter Ethiopia", "url": "https://news.google.com/rss/search?q=site:ethiopianreporter.com"},
    {"category": "general", "name": "Fana Broadcasting (FBC)", "url": "https://rsshub.app/telegram/channel/fana_broadcast"},
    {"category": "general", "name": "EBC", "url": "https://news.google.com/rss/search?q=site:ebc.et"},
    {"category": "general", "name": "Capital Ethiopia", "url": "https://news.google.com/rss/search?q=site:capitalethiopia.com"},
    {"category": "general", "name": "Borkena", "url": "https://borkena.com/feed/"},
    {"category": "general", "name": "Sheger FM 102.1", "url": "https://news.google.com/rss/search?q=Sheger+FM+102.1+Ethiopia"},
    {"category": "general", "name": "Addis Standard", "url": "https://addisstandard.com/feed/"},
    {"category": "general", "name": "Walta Media (WMCC)", "url": "https://news.google.com/rss/search?q=site:waltainfo.com"},
    {"category": "general", "name": "AllAfrica", "url": "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf"},
    {"category": "general", "name": "Africanews", "url": "https://www.africanews.com/feed/"},
    {"category": "general", "name": "PanaPress", "url": "https://news.google.com/rss/search?q=site:panapress.com"},
    {"category": "general", "name": "Forbes Africa", "url": "https://news.google.com/rss/search?q=site:forbesafrica.com"},
    {"category": "general", "name": "The Africa Report", "url": "https://www.theafricareport.com/feed/"},
    {"category": "general", "name": "The EastAfrican", "url": "https://www.theeastafrican.co.ke/service/rss/2558/feed.rss"},
    {"category": "general", "name": "Daily Nation Kenya", "url": "https://nation.africa/kenya/service/rss/435440/feed.rss"},
    {"category": "general", "name": "The Standard Kenya", "url": "https://www.standardmedia.co.ke/rss/headlines.php"},
    {"category": "general", "name": "Daily Monitor Uganda", "url": "https://www.monitor.co.ug/service/rss/6886/feed.rss"},
    {"category": "general", "name": "The New Times Rwanda", "url": "https://www.newtimes.co.rw/rss"},
    {"category": "general", "name": "The Citizen Tanzania", "url": "https://www.thecitizen.co.tz/service/rss/2740/feed.rss"},
    {"category": "general", "name": "The Guardian Nigeria", "url": "https://guardian.ng/feed/"},
    {"category": "general", "name": "Premium Times Nigeria", "url": "https://www.premiumtimesng.com/feed"},
    {"category": "general", "name": "Channels TV Nigeria", "url": "https://www.channelstv.com/feed/"},
    {"category": "general", "name": "Vanguard Nigeria", "url": "https://www.vanguardngr.com/feed/"},
    {"category": "general", "name": "Daily Graphic Ghana", "url": "https://news.google.com/rss/search?q=site:graphic.com.gh"},
    {"category": "general", "name": "JoyNews Ghana", "url": "https://www.myjoyonline.com/feed/"},
    {"category": "general", "name": "Fraternité Matin Ivory Coast", "url": "https://news.google.com/rss/search?q=site:fratmat.info"},
    {"category": "general", "name": "Le Soleil Senegal", "url": "https://news.google.com/rss/search?q=site:lesoleil.sn"},
    {"category": "general", "name": "SABC News South Africa", "url": "https://www.sabcnews.com/sabcnews/feed/"},
    {"category": "general", "name": "News24 South Africa", "url": "https://news.google.com/rss/search?q=site:news24.com"},
    {"category": "general", "name": "Daily Maverick South Africa", "url": "https://www.dailymaverick.co.za/feed/"},
    {"category": "general", "name": "Business Day South Africa", "url": "https://www.businesslive.co.za/rss/?publication=bd"},
    {"category": "general", "name": "Mail & Guardian South Africa", "url": "https://mg.co.za/feed/"},
    {"category": "general", "name": "The Herald Zimbabwe", "url": "https://www.herald.co.zw/feed/"},
    {"category": "general", "name": "Al-Ahram Egypt", "url": "https://news.google.com/rss/search?q=site:ahram.org.eg"},
    {"category": "general", "name": "MAP Morocco", "url": "https://news.google.com/rss/search?q=site:mapnews.ma"},
    {"category": "general", "name": "El Khabar Algeria", "url": "https://news.google.com/rss/search?q=site:elkhabar.com"},
    {"category": "general", "name": "Business News Tunisia", "url": "https://www.businessnews.com.tn/rss.xml"},
    {"category": "general", "name": "SUNA Sudan", "url": "https://news.google.com/rss/search?q=site:suna-news.net"},
    {"category": "general", "name": "Reuters", "url": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best"},
    {"category": "general", "name": "Associated Press (AP)", "url": "https://news.google.com/rss/search?q=site:apnews.com"},
    {"category": "general", "name": "AFP News", "url": "https://news.google.com/rss/search?q=site:afp.com"},
    {"category": "general", "name": "DPA Germany", "url": "https://news.google.com/rss/search?q=site:dpa.com"},
    {"category": "general", "name": "Agencia EFE", "url": "https://news.google.com/rss/search?q=site:efe.com"},
    {"category": "general", "name": "Anadolu Agency", "url": "https://www.aa.com.tr/en/rss/default?cat=world"},
    {"category": "general", "name": "Kyodo News Japan", "url": "https://news.google.com/rss/search?q=site:english.kyodonews.net"},
    {"category": "general", "name": "Press Trust of India (PTI)", "url": "https://news.google.com/rss/search?q=site:ptinews.com"},
    {"category": "general", "name": "Yonhap News South Korea", "url": "https://news.google.com/rss/search?q=site:en.yna.co.kr"},
    {"category": "general", "name": "Xinhua News China", "url": "http://www.xinhuanet.com/rss/world.xml"},
    {"category": "general", "name": "BBC News", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"category": "general", "name": "The Guardian UK", "url": "https://www.theguardian.com/world/rss"},
    {"category": "general", "name": "Financial Times", "url": "https://www.ft.com/?format=rss"},
    {"category": "general", "name": "The Economist", "url": "https://www.economist.com/sections/international/rss.xml"},
    {"category": "general", "name": "Le Monde France", "url": "https://www.lemonde.fr/rss/une.xml"},
    {"category": "general", "name": "France 24", "url": "https://www.france24.com/en/rss"},
    {"category": "general", "name": "Deutsche Welle (DW)", "url": "https://rss.dw.com/xml/rss-en-all"},
    {"category": "general", "name": "Der Spiegel Germany", "url": "https://www.spiegel.de/international/index.rss"},
    {"category": "general", "name": "El País Spain", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"},
    {"category": "general", "name": "SWI swissinfo.ch", "url": "https://www.swissinfo.ch/eng/rss"},
    {"category": "general", "name": "Politico Europe", "url": "https://www.politico.eu/feed/"},
    {"category": "general", "name": "Euronews", "url": "https://www.euronews.com/rss"},
    {"category": "general", "name": "The New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"category": "general", "name": "The Washington Post", "url": "https://feeds.washingtonpost.com/rss/world"},
    {"category": "general", "name": "The Wall Street Journal", "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"},
    {"category": "general", "name": "Bloomberg News", "url": "https://news.google.com/rss/search?q=site:bloomberg.com"},
    {"category": "general", "name": "CNN International", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"category": "general", "name": "NPR", "url": "https://feeds.npr.org/1004/rss.xml"},
    {"category": "general", "name": "The Atlantic", "url": "https://www.theatlantic.com/feed/all/"},
    {"category": "general", "name": "Foreign Affairs", "url": "https://www.foreignaffairs.com/rss.xml"},
    {"category": "general", "name": "CBC News Canada", "url": "https://www.cbc.ca/cbbc/lineup/topstories.xml"},
    {"category": "general", "name": "Al Jazeera English", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"category": "general", "name": "Al Arabiya", "url": "https://news.google.com/rss/search?q=site:english.alarabiya.net"},
    {"category": "general", "name": "The National UAE", "url": "https://www.thenationalnews.com/arc/outboundfeeds/rss/"},
    {"category": "general", "name": "Middle East Eye", "url": "https://www.middleeasteye.net/rss"},
    {"category": "general", "name": "Haaretz Israel", "url": "https://www.haaretz.com/cmlink/1.4603373"},
    {"category": "general", "name": "The Times of Israel", "url": "https://www.timesofisrael.com/feed/"},
    {"category": "general", "name": "TRT World Turkey", "url": "https://www.trtworld.com/rss"},
    {"category": "general", "name": "South China Morning Post", "url": "https://www.scmp.com/rss/91/feed"},
    {"category": "general", "name": "The Times of India", "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"},
    {"category": "general", "name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss"},
    {"category": "general", "name": "Nikkei Asia", "url": "https://news.google.com/rss/search?q=site:asia.nikkei.com"},
    {"category": "general", "name": "NHK World Japan", "url": "https://news.google.com/rss/search?q=site:www3.nhk.or.jp/nhkworld"},

    # -------------------------------------------------------------
    # 2. SPORTS (ETHIOPIA, AFRICA, GLOBAL)
    # -------------------------------------------------------------
    {"category": "sports", "name": "Soccer Ethiopia", "url": "https://soccerethiopia.net/feed/"},
    {"category": "sports", "name": "Ethiopian Athletics Federation", "url": "https://news.google.com/rss/search?q=Ethiopian+Athletics+Federation"},
    {"category": "sports", "name": "Ethio Foot", "url": "https://news.google.com/rss/search?q=Ethio+Foot"},
    {"category": "sports", "name": "HatTrick Sport", "url": "https://news.google.com/rss/search?q=HatTrick+Sport+Ethiopia"},
    {"category": "sports", "name": "Bisrat FM 101.1 Sports", "url": "https://news.google.com/rss/search?q=Bisrat+FM+Sports"},
    {"category": "sports", "name": "Sheger Sports", "url": "https://news.google.com/rss/search?q=Sheger+FM+Sports"},
    {"category": "sports", "name": "EBC Sport", "url": "https://news.google.com/rss/search?q=EBC+Sport+Ethiopia"},
    {"category": "sports", "name": "Fana Sport", "url": "https://news.google.com/rss/search?q=Fana+Sport+Ethiopia"},
    {"category": "sports", "name": "SuperSport", "url": "https://news.google.com/rss/search?q=site:supersport.com"},
    {"category": "sports", "name": "CAF Online", "url": "https://news.google.com/rss/search?q=site:cafonline.com"},
    {"category": "sports", "name": "BBC Sport Africa", "url": "https://feeds.bbci.co.uk/sport/africa/rss.xml"},
    {"category": "sports", "name": "Africanews Sport", "url": "https://www.africanews.com/feed/sport"},
    {"category": "sports", "name": "FilGoal Egypt", "url": "https://news.google.com/rss/search?q=site:filgoal.com"},
    {"category": "sports", "name": "Hespress Sport Morocco", "url": "https://news.google.com/rss/search?q=site:sport.hespress.com"},
    {"category": "sports", "name": "Brila FM Nigeria", "url": "https://www.brila.net/feed/"},
    {"category": "sports", "name": "Complete Sports Nigeria", "url": "https://www.completesports.com/feed/"},
    {"category": "sports", "name": "Ghanasoccernet", "url": "https://ghanasoccernet.com/feed"},
    {"category": "sports", "name": "Kawowo Sports Uganda", "url": "https://kawowo.com/feed/"},
    {"category": "sports", "name": "KickOff South Africa", "url": "https://news.google.com/rss/search?q=site:kickoff.com"},
    {"category": "sports", "name": "Soccer Laduma South Africa", "url": "https://news.google.com/rss/search?q=site:soccerladuma.co.za"},
    {"category": "sports", "name": "ESPN", "url": "https://www.espn.com/espn/rss/news"},
    {"category": "sports", "name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml"},
    {"category": "sports", "name": "Sky Sports", "url": "https://www.skysports.com/rss/12040"},
    {"category": "sports", "name": "The Athletic", "url": "https://news.google.com/rss/search?q=site:theathletic.com"},
    {"category": "sports", "name": "Marca English", "url": "https://e00-marca.uecdn.es/rss/en/index.xml"},
    {"category": "sports", "name": "La Gazzetta dello Sport", "url": "https://news.google.com/rss/search?q=site:gazzetta.it"},
    {"category": "sports", "name": "L'Équipe France", "url": "https://www.lequipe.fr/rss/actu_rss.xml"},
    {"category": "sports", "name": "Diario AS Spain", "url": "https://as.com/rss/tags/ultimas_noticias.xml"},
    {"category": "sports", "name": "Goal.com", "url": "https://news.google.com/rss/search?q=site:goal.com"},
    {"category": "sports", "name": "Transfermarkt", "url": "https://news.google.com/rss/search?q=site:transfermarkt.com"},
    {"category": "sports", "name": "World Athletics", "url": "https://news.google.com/rss/search?q=site:worldathletics.org"},
    {"category": "sports", "name": "LetsRun.com", "url": "https://www.letsrun.com/feed"},

    # -------------------------------------------------------------
    # 3. TECHNOLOGY & INNOVATION
    # -------------------------------------------------------------
    {"category": "tech", "name": "Shega.co", "url": "https://shega.co/feed/"},
    {"category": "tech", "name": "iCog Labs News", "url": "https://news.google.com/rss/search?q=iCog+Labs+Ethiopia"},
    {"category": "tech", "name": "Ministry of Innovation & Tech (MInT)", "url": "https://news.google.com/rss/search?q=Ministry+of+Innovation+and+Technology+Ethiopia"},
    {"category": "tech", "name": "TechCabal", "url": "https://techcabal.com/feed/"},
    {"category": "tech", "name": "Disrupt Africa", "url": "https://disrupt-africa.com/feed/"},
    {"category": "tech", "name": "Techpoint Africa", "url": "https://techpoint.africa/feed/"},
    {"category": "tech", "name": "Ventureburn", "url": "https://ventureburn.com/feed/"},
    {"category": "tech", "name": "TechCentral South Africa", "url": "https://techcentral.co.za/feed"},
    {"category": "tech", "name": "MyBroadband South Africa", "url": "https://mybroadband.co.za/news/feed"},
    {"category": "tech", "name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
    {"category": "tech", "name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    {"category": "tech", "name": "Wired", "url": "https://www.wired.com/feed/rss"},
    {"category": "tech", "name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
    {"category": "tech", "name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
    {"category": "tech", "name": "CNet", "url": "https://www.cnet.com/rss/news/"},
    {"category": "tech", "name": "Engadget", "url": "https://www.engadget.com/rss.xml"},
    {"category": "tech", "name": "Gizmodo", "url": "https://gizmodo.com/rss"},
    {"category": "tech", "name": "VentureBeat", "url": "https://venturebeat.com/feed/"},
    {"category": "tech", "name": "ZDNET", "url": "https://www.zdnet.com/news/rss.xml"},
    {"category": "tech", "name": "Hacker News", "url": "https://news.ycombinator.com/rss"},
    {"category": "tech", "name": "OpenAI Blog", "url": "https://news.google.com/rss/search?q=site:openai.com/blog"},
    {"category": "tech", "name": "The Hacker News (THN)", "url": "https://feeds.feedburner.com/TheHackersNews"},
    {"category": "tech", "name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
    {"category": "tech", "name": "Tom's Hardware", "url": "https://www.tomshardware.com/feeds/all"},
    {"category": "tech", "name": "GSM Arena", "url": "https://www.gsmarena.com/rss-news-reviews.php3"},
    {"category": "tech", "name": "Technode China", "url": "https://technode.com/feed/"},

    # -------------------------------------------------------------
    # 4. BUSINESS & ECONOMY
    # -------------------------------------------------------------
    {"category": "business", "name": "Addis Fortune", "url": "https://addisfortune.news/feed/"},
    {"category": "business", "name": "Capital Ethiopia Business", "url": "https://news.google.com/rss/search?q=site:capitalethiopia.com"},
    {"category": "business", "name": "National Bank of Ethiopia (NBE)", "url": "https://news.google.com/rss/search?q=National+Bank+of+Ethiopia"},
    {"category": "business", "name": "Ethiopian Business Review (EBR)", "url": "https://news.google.com/rss/search?q=Ethiopian+Business+Review"},
    {"category": "business", "name": "Business Day Africa", "url": "https://news.google.com/rss/search?q=Business+Day+Africa"},
    {"category": "business", "name": "African Business Magazine", "url": "https://african.business/feed"},
    {"category": "business", "name": "BusinessDay Nigeria", "url": "https://businessday.ng/feed/"},
    {"category": "business", "name": "Nairametrics Nigeria", "url": "https://nairametrics.com/feed/"},
    {"category": "business", "name": "Business Daily Africa Kenya", "url": "https://www.businessdailyafrica.com/service/rss/bda/2046/feed.rss"},
    {"category": "business", "name": "Moneyweb South Africa", "url": "https://www.moneyweb.co.za/feed/"},
    {"category": "business", "name": "Fin24 South Africa", "url": "https://news.google.com/rss/search?q=site:fin24.com"},
    {"category": "business", "name": "Enterprise Egypt", "url": "https://enterprise.press/feed/"},
    {"category": "business", "name": "Bloomberg Business", "url": "https://news.google.com/rss/search?q=site:bloomberg.com/news"},
    {"category": "business", "name": "MarketWatch", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
    {"category": "business", "name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
    {"category": "business", "name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex"},
    {"category": "business", "name": "The Wall Street Journal Business", "url": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml"},
    {"category": "business", "name": "Forbes", "url": "https://www.forbes.com/business/feed/"},
    {"category": "business", "name": "Business Insider", "url": "https://www.businessinsider.com/rss"},
    {"category": "business", "name": "Quartz", "url": "https://qz.com/rss"},
    {"category": "business", "name": "Les Echos France", "url": "https://news.google.com/rss/search?q=site:lesechos.fr"},
    {"category": "business", "name": "Arabian Business UAE", "url": "https://www.arabianbusiness.com/feed"},

    # -------------------------------------------------------------
    # 5. LIFESTYLE & ENTERTAINMENT
    # -------------------------------------------------------------
    {"category": "lifestyle", "name": "LinkUp Addis", "url": "https://rsshub.app/telegram/channel/linkupaddis"},
    {"category": "lifestyle", "name": "Addis Insight", "url": "https://addisinsight.net/feed/"},
    {"category": "lifestyle", "name": "EBS TV Entertainment", "url": "https://news.google.com/rss/search?q=EBS+TV+Entertainment+Ethiopia"},
    {"category": "lifestyle", "name": "Kana TV", "url": "https://news.google.com/rss/search?q=Kana+TV+Ethiopia"},
    {"category": "lifestyle", "name": "DireTube", "url": "https://news.google.com/rss/search?q=site:diretube.com"},
    {"category": "lifestyle", "name": "BellaNaija Nigeria", "url": "https://www.bellanaija.com/feed/"},
    {"category": "lifestyle", "name": "GQ South Africa", "url": "https://www.gq.co.za/rss"},
    {"category": "lifestyle", "name": "Pulse Africa", "url": "https://news.google.com/rss/search?q=Pulse+Africa+Entertainment"},
    {"category": "lifestyle", "name": "OkayAfrica", "url": "https://www.okayafrica.com/community/rss"},
    {"category": "lifestyle", "name": "Variety", "url": "https://variety.com/feed/"},
    {"category": "lifestyle", "name": "The Hollywood Reporter", "url": "https://www.hollywoodreporter.com/feed/"},
    {"category": "lifestyle", "name": "Deadline Hollywood", "url": "https://deadline.com/feed/"},
    {"category": "lifestyle", "name": "Rolling Stone", "url": "https://www.rollingstone.com/feed/"},
    {"category": "lifestyle", "name": "Billboard", "url": "https://www.billboard.com/feed/"},
    {"category": "lifestyle", "name": "Pitchfork", "url": "https://pitchfork.com/rss/news/"},
    {"category": "lifestyle", "name": "Vogue", "url": "https://www.vogue.com/feed/rss"},
    {"category": "lifestyle", "name": "GQ Magazine", "url": "https://www.gq.com/feed/rss"},
    {"category": "lifestyle", "name": "Highsnobiety", "url": "https://www.highsnobiety.com/feed/"},
    {"category": "lifestyle", "name": "Hypebeast", "url": "https://hypebeast.com/feed"},
    {"category": "lifestyle", "name": "Condé Nast Traveler", "url": "https://www.cntraveler.com/feed/rss"},
    {"category": "lifestyle", "name": "IGN", "url": "https://feeds.feedburner.com/ign/news"},
    {"category": "lifestyle", "name": "Polygon", "url": "https://www.polygon.com/rss/index.xml"},
    {"category": "lifestyle", "name": "Men's Health", "url": "https://www.menshealth.com/rss/all.xml/"},

    # -------------------------------------------------------------
    # 6. ODD & OFFBEAT NEWS
    # -------------------------------------------------------------
    {"category": "oddities", "name": "Borkena Oddities", "url": "https://borkena.com/category/odd-news/feed/"},
    {"category": "oddities", "name": "EBC Strange & Wonderful", "url": "https://news.google.com/rss/search?q=EBC+Strange+News+Ethiopia"},
    {"category": "oddities", "name": "Sheger FM Yeneta", "url": "https://news.google.com/rss/search?q=Sheger+FM+Yeneta"},
    {"category": "oddities", "name": "Tikvah Ethiopia Odd News", "url": "https://rsshub.app/telegram/channel/TikvahEthiopia"},
    {"category": "oddities", "name": "Oddity Central", "url": "https://www.odditycentral.com/feed"},
    {"category": "oddities", "name": "Oddee", "url": "https://www.oddee.com/feed/"},
    {"category": "oddities", "name": "UPI Odd News", "url": "https://www.upi.com/rss/Odd_News/"},
    {"category": "oddities", "name": "Guinness World Records", "url": "https://news.google.com/rss/search?q=site:guinnessworldrecords.com"},
    {"category": "oddities", "name": "Bored Panda", "url": "https://www.boredpanda.com/feed/"},
    {"category": "oddities", "name": "AP Oddities", "url": "https://news.google.com/rss/search?q=site:apnews.com+oddities"},
    {"category": "oddities", "name": "Reuters Oddly Enough", "url": "https://news.google.com/rss/search?q=site:reuters.com+oddly+enough"},
    {"category": "oddities", "name": "Reddit r/NotTheOnion", "url": "https://www.reddit.com/r/nottheonion/top/.rss?sort=top&t=day"},
    {"category": "oddities", "name": "Live Science Strange News", "url": "https://www.livescience.com/feeds/all"},
    {"category": "oddities", "name": "SoraNews24 Japan", "url": "https://soranews24.com/feed/"}
]


  async def fetch_single_feed(http_client, source):
    try:
        response = await http_client.get(source["url"], timeout=6.0)
        feed = feedparser.parse(response.content)
        items = []
        for entry in feed.entries[:2]:
            items.append({
                "category": source["category"],
                "source": source["name"],
                "headline": getattr(entry, 'title', ''),
                "context": getattr(entry, 'summary', '')
            })
        return items
    except Exception as e:
        print(f"⚠️ Warning: Failed to fetch {source['name']}: {e}")
        return []

async def fetch_all_feeds():
    async with httpx.AsyncClient(follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as http_client:
        tasks = [fetch_single_feed(http_client, src) for src in SOURCES]
        results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]

def generate_tri_lingual_articles(raw_items):
    combined_raw_text = json.dumps(raw_items, ensure_ascii=False, indent=2)
    
    prompt = f"""
You are the Chief Editor for a tri-lingual news network.
Select the top 1 news event for EACH category (general, sports, tech, business, lifestyle, oddities) from the raw data below:

{combined_raw_text}

For each selected story, write complete long-form detailed articles in Amharic (AM), Afaan Oromoo (OM), and English (EN).
Return ONLY a raw JSON array of objects without markdown backticks or commentary. Format exact schema:

[
  {{
    "category": "general|sports|tech|business|lifestyle|oddities",
    "source_name": "Source Name",
    "amharic": {{
      "title": "ርዕስ በአማርኛ...",
      "content": "<p>ዝርዝር አንቀጽ 1...</p><p>ዝርዝር አንቀጽ 2...</p>"
    }},
    "afaan_oromoo": {{
      "title": "Mata Duree Afaan Oromootiin...",
      "content": "<p>Keeyyata 1...</p><p>Keeyyata 2...</p>"
    }},
    "english": {{
      "title": "Detailed English Title...",
      "content": "<p>Detailed paragraph 1...</p><p>Detailed paragraph 2...</p>"
    }}
  }}
]
"""

    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro"]

    for model_name in models_to_try:
        try:
            print(f"Attempting API call with model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            raw_text = response.text.strip()
            
            if "```" in raw_text:
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            
            clean_json = raw_text.strip()
            articles = json.loads(clean_json)
            print(f"✅ SUCCESS: Generated {len(articles)} multi-lingual stories!")
            return articles
        except Exception as e:
            print(f"⚠️ Model {model_name} execution error: {e}")
            time.sleep(1)

    print("❌ Error: All Gemini generation attempts failed.")
    return []

def save_markdown_posts(articles):
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H%M%S")

    for idx, article in enumerate(articles):
        cat = article.get("category", "general")
        source = article.get("source_name", "News")

        # 1. Save Amharic Post
        am_dir = "_posts/am"
        os.makedirs(am_dir, exist_ok=True)
        am_file = f"{am_dir}/{today}-{cat}-{timestamp}-{idx}.md"
        am_meta = f"---\nlayout: post\ntitle: \"{article['amharic']['title']}\"\ncategories: {cat}\nlang: am\nsource: \"{source}\"\n---\n\n{article['amharic']['content']}\n\n<p><strong>📌 ምንጭ:</strong> {source}</p>"
        with open(am_file, "w", encoding="utf-8") as f:
            f.write(am_meta)

        # 2. Save Afaan Oromoo Post
        om_dir = "_posts/om"
        os.makedirs(om_dir, exist_ok=True)
        om_file = f"{om_dir}/{today}-{cat}-{timestamp}-{idx}.md"
        om_meta = f"---\nlayout: post\ntitle: \"{article['afaan_oromoo']['title']}\"\ncategories: {cat}\nlang: om\nsource: \"{source}\"\n---\n\n{article['afaan_oromoo']['content']}\n\n<p><strong>📌 Madda:</strong> {source}</p>"
        with open(om_file, "w", encoding="utf-8") as f:
            f.write(om_meta)

        # 3. Save English Post
        en_dir = "_posts/en"
        os.makedirs(en_dir, exist_ok=True)
        en_file = f"{en_dir}/{today}-{cat}-{timestamp}-{idx}.md"
        en_meta = f"---\nlayout: post\ntitle: \"{article['english']['title']}\"\ncategories: {cat}\nlang: en\nsource: \"{source}\"\n---\n\n{article['english']['content']}\n\n<p><strong>📌 Source:</strong> {source}</p>"
        with open(en_file, "w", encoding="utf-8") as f:
            f.write(en_meta)

    print(f"✅ Generated and committed {len(articles) * 3} post files!")

async def main():
    try:
        print("Starting feed collection...")
        raw_news = await fetch_all_feeds()
        if not raw_news:
            print("❌ No news items fetched from feeds.")
            return
        
        print(f"Collected {len(raw_news)} raw news snippets. Generating articles...")
        articles = generate_tri_lingual_articles(raw_news)
        if articles:
            save_markdown_posts(articles)
        else:
            print("⚠️ Article array empty. Skipping file creation.")
    except Exception as general_error:
        print(f"❌ Unhandled execution error: {general_error}")

if __name__ == "__main__":
    asyncio.run(main())
