"""
Advanced OSINT Automation Framework
Comprehensive open source intelligence gathering and analysis for defensive cybersecurity.
Enhanced threat hunting, intelligence fusion, and automated security workflows.
"""

import asyncio
import aiohttp
import logging
import json
import re
import hashlib
import ipaddress
import dns.resolver
try:
    import whois
except ImportError:
    whois = None
import socket
try:
    import geoip2.database
    import geoip2.errors
except ImportError:
    geoip2 = None
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse, urljoin, parse_qs
from collections import defaultdict, Counter
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import difflib
import time
import random
import ssl
import certifi
from concurrent.futures import ThreadPoolExecutor
import asyncio
from pathlib import Path

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)

logger = logging.getLogger(__name__)

class IntelligenceSource(Enum):
    """Sources of intelligence data"""
    THREAT_FEEDS = "threat_feeds"
    WHOIS = "whois"
    DNS = "dns"
    GEOLOCATION = "geolocation"
    SOCIAL_MEDIA = "social_media"
    SEARCH_ENGINES = "search_engines"
    DOMAIN_ANALYSIS = "domain_analysis"
    CERTIFICATE_TRANSPARENCY = "certificate_transparency"
    DARKWEB_MONITORING = "darkweb_monitoring"
    VULNERABILITY_DATABASES = "vulnerability_databases"

class ThreatActorType(Enum):
    """Types of threat actors"""
    APT = "apt"
    CYBERCRIMINAL = "cybercriminal"
    HACKTIVIST = "hacktivist"
    INSIDER_THREAT = "insider_threat"
    NATION_STATE = "nation_state"
    RANSOMWARE_GROUP = "ransomware_group"
    SCAMMER = "scammer"
    BOT_OPERATOR = "bot_operator"

class AnalysisType(Enum):
    """Types of analysis performed"""
    DOMAIN_REPUTATION = "domain_reputation"
    IP_REPUTATION = "ip_reputation"
    URL_ANALYSIS = "url_analysis"
    EMAIL_ANALYSIS = "email_analysis"
    THREAT_HUNTING = "threat_hunting"
    ATTRIBUTION = "attribution"
    INFRASTRUCTURE_MAPPING = "infrastructure_mapping"
    CAMPAIGN_TRACKING = "campaign_tracking"

@dataclass
class GeolocationData:
    """Geolocation information for IP addresses"""
    ip_address: str
    country: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    isp: Optional[str] = None
    organization: Optional[str] = None
    asn: Optional[str] = None
    timezone: Optional[str] = None
    threat_types: List[str] = field(default_factory=list)

@dataclass
class DomainIntelligence:
    """Comprehensive domain intelligence data"""
    domain: str
    creation_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    registrar: Optional[str] = None
    registrant: Optional[Dict[str, Any]] = None
    name_servers: List[str] = field(default_factory=list)
    mx_records: List[str] = field(default_factory=list)
    txt_records: List[str] = field(default_factory=list)
    a_records: List[str] = field(default_factory=list)
    aaaa_records: List[str] = field(default_factory=list)
    subdomains: Set[str] = field(default_factory=set)
    certificates: List[Dict[str, Any]] = field(default_factory=list)
    typosquatting_variants: List[str] = field(default_factory=list)
    reputation_score: float = 0.0
    threat_categories: List[str] = field(default_factory=list)
    intelligence_sources: List[str] = field(default_factory=list)

@dataclass
class ThreatActor:
    """Threat actor profile with attribution data"""
    actor_id: str
    aliases: List[str] = field(default_factory=list)
    actor_type: Optional[ThreatActorType] = None
    attribution_confidence: float = 0.0
    first_observed: Optional[datetime] = None
    last_observed: Optional[datetime] = None
    geographic_focus: List[str] = field(default_factory=list)
    target_sectors: List[str] = field(default_factory=list)
    attack_vectors: List[str] = field(default_factory=list)
    infrastructure: Dict[str, List[str]] = field(default_factory=dict)
    indicators: Dict[str, List[str]] = field(default_factory=dict)
    campaigns: List[str] = field(default_factory=list)
    motivations: List[str] = field(default_factory=list)
    sophistication_level: str = "unknown"
    associated_malware: List[str] = field(default_factory=list)

@dataclass
class ThreatCampaign:
    """Threat campaign tracking and analysis"""
    campaign_id: str
    name: Optional[str] = None
    attribution: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_countries: List[str] = field(default_factory=list)
    target_sectors: List[str] = field(default_factory=list)
    attack_chain: List[Dict[str, Any]] = field(default_factory=list)
    indicators: Dict[str, List[str]] = field(default_factory=dict)
    malware_families: List[str] = field(default_factory=list)
    infrastructure: Dict[str, List[str]] = field(default_factory=dict)
    victim_count: int = 0
    financial_impact: float = 0.0

@dataclass
class IntelligenceCorrelation:
    """Correlation between different intelligence sources"""
    correlation_id: str
    primary_indicator: str
    related_indicators: List[str] = field(default_factory=list)
    correlation_strength: float = 0.0
    correlation_type: str = "unknown"
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

class RateLimiter:
    """Advanced rate limiter for API calls"""

    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)

    async def acquire(self, source: str) -> bool:
        """Check if request can be made"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)

        # Clean old requests
        self.requests[source] = [
            req_time for req_time in self.requests[source]
            if req_time > cutoff
        ]

        if len(self.requests[source]) < self.max_requests:
            self.requests[source].append(now)
            return True
        return False

    async def wait_for_slot(self, source: str) -> None:
        """Wait until a slot is available"""
        while not await self.acquire(source):
            await asyncio.sleep(1)

class AdvancedOSINTAutomation:
    """Advanced OSINT automation framework with ML-powered analysis"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.session = None
        self.rate_limiter = RateLimiter()
        self.intelligence_db = {}
        self.correlation_engine = IntelligenceCorrelationEngine()
        self.threat_hunter = AutomatedThreatHunter()
        self.domain_analyzer = AdvancedDomainAnalyzer()
        self.threat_actor_profiler = ThreatActorProfiler()
        self.campaign_tracker = CampaignTracker()
        self.ml_processor = MLIntelligenceProcessor()
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Initialize sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

        # Threat feed configurations with advanced sources
        self.threat_feeds = self._initialize_advanced_threat_feeds()

        # Initialize GeoIP database path (optional)
        self.geoip_db_path = self.config.get('geoip_db_path')

    def _initialize_advanced_threat_feeds(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive threat intelligence feeds"""
        return {
            # Malware and C2 Infrastructure
            "urlhaus_payloads": {
                "url": "https://urlhaus.abuse.ch/downloads/json/",
                "format": "json",
                "type": "malware_urls",
                "update_frequency": 1,
                "reliability": 0.9
            },
            "feodo_tracker": {
                "url": "https://feodotracker.abuse.ch/downloads/ipblocklist.json",
                "format": "json",
                "type": "botnet_c2",
                "update_frequency": 1,
                "reliability": 0.95
            },
            "threatfox_iocs": {
                "url": "https://threatfox.abuse.ch/downloads/json/",
                "format": "json",
                "type": "mixed_iocs",
                "update_frequency": 1,
                "reliability": 0.85
            },

            # Phishing and Scam Intelligence
            "openphish": {
                "url": "https://openphish.com/feed.txt",
                "format": "text",
                "type": "phishing_urls",
                "update_frequency": 1,
                "reliability": 0.8
            },
            "phishtank": {
                "url": "http://data.phishtank.com/data/online-valid.json",
                "format": "json",
                "type": "phishing_urls",
                "update_frequency": 1,
                "reliability": 0.85
            },
            "scam_advisors": {
                "url": "https://www.scam-detector.com/validator/",
                "format": "api",
                "type": "scam_domains",
                "update_frequency": 6,
                "reliability": 0.7
            },

            # IP Reputation and Geolocation
            "abuseipdb": {
                "url": "https://api.abuseipdb.com/api/v2/",
                "format": "api",
                "type": "ip_reputation",
                "update_frequency": 2,
                "reliability": 0.9
            },
            "virustotal": {
                "url": "https://www.virustotal.com/vtapi/v2/",
                "format": "api",
                "type": "multi_scanner",
                "update_frequency": 1,
                "reliability": 0.95
            },
            "shodan": {
                "url": "https://api.shodan.io/",
                "format": "api",
                "type": "internet_scanning",
                "update_frequency": 24,
                "reliability": 0.9
            },

            # Certificate Transparency
            "crt_sh": {
                "url": "https://crt.sh/",
                "format": "json",
                "type": "certificates",
                "update_frequency": 6,
                "reliability": 0.95
            },
            "certificate_transparency": {
                "url": "https://ct.googleapis.com/logs/argon2023/",
                "format": "json",
                "type": "certificates",
                "update_frequency": 1,
                "reliability": 0.98
            },

            # Cryptocurrency Tracking
            "bitcoin_abuse": {
                "url": "https://www.bitcoinabuse.com/api/",
                "format": "api",
                "type": "crypto_addresses",
                "update_frequency": 6,
                "reliability": 0.8
            },
            "chainanalysis": {
                "url": "https://api.chainalysis.com/",
                "format": "api",
                "type": "crypto_intelligence",
                "update_frequency": 2,
                "reliability": 0.95
            },

            # Dark Web Monitoring (Defensive)
            "darkweb_intel": {
                "url": "defensive_only",
                "format": "custom",
                "type": "darkweb_mentions",
                "update_frequency": 12,
                "reliability": 0.7
            }
        }

    async def initialize_session(self) -> None:
        """Initialize HTTP session with security headers"""
        if not self.session:
            connector = aiohttp.TCPConnector(
                ssl=ssl.create_default_context(cafile=certifi.where()),
                limit=100,
                limit_per_host=30
            )
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Defensive Security Research)',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache'
            }
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )

    async def close_session(self) -> None:
        """Close HTTP session and cleanup resources"""
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=True)

    async def perform_comprehensive_domain_analysis(self, domain: str) -> DomainIntelligence:
        """Perform comprehensive multi-source domain analysis"""
        await self.initialize_session()

        domain_intel = DomainIntelligence(domain=domain)

        # Parallel analysis tasks
        tasks = [
            self._analyze_whois_data(domain),
            self._analyze_dns_records(domain),
            self._check_certificate_transparency(domain),
            self._analyze_domain_reputation(domain),
            self._generate_typosquatting_analysis(domain),
            self._check_subdomain_enumeration(domain),
            self._analyze_domain_infrastructure(domain)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge results into domain intelligence
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Domain analysis task {i} failed: {result}")
                continue

            if isinstance(result, dict):
                self._merge_domain_intelligence(domain_intel, result)

        # Calculate final reputation score
        domain_intel.reputation_score = self._calculate_domain_reputation_score(domain_intel)

        return domain_intel

    async def _analyze_whois_data(self, domain: str) -> Dict[str, Any]:
        """Analyze WHOIS data with enhanced parsing"""
        try:
            # Use thread executor for blocking WHOIS call
            whois_data = await asyncio.get_event_loop().run_in_executor(
                self.executor, whois.whois, domain
            )

            return {
                'whois': {
                    'creation_date': whois_data.creation_date,
                    'expiration_date': whois_data.expiration_date,
                    'registrar': whois_data.registrar,
                    'registrant': {
                        'name': getattr(whois_data, 'name', None),
                        'organization': getattr(whois_data, 'org', None),
                        'country': getattr(whois_data, 'country', None),
                        'email': getattr(whois_data, 'email', None)
                    },
                    'name_servers': whois_data.name_servers or []
                }
            }
        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {e}")
            return {'whois': None}

    async def _analyze_dns_records(self, domain: str) -> Dict[str, Any]:
        """Comprehensive DNS record analysis"""
        dns_data = {
            'a_records': [],
            'aaaa_records': [],
            'mx_records': [],
            'txt_records': [],
            'cname_records': [],
            'ns_records': []
        }

        record_types = [
            ('A', 'a_records'),
            ('AAAA', 'aaaa_records'),
            ('MX', 'mx_records'),
            ('TXT', 'txt_records'),
            ('CNAME', 'cname_records'),
            ('NS', 'ns_records')
        ]

        for record_type, key in record_types:
            try:
                answers = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    lambda: dns.resolver.resolve(domain, record_type)
                )
                dns_data[key] = [str(rdata) for rdata in answers]
            except Exception as e:
                logger.debug(f"DNS {record_type} lookup failed for {domain}: {e}")

        return {'dns': dns_data}

    async def _check_certificate_transparency(self, domain: str) -> Dict[str, Any]:
        """Check certificate transparency logs"""
        try:
            await self.rate_limiter.wait_for_slot('crt_sh')

            url = f"https://crt.sh/?q={domain}&output=json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    certificates = await response.json()

                    processed_certs = []
                    for cert in certificates[:10]:  # Limit to recent 10
                        processed_certs.append({
                            'issuer': cert.get('issuer_name', ''),
                            'subject': cert.get('name_value', ''),
                            'not_before': cert.get('not_before', ''),
                            'not_after': cert.get('not_after', ''),
                            'serial_number': cert.get('serial_number', '')
                        })

                    return {'certificates': processed_certs}
        except Exception as e:
            logger.warning(f"Certificate transparency check failed for {domain}: {e}")

        return {'certificates': []}

    async def _analyze_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Analyze domain reputation across multiple sources"""
        reputation_data = {
            'threat_categories': [],
            'reputation_sources': [],
            'security_vendors': {}
        }

        # Check against threat feeds
        domain_hash = hashlib.md5(domain.encode()).hexdigest()
        if domain_hash in self.intelligence_db:
            threat_info = self.intelligence_db[domain_hash]
            reputation_data['threat_categories'].append(threat_info.get('category', 'unknown'))
            reputation_data['reputation_sources'].extend(threat_info.get('sources', []))

        # Additional reputation checks would go here
        # (VirusTotal, AbuseIPDB, etc. - requires API keys)

        return {'reputation': reputation_data}

    async def _generate_typosquatting_analysis(self, domain: str) -> Dict[str, Any]:
        """Generate and analyze typosquatting variants"""
        variants = self.domain_analyzer.generate_comprehensive_typosquatting_variants(domain)

        # Check each variant for registration
        registered_variants = []
        for variant in variants[:50]:  # Limit to prevent excessive DNS queries
            try:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    lambda d=variant: socket.gethostbyname(d)
                )
                registered_variants.append(variant)
            except socket.gaierror:
                pass  # Domain not registered
            except Exception as e:
                logger.debug(f"Error checking variant {variant}: {e}")

        return {'typosquatting': {'variants': variants, 'registered': registered_variants}}

    async def _check_subdomain_enumeration(self, domain: str) -> Dict[str, Any]:
        """Enumerate subdomains using various techniques"""
        common_subdomains = [
            'www', 'mail', 'ftp', 'admin', 'api', 'dev', 'test', 'staging',
            'blog', 'shop', 'secure', 'login', 'portal', 'support', 'help',
            'docs', 'cdn', 'static', 'assets', 'images', 'files', 'download'
        ]

        found_subdomains = set()

        for subdomain in common_subdomains:
            full_domain = f"{subdomain}.{domain}"
            try:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    lambda d=full_domain: socket.gethostbyname(d)
                )
                found_subdomains.add(full_domain)
            except socket.gaierror:
                pass
            except Exception:
                pass

        return {'subdomains': list(found_subdomains)}

    async def _analyze_domain_infrastructure(self, domain: str) -> Dict[str, Any]:
        """Analyze domain infrastructure and hosting"""
        infrastructure = {
            'hosting_provider': None,
            'ip_addresses': [],
            'geolocation': {},
            'asn_info': {},
            'shared_hosting': []
        }

        try:
            # Get IP addresses
            answers = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: dns.resolver.resolve(domain, 'A')
            )

            ips = [str(rdata) for rdata in answers]
            infrastructure['ip_addresses'] = ips

            # Analyze each IP
            for ip in ips[:3]:  # Limit to first 3 IPs
                geo_data = await self._get_ip_geolocation(ip)
                if geo_data:
                    infrastructure['geolocation'][ip] = geo_data

        except Exception as e:
            logger.debug(f"Infrastructure analysis failed for {domain}: {e}")

        return {'infrastructure': infrastructure}

    async def _get_ip_geolocation(self, ip_address: str) -> Optional[GeolocationData]:
        """Get geolocation data for IP address"""
        try:
            if self.geoip_db_path and Path(self.geoip_db_path).exists():
                # Use local GeoIP database if available
                with geoip2.database.Reader(self.geoip_db_path) as reader:
                    response = reader.city(ip_address)

                    return GeolocationData(
                        ip_address=ip_address,
                        country=response.country.name,
                        country_code=response.country.iso_code,
                        region=response.subdivisions.most_specific.name,
                        city=response.city.name,
                        latitude=float(response.location.latitude) if response.location.latitude else None,
                        longitude=float(response.location.longitude) if response.location.longitude else None,
                        timezone=response.location.time_zone
                    )
            else:
                # Use online geolocation service with rate limiting
                await self.rate_limiter.wait_for_slot('geolocation')

                # Mock implementation - replace with actual service
                return GeolocationData(
                    ip_address=ip_address,
                    country="Unknown",
                    country_code="XX"
                )

        except Exception as e:
            logger.debug(f"Geolocation lookup failed for {ip_address}: {e}")
            return None

    def _merge_domain_intelligence(self, domain_intel: DomainIntelligence, data: Dict[str, Any]) -> None:
        """Merge analysis results into domain intelligence object"""
        if 'whois' in data and data['whois']:
            whois_data = data['whois']
            domain_intel.creation_date = whois_data.get('creation_date')
            domain_intel.expiration_date = whois_data.get('expiration_date')
            domain_intel.registrar = whois_data.get('registrar')
            domain_intel.registrant = whois_data.get('registrant')
            domain_intel.name_servers = whois_data.get('name_servers', [])

        if 'dns' in data:
            dns_data = data['dns']
            domain_intel.a_records = dns_data.get('a_records', [])
            domain_intel.aaaa_records = dns_data.get('aaaa_records', [])
            domain_intel.mx_records = dns_data.get('mx_records', [])
            domain_intel.txt_records = dns_data.get('txt_records', [])

        if 'certificates' in data:
            domain_intel.certificates = data['certificates']

        if 'typosquatting' in data:
            typo_data = data['typosquatting']
            domain_intel.typosquatting_variants = typo_data.get('variants', [])

        if 'subdomains' in data:
            domain_intel.subdomains.update(data['subdomains'])

        if 'reputation' in data:
            rep_data = data['reputation']
            domain_intel.threat_categories = rep_data.get('threat_categories', [])
            domain_intel.intelligence_sources = rep_data.get('reputation_sources', [])

    def _calculate_domain_reputation_score(self, domain_intel: DomainIntelligence) -> float:
        """Calculate comprehensive domain reputation score"""
        score = 0.5  # Neutral starting point

        # Age factor (older domains generally more trustworthy)
        if domain_intel.creation_date:
            domain_age = (datetime.now() - domain_intel.creation_date).days
            age_factor = min(domain_age / 365, 5) * 0.1  # Max 0.5 points for 5+ years
            score += age_factor

        # Threat intelligence factor
        if domain_intel.threat_categories:
            score -= 0.4  # Significant penalty for known threats

        # Certificate factor
        if domain_intel.certificates:
            score += 0.1  # Bonus for having certificates

        # Infrastructure factor
        if domain_intel.a_records:
            score += 0.1  # Bonus for proper DNS setup

        # Typosquatting factor
        if len(domain_intel.typosquatting_variants) > 20:
            score -= 0.1  # Penalty for many variants (potential brand abuse)

        return max(0.0, min(1.0, score))

    async def perform_automated_threat_hunting(self, hunt_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform automated threat hunting based on parameters"""
        return await self.threat_hunter.execute_hunt(hunt_parameters)

    async def correlate_intelligence_sources(self, indicators: List[str]) -> List[IntelligenceCorrelation]:
        """Correlate intelligence across multiple sources"""
        return await self.correlation_engine.correlate_indicators(indicators)

    async def profile_threat_actor(self, actor_indicators: Dict[str, List[str]]) -> ThreatActor:
        """Create comprehensive threat actor profile"""
        return await self.threat_actor_profiler.create_profile(actor_indicators)

    async def track_threat_campaign(self, campaign_data: Dict[str, Any]) -> ThreatCampaign:
        """Track and analyze threat campaign"""
        return await self.campaign_tracker.analyze_campaign(campaign_data)

    async def generate_intelligence_report(self, scope: str, indicators: List[str]) -> Dict[str, Any]:
        """Generate comprehensive intelligence report"""
        report = {
            'report_id': f"intel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'scope': scope,
            'executive_summary': {},
            'detailed_analysis': {},
            'indicators_analyzed': len(indicators),
            'threat_landscape': {},
            'recommendations': [],
            'attribution_analysis': {},
            'campaign_tracking': {},
            'defensive_measures': []
        }

        # Perform analysis based on scope
        if scope == 'domain_intelligence':
            for indicator in indicators:
                if self._is_domain(indicator):
                    analysis = await self.perform_comprehensive_domain_analysis(indicator)
                    report['detailed_analysis'][indicator] = analysis

        elif scope == 'threat_hunting':
            hunt_results = await self.perform_automated_threat_hunting({
                'indicators': indicators,
                'time_range': '30d',
                'threat_types': ['malware', 'phishing', 'c2']
            })
            report['detailed_analysis']['threat_hunt'] = hunt_results

        elif scope == 'attribution':
            correlations = await self.correlate_intelligence_sources(indicators)
            report['attribution_analysis'] = {
                'correlations': correlations,
                'confidence_level': self._calculate_attribution_confidence(correlations)
            }

        # Generate recommendations
        report['recommendations'] = self._generate_defensive_recommendations(report)

        return report

    def _is_domain(self, indicator: str) -> bool:
        """Check if indicator is a domain"""
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_pattern, indicator))

    def _calculate_attribution_confidence(self, correlations: List[IntelligenceCorrelation]) -> float:
        """Calculate attribution confidence based on correlations"""
        if not correlations:
            return 0.0

        total_confidence = sum(corr.confidence_score for corr in correlations)
        return min(1.0, total_confidence / len(correlations))

    def _generate_defensive_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate defensive recommendations based on analysis"""
        recommendations = [
            "Implement comprehensive DNS monitoring for suspicious queries",
            "Deploy threat intelligence feeds to security tools",
            "Configure email security gateways with domain reputation checks",
            "Implement certificate transparency monitoring",
            "Deploy network segmentation and zero-trust architecture"
        ]

        # Add specific recommendations based on findings
        if 'detailed_analysis' in report:
            for indicator, analysis in report['detailed_analysis'].items():
                if isinstance(analysis, DomainIntelligence):
                    if analysis.threat_categories:
                        recommendations.append(f"Block domain {indicator} at DNS and proxy levels")
                    if analysis.typosquatting_variants:
                        recommendations.append(f"Monitor typosquatting variants of {indicator}")

        return recommendations


class IntelligenceCorrelationEngine:
    """Advanced intelligence correlation and fusion engine"""

    def __init__(self):
        self.correlation_algorithms = [
            self._correlate_by_infrastructure,
            self._correlate_by_timing,
            self._correlate_by_behavior_patterns,
            self._correlate_by_geolocation,
            self._correlate_by_campaign_similarity
        ]

    async def correlate_indicators(self, indicators: List[str]) -> List[IntelligenceCorrelation]:
        """Correlate indicators using multiple algorithms"""
        correlations = []

        for algorithm in self.correlation_algorithms:
            try:
                algorithm_correlations = await algorithm(indicators)
                correlations.extend(algorithm_correlations)
            except Exception as e:
                logger.warning(f"Correlation algorithm failed: {e}")

        # Remove duplicates and merge similar correlations
        return self._merge_correlations(correlations)

    async def _correlate_by_infrastructure(self, indicators: List[str]) -> List[IntelligenceCorrelation]:
        """Correlate indicators based on shared infrastructure"""
        correlations = []
        # Implementation would analyze shared IP addresses, ASNs, hosting providers
        return correlations

    async def _correlate_by_timing(self, indicators: List[str]) -> List[IntelligenceCorrelation]:
        """Correlate indicators based on temporal patterns"""
        correlations = []
        # Implementation would analyze creation times, activity patterns
        return correlations

    async def _correlate_by_behavior_patterns(self, indicators: List[str]) -> List[IntelligenceCorrelation]:
        """Correlate indicators based on behavioral similarities"""
        correlations = []
        # Implementation would analyze attack patterns, TTP similarities
        return correlations

    async def _correlate_by_geolocation(self, indicators: List[str]) -> List[IntelligenceCorrelation]:
        """Correlate indicators based on geographic patterns"""
        correlations = []
        # Implementation would analyze geographic clustering
        return correlations

    async def _correlate_by_campaign_similarity(self, indicators: List[str]) -> List[IntelligenceCorrelation]:
        """Correlate indicators based on campaign similarities"""
        correlations = []
        # Implementation would analyze campaign patterns
        return correlations

    def _merge_correlations(self, correlations: List[IntelligenceCorrelation]) -> List[IntelligenceCorrelation]:
        """Merge and deduplicate correlations"""
        # Implementation would merge similar correlations
        return correlations


class AutomatedThreatHunter:
    """Automated threat hunting with ML-powered detection"""

    def __init__(self):
        self.hunt_rules = self._initialize_hunt_rules()
        self.ml_models = {}

    def _initialize_hunt_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize threat hunting rules"""
        return {
            'suspicious_domains': {
                'patterns': [
                    r'.*-[a-z0-9]{8,}\.com$',  # Random string domains
                    r'.*\.tk$|.*\.ml$|.*\.ga$',  # Free TLD abuse
                    r'.*[0-9]{4,}.*\.com$'  # Domains with long numbers
                ],
                'confidence': 0.7
            },
            'dga_domains': {
                'patterns': [
                    r'^[a-z]{8,20}\.com$',  # DGA-like patterns
                    r'^[bcdfghjklmnpqrstvwxyz]{10,}\.net$'  # Consonant-heavy
                ],
                'confidence': 0.8
            },
            'c2_infrastructure': {
                'patterns': [
                    r'.*admin.*\..*',
                    r'.*panel.*\..*',
                    r'.*gate.*\..*'
                ],
                'confidence': 0.6
            }
        }

    async def execute_hunt(self, hunt_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automated threat hunt"""
        results = {
            'hunt_id': f"hunt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'parameters': hunt_parameters,
            'findings': [],
            'statistics': {},
            'recommendations': []
        }

        indicators = hunt_parameters.get('indicators', [])

        for indicator in indicators:
            findings = await self._analyze_indicator(indicator)
            if findings:
                results['findings'].extend(findings)

        results['statistics'] = self._calculate_hunt_statistics(results['findings'])
        results['recommendations'] = self._generate_hunt_recommendations(results['findings'])

        return results

    async def _analyze_indicator(self, indicator: str) -> List[Dict[str, Any]]:
        """Analyze individual indicator against hunt rules"""
        findings = []

        for rule_name, rule_config in self.hunt_rules.items():
            for pattern in rule_config['patterns']:
                if re.match(pattern, indicator, re.IGNORECASE):
                    findings.append({
                        'indicator': indicator,
                        'rule': rule_name,
                        'pattern': pattern,
                        'confidence': rule_config['confidence'],
                        'detected_at': datetime.now().isoformat()
                    })

        return findings

    def _calculate_hunt_statistics(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate hunt statistics"""
        return {
            'total_findings': len(findings),
            'high_confidence': len([f for f in findings if f['confidence'] >= 0.8]),
            'medium_confidence': len([f for f in findings if 0.5 <= f['confidence'] < 0.8]),
            'low_confidence': len([f for f in findings if f['confidence'] < 0.5])
        }

    def _generate_hunt_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on hunt findings"""
        recommendations = []

        if any(f['confidence'] >= 0.8 for f in findings):
            recommendations.append("Immediate investigation required for high-confidence findings")

        if len(findings) > 10:
            recommendations.append("Consider expanding hunt scope to identify campaign")

        return recommendations


class AdvancedDomainAnalyzer:
    """Advanced domain analysis with typosquatting and infrastructure mapping"""

    def __init__(self):
        self.keyboard_layouts = {
            'qwerty': {
                'q': ['w', 'a'], 'w': ['q', 'e', 's'], 'e': ['w', 'r', 'd'],
                'r': ['e', 't', 'f'], 't': ['r', 'y', 'g'], 'y': ['t', 'u', 'h'],
                'u': ['y', 'i', 'j'], 'i': ['u', 'o', 'k'], 'o': ['i', 'p', 'l'],
                'p': ['o', 'l'], 'a': ['q', 's', 'z'], 's': ['a', 'w', 'd', 'x'],
                'd': ['s', 'e', 'f', 'c'], 'f': ['d', 'r', 'g', 'v'],
                'g': ['f', 't', 'h', 'b'], 'h': ['g', 'y', 'j', 'n'],
                'j': ['h', 'u', 'k', 'm'], 'k': ['j', 'i', 'l'],
                'l': ['k', 'o', 'p'], 'z': ['a', 's', 'x'], 'x': ['z', 's', 'd', 'c'],
                'c': ['x', 'd', 'f', 'v'], 'v': ['c', 'f', 'g', 'b'],
                'b': ['v', 'g', 'h', 'n'], 'n': ['b', 'h', 'j', 'm'],
                'm': ['n', 'j', 'k']
            }
        }

    def generate_comprehensive_typosquatting_variants(self, domain: str) -> List[str]:
        """Generate comprehensive typosquatting variants"""
        if '.' not in domain:
            return []

        name, tld = domain.rsplit('.', 1)
        variants = set()

        # Character substitution
        variants.update(self._generate_substitution_variants(name, tld))

        # Character insertion
        variants.update(self._generate_insertion_variants(name, tld))

        # Character deletion
        variants.update(self._generate_deletion_variants(name, tld))

        # Character transposition
        variants.update(self._generate_transposition_variants(name, tld))

        # Keyboard proximity errors
        variants.update(self._generate_keyboard_variants(name, tld))

        # Homograph attacks
        variants.update(self._generate_homograph_variants(name, tld))

        # TLD variations
        variants.update(self._generate_tld_variants(name, domain))

        return list(variants)[:100]  # Limit to 100 variants

    def _generate_substitution_variants(self, name: str, tld: str) -> Set[str]:
        """Generate character substitution variants"""
        variants = set()
        substitutions = {
            'a': ['4', '@', 'e'], 'e': ['3', 'a'], 'i': ['1', '!', 'l'],
            'o': ['0', 'u'], 's': ['5', '$'], 't': ['7'], 'g': ['9'],
            'l': ['1', 'i'], 'b': ['6'], 'z': ['2']
        }

        for i, char in enumerate(name.lower()):
            if char in substitutions:
                for sub in substitutions[char]:
                    variant = name[:i] + sub + name[i+1:] + '.' + tld
                    variants.add(variant.lower())

        return variants

    def _generate_insertion_variants(self, name: str, tld: str) -> Set[str]:
        """Generate character insertion variants"""
        variants = set()
        common_insertions = ['1', 'a', 'e', 'i', 'o', 'u', 's', 't', 'n', 'r']

        for i in range(len(name) + 1):
            for char in common_insertions:
                variant = name[:i] + char + name[i:] + '.' + tld
                variants.add(variant.lower())

        return variants

    def _generate_deletion_variants(self, name: str, tld: str) -> Set[str]:
        """Generate character deletion variants"""
        variants = set()

        for i in range(len(name)):
            if len(name) > 3:  # Don't make domain too short
                variant = name[:i] + name[i+1:] + '.' + tld
                variants.add(variant.lower())

        return variants

    def _generate_transposition_variants(self, name: str, tld: str) -> Set[str]:
        """Generate character transposition variants"""
        variants = set()

        for i in range(len(name) - 1):
            chars = list(name)
            chars[i], chars[i+1] = chars[i+1], chars[i]
            variant = ''.join(chars) + '.' + tld
            variants.add(variant.lower())

        return variants

    def _generate_keyboard_variants(self, name: str, tld: str) -> Set[str]:
        """Generate keyboard proximity error variants"""
        variants = set()
        keyboard = self.keyboard_layouts['qwerty']

        for i, char in enumerate(name.lower()):
            if char in keyboard:
                for adjacent in keyboard[char]:
                    variant = name[:i] + adjacent + name[i+1:] + '.' + tld
                    variants.add(variant.lower())

        return variants

    def _generate_homograph_variants(self, name: str, tld: str) -> Set[str]:
        """Generate homograph attack variants"""
        variants = set()
        homographs = {
            'a': ['а'], 'c': ['с'], 'e': ['е'], 'o': ['о'],
            'p': ['р'], 'x': ['х'], 'y': ['у']
        }

        for i, char in enumerate(name.lower()):
            if char in homographs:
                for homograph in homographs[char]:
                    variant = name[:i] + homograph + name[i+1:] + '.' + tld
                    variants.add(variant)

        return variants

    def _generate_tld_variants(self, name: str, original_domain: str) -> Set[str]:
        """Generate TLD variation variants"""
        variants = set()
        common_tlds = [
            'com', 'net', 'org', 'info', 'biz', 'us', 'co.uk', 'de',
            'ru', 'cn', 'tk', 'ml', 'ga', 'cf'
        ]

        for tld in common_tlds:
            variant = name + '.' + tld
            if variant != original_domain:
                variants.add(variant.lower())

        return variants


class ThreatActorProfiler:
    """Advanced threat actor profiling and attribution"""

    def __init__(self):
        self.profiling_techniques = [
            self._analyze_infrastructure_patterns,
            self._analyze_temporal_patterns,
            self._analyze_language_patterns,
            self._analyze_technical_capabilities,
            self._analyze_target_selection
        ]

    async def create_profile(self, actor_indicators: Dict[str, List[str]]) -> ThreatActor:
        """Create comprehensive threat actor profile"""
        actor_id = f"actor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        profile = ThreatActor(
            actor_id=actor_id,
            first_observed=datetime.now(),
            last_observed=datetime.now()
        )

        # Apply profiling techniques
        for technique in self.profiling_techniques:
            try:
                await technique(profile, actor_indicators)
            except Exception as e:
                logger.warning(f"Profiling technique failed: {e}")

        # Calculate attribution confidence
        profile.attribution_confidence = self._calculate_attribution_confidence(profile)

        return profile

    async def _analyze_infrastructure_patterns(self, profile: ThreatActor, indicators: Dict[str, List[str]]) -> None:
        """Analyze infrastructure usage patterns"""
        # Analyze hosting providers, IP ranges, domain patterns
        pass

    async def _analyze_temporal_patterns(self, profile: ThreatActor, indicators: Dict[str, List[str]]) -> None:
        """Analyze temporal activity patterns"""
        # Analyze activity times, campaign durations
        pass

    async def _analyze_language_patterns(self, profile: ThreatActor, indicators: Dict[str, List[str]]) -> None:
        """Analyze language and communication patterns"""
        # Analyze language usage, writing patterns in communications
        pass

    async def _analyze_technical_capabilities(self, profile: ThreatActor, indicators: Dict[str, List[str]]) -> None:
        """Analyze technical capabilities and sophistication"""
        # Analyze malware complexity, exploitation techniques
        pass

    async def _analyze_target_selection(self, profile: ThreatActor, indicators: Dict[str, List[str]]) -> None:
        """Analyze target selection patterns"""
        # Analyze victim demographics, industry targeting
        pass

    def _calculate_attribution_confidence(self, profile: ThreatActor) -> float:
        """Calculate attribution confidence based on profile completeness"""
        confidence_factors = []

        if profile.infrastructure:
            confidence_factors.append(0.2)
        if profile.attack_vectors:
            confidence_factors.append(0.2)
        if profile.target_sectors:
            confidence_factors.append(0.15)
        if profile.geographic_focus:
            confidence_factors.append(0.15)
        if profile.associated_malware:
            confidence_factors.append(0.2)
        if profile.campaigns:
            confidence_factors.append(0.1)

        return sum(confidence_factors)


class CampaignTracker:
    """Threat campaign tracking and analysis"""

    def __init__(self):
        self.active_campaigns = {}
        self.campaign_patterns = {}

    async def analyze_campaign(self, campaign_data: Dict[str, Any]) -> ThreatCampaign:
        """Analyze and track threat campaign"""
        campaign_id = campaign_data.get('campaign_id', f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        campaign = ThreatCampaign(
            campaign_id=campaign_id,
            name=campaign_data.get('name'),
            start_date=datetime.now()
        )

        # Analyze campaign characteristics
        campaign.indicators = campaign_data.get('indicators', {})
        campaign.target_countries = campaign_data.get('target_countries', [])
        campaign.target_sectors = campaign_data.get('target_sectors', [])
        campaign.malware_families = campaign_data.get('malware_families', [])

        self.active_campaigns[campaign_id] = campaign

        return campaign


class MLIntelligenceProcessor:
    """Machine learning powered intelligence processing"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.clustering_model = DBSCAN(eps=0.3, min_samples=2)
        self.models_trained = False

    async def process_text_intelligence(self, texts: List[str]) -> Dict[str, Any]:
        """Process text-based intelligence using NLP"""
        if not texts:
            return {'clusters': [], 'sentiment': [], 'keywords': []}

        # Sentiment analysis
        sentiment_scores = []
        for text in texts:
            scores = SentimentIntensityAnalyzer().polarity_scores(text)
            sentiment_scores.append(scores)

        # Text clustering
        try:
            text_vectors = self.vectorizer.fit_transform(texts)
            clusters = self.clustering_model.fit_predict(text_vectors)

            cluster_info = {}
            for i, cluster_id in enumerate(clusters):
                if cluster_id not in cluster_info:
                    cluster_info[cluster_id] = []
                cluster_info[cluster_id].append(i)

        except Exception as e:
            logger.warning(f"Text clustering failed: {e}")
            cluster_info = {}

        # Keyword extraction
        keywords = self._extract_keywords(texts)

        return {
            'clusters': cluster_info,
            'sentiment': sentiment_scores,
            'keywords': keywords
        }

    def _extract_keywords(self, texts: List[str]) -> List[str]:
        """Extract important keywords from texts"""
        all_text = ' '.join(texts)
        tokens = word_tokenize(all_text.lower())

        # Remove stopwords and short words
        stop_words = set(stopwords.words('english'))
        keywords = [word for word in tokens if word.isalpha() and len(word) > 3 and word not in stop_words]

        # Get most common keywords
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(20)]


# Export main class
__all__ = ['AdvancedOSINTAutomation']