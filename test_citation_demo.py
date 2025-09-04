#!/usr/bin/env python3
"""
Test script to demonstrate the improved citation extraction logic
using the existing ChatGPT response data
"""

import re

def extract_citations_from_text(text):
    """Test the improved citation extraction logic"""
    links = set()
    
    print(f"🔍 Processing {len(text)} characters of text for citations...")
    
    # Find URLs in text using regex
    url_pattern = r'https?://[^\s\)]+'
    text_urls = re.findall(url_pattern, text)
    print(f"🔗 Found {len(text_urls)} URLs in text")
    for url in text_urls:
        # Clean URL
        if "?" in url:
            url = url.split("?")[0]
        if ")" in url:
            url = url.rstrip(")")
        links.add(url)
        print(f"✅ Added URL citation: {url}")
    
    # Look for domain-like patterns
    domain_pattern = r'\b[A-Z][a-zA-Z\s&]+(?:\.com|\.io|\.org|\.net|\.co\.uk|\.ai|\.tech)\b'
    domain_matches = re.findall(domain_pattern, text)
    print(f"🌐 Found {len(domain_matches)} domain-like patterns")
    for domain in domain_matches:
        clean_domain = domain.strip()
        if clean_domain and len(clean_domain) > 3:
            links.add(f"Potential source: {clean_domain}")
            print(f"✅ Added domain citation: {clean_domain}")
    
    # Look for company names that might be sources
    company_pattern = r'\b(?:Business Chief|AI Magazine|FNLondon|Business Insider|The Wall Street Journal|Wikipedia|McKinsey|BCG|Deloitte|EY|PwC|Accenture|IBM|Infosys|Capgemini|Cognizant|Financial Times|The Times of India|The Australian|LinkedIn|Superside|Bitcot|Goml|Ailoitte|Xonique|Faculty|Fractal|Algoscale|Quantiphi|Tredence|ZS Associates|Slalom|Booz Allen Hamilton|Unity Advisory|Keystone|Fusion Collective|Slideworks|Monevate|SIB|Perceptis|Xavier AI)\b'
    company_matches = re.findall(company_pattern, text)
    print(f"🏢 Found {len(company_matches)} company name matches")
    for company in company_matches:
        links.add(f"Source: {company}")
        print(f"✅ Added company citation: {company}")
    
    # Look for any capitalized phrases that might be sources
    source_pattern = r'\b[A-Z][a-zA-Z\s&]+(?:Magazine|Journal|Times|Insider|Chief|London|Financial|Wall Street|Business|AI|Tech|Consulting|Analytics|Platform|Company|Firm|Group|Advisory|Collective|Works|Advisory)\b'
    source_matches = re.findall(source_pattern, text)
    print(f"📰 Found {len(source_matches)} source pattern matches")
    for source in source_matches:
        clean_source = source.strip()
        if clean_source and len(clean_source) > 3:
            # Check if it's not already captured
            if not any(clean_source in link for link in links):
                links.add(f"Potential source: {clean_source}")
                print(f"✅ Added source citation: {clean_source}")
    
    return sorted(links)

# Test with the example text you provided
test_text = """You're asking who provides the best AI services in IT consulting, and based on current insights across the industry, here's a refined overview of leading players along with emerging specialists reshaping the space:

Top Global IT Consulting Firms with AI Expertise
IBM Consulting (including Watsonx)
Recognized consistently as a top-tier provider in AI consulting, offering end-to-end AI strategy, implementation, and management—with a strong ethical and enterprise-grade tech orientation. Use of platforms like Watsonx and integrations like Meta's Llama 2 underscore its technical leadership.
Business Chief
AI Magazine
Accenture
A global powerhouse in digital and AI strategy, implementing vast AI initiatives across industries. It has invested heavily (up to US$3 billion) in AI and GenAI, rolling out hundreds of internal AI applications and reinforcing client transformation capabilities.
AI Magazine
FNLondon
goml.io
McKinsey & Company (QuantumBlack)
Their AI consulting arm, QuantumBlack, unites over 1,000 consultants globally to tackle advanced analytics and automation. AI accounts for about 40% of McKinsey's work, showing entrenched AI integration across the firm.
AI Magazine
Business Insider
Boston Consulting Group (BCG)
Their AI services are structured around strategic business transformation—not just technical deployment. Partnerships with Microsoft and other tech players aid in delivering end-to-end AI strategies that yield meaningful ROI.
AI Magazine
Business Insider
PwC
Heavily investing in AI—planning US$1 billion over three years—PwC focuses on AI training, automation, and innovation via partnerships with Microsoft and OpenAI.
AI Magazine
The Wall Street Journal
Deloitte
Offers AI advisory services including strategy, governance, and implementation. Their AI tools like Zora (co-developed with NVIDIA) drive AI capabilities in finance, tax, and supply chain domains.
AI Magazine
ailoitte.com
EY (Ernst & Young)
With platforms like EY.ai and a strong emphasis on responsible, ethical AI, EY supports clients through strategy design, automation, and AI integration across industries.
AI Magazine
Bitcot
Infosys
Known for AI automation acceleration through Topaz and other platforms, Infosys brings practical, scalable AI use cases to sectors like telecom, finance, and manufacturing.
AI Magazine
ailoitte.com
Capgemini
Delivers AI services including intelligent automation, conversational AI, and GenAI, backed by strong global reach and strategic tech capabilities.
AI Magazine
Xonique - Leading AI Development Company
Cognizant
An IT services leader with dedicated AI consulting through its AI & Data Platform team, Cognizant supports enterprises with AI strategies, platforms, and deployment.
AI Magazine
Bitcot
Emerging Boutique Firms Offering Nimble, AI-Centric Services
In addition to the giants, specialized AI-first boutique firms are gaining attention for their flexibility, focused expertise, and cost-effectiveness:
Xavier AI, Perceptis, SIB, Monevate, Keystone, Fusion Collective, Slideworks, and Unity Advisory stand out for delivering niche AI capabilities—from pricing strategy to operational AI and infrastructure readiness.
Business Insider
These firms often offer tailored, agile solutions without the overhead of large consultancies.
London and UK Spotlight: Faculty
Since you're based in London, UK—it's worth highlighting Faculty, a London-founded AI consultancy offering AI-powered software and strategy consulting. They've worked with UK government bodies and the NHS, particularly during the COVID‑19 pandemic.
Wikipedia
Recommendation Summary Table
Consulting Entity Strengths Best For...
IBM Enterprise-grade AI, ethics, deep tech platforms Large regulated sectors
Accenture Scale, AI reinvention, global delivery Complex multi-industry adoption
McKinsey/QuantumBlack Strategy-driven, advanced analytics High-impact transformation initiatives
BCG Business & people change focus, strategic execution Organizations needing responsible AI
PwC Skill training, large AI invest, GenAI tools Workforce upskilling and governance
Deloitte AI in finance, operations via agentic tools Automation and domain-specific tasks
EY Ethical AI, integrated advisory and deployment Trust-sensitive industries
Infosys Industrial-scale automation & platforms Manufacturing, telecom, digital scale
Capgemini End-to-end implementation globally Performance-driven enterprises
Cognizant AI strategy + tech integration IT-heavy enterprises
Boutiques Flexible, AI-specialist services Targeted projects, SMEs, cost-efficiency
Faculty (UK) Local expertise, public sector projects UK-specific strategy, public sector AI
Final Thoughts
For global reach and transformation: Accenture, IBM, McKinsey, BCG.
For ethical/responsible AI at scale: PwC, Deloitte, EY.
For tech-driven enterprise automation: Infosys, Cognizant, Capgemini.
For agile, lean projects: Boutique AI consultancies.
For UK-based needs: Faculty provides a local, experienced alternative.
Let me know your specific industry, project goals, or whether you're looking at strategy, deployment, or training—I'd be happy to help narrow the field further!
More on AI Consulting News
Business Insider
McKinsey, BCG, and Deloitte's new competition is small, fast, and driven by AI
Apr 28, 2025
FNLondon
Accenture backs AI boom with new management structure
Jun 20, 2025"""

print("🚀 Testing Improved Citation Extraction Logic")
print("=" * 60)

citations = extract_citations_from_text(test_text)

print("\n" + "=" * 60)
print(f"📚 Final Results: {len(citations)} citations extracted")
print("=" * 60)

for i, citation in enumerate(citations, 1):
    print(f"{i:2d}. {citation}")

print("\n✅ This demonstrates what the improved scraper would capture!")

