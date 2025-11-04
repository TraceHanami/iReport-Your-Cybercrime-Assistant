import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os
import pandas as pd
from datetime import datetime

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class CrimeClassifier:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000, 
                stop_words='english', 
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.8
            )),
            ('classifier', MultinomialNB())
        ])
        self.is_trained = False
        
        # Comprehensive crime categories with 150+ keywords each
        self.crime_categories = {
            # Violent Crimes (150+ keywords) - Previous category remains
            'violent_crime': [
                'assault', 'attack', 'battery', 'violence', 'physical harm', 'beating', 'hitting', 'punching',
                'kicking', 'stabbing', 'shooting', 'strangling', 'choking', 'throttling', 'maiming', 'wounding',
                'injuring', 'hurt', 'harm', 'brutality', 'force', 'coercion', 'intimidation', 'threat', 'menace',
                'terror', 'fear', 'danger', 'peril', 'risk', 'hazard', 'jeopardy', 'menacing', 'bullying',
                'harassment', 'molestation', 'abuse', 'mistreatment', 'torture', 'torment', 'persecution',
                'oppression', 'aggression', 'hostility', 'belligerence', 'combat', 'fight', 'brawl', 'clash',
                'conflict', 'struggle', 'scuffle', 'tussle', 'fracas', 'melee', 'riot', 'disturbance', 'uproar',
                'commotion', 'turmoil', 'unrest', 'violence', 'force', 'coercion', 'compulsion', 'duress',
                'pressure', 'constraint', 'restraint', 'confinement', 'detention', 'captivity', 'imprisonment',
                'incarceration', 'jailing', 'locking', 'caging', 'ensnaring', 'trapping', 'snaring', 'netting',
                'entrapping', 'ambushing', 'waylaying', 'bushwhacking', 'surprising', 'startling', 'shocking',
                'alarming', 'frightening', 'terrifying', 'petrifying', 'horrifying', 'traumatizing', 'scarring',
                'damaging', 'harming', 'hurting', 'injuring', 'wounding', 'maiming', 'disfiguring', 'crippling',
                'disabling', 'incapacitating', 'weakening', 'enfeebling', 'debilitating', 'exhausting', 'fatiguing',
                'tiring', 'wearying', 'draining', 'sapping', 'enervating', 'devitalizing', 'weakening', 'undermining',
                'sabotaging', 'subverting', 'undercutting', 'weakening', 'compromising', 'jeopardizing', 'endangering',
                'imperiling', 'risking', 'hazarding', 'gambling', 'betting', 'wagering', 'staking', 'venturing'
            ],
            
            # Theft & Robbery (150+ keywords) - Previous category remains
            'theft_robbery': [
                'theft', 'stealing', 'robbery', 'burglary', 'larceny', 'pilfering', 'filching', 'purloining',
                'embezzlement', 'misappropriation', 'defalcation', 'peculation', 'swindling', 'fleecing', 'bilking',
                'cheating', 'defrauding', 'duping', 'hoodwinking', 'bamboo zling', 'gulling', 'tricking', 'deceiving',
                'deluding', 'misleading', 'misinforming', 'misdirecting', 'misguiding', 'misleading', 'beguiling',
                'entrapping', 'ensnaring', 'trapping', 'snaring', 'netting', 'catching', 'capturing', 'seizing',
                'grabbing', 'snatching', 'wresting', 'wrenching', 'prying', 'forcing', 'compelling', 'coercing',
                'pressuring', 'constraining', 'restraining', 'confining', 'detaining', 'imprisoning', 'jailing',
                'locking', 'caging', 'enslaving', 'subjugating', 'dominating', 'controlling', 'mastering', 'ruling',
                'governing', 'commanding', 'directing', 'managing', 'supervising', 'overseeing', 'monitoring',
                'watching', 'observing', 'scrutinizing', 'examining', 'inspecting', 'checking', 'verifying',
                'confirming', 'validating', 'authenticating', 'certifying', 'attesting', 'witnessing', 'testifying',
                'swearing', 'affirming', 'declaring', 'stating', 'asserting', 'claiming', 'alleging', 'contending',
                'maintaining', 'insisting', 'persisting', 'persevering', 'continuing', 'enduring', 'lasting',
                'surviving', 'persisting', 'remaining', 'staying', 'lingering', 'abiding', 'dwelling', 'residing',
                'inhabiting', 'occupying', 'possessing', 'holding', 'owning', 'having', 'keeping', 'retaining',
                'preserving', 'conserving', 'saving', 'protecting', 'guarding', 'defending', 'shielding', 'sheltering'

            ],
            
            # CYBER CRIMES - EXPANDED SECTION
            'cyber_attack': [
                'hacking', 'cyber attack', 'malware', 'virus', 'trojan', 'ransomware', 'spyware', 'adware',
                'keylogger', 'botnet', 'ddos attack', 'dos attack', 'sql injection', 'xss', 'cross site scripting',
                'csrf', 'clickjacking', 'session hijacking', 'cookie theft', 'password cracking', 'brute force',
                'zero day exploit', 'remote code execution', 'privilege escalation', 'backdoor', 'rootkit',
                'bootkit', 'firmware attack', 'bios attack', 'uefi attack', 'supply chain attack', 'apt attack',
                'advanced persistent threat', 'nation state attack', 'cyber warfare', 'digital warfare',
                'information warfare', 'network warfare', 'computer network attack', 'cyber espionage',
                'digital espionage', 'corporate espionage', 'industrial espionage', 'economic espionage',
                'state sponsored hacking', 'hacktivism', 'cyber terrorism', 'digital terrorism', 'online terrorism',
                'critical infrastructure attack', 'scada attack', 'ics attack', 'industrial control system',
                'power grid attack', 'water system attack', 'transportation system attack', 'healthcare system attack',
                'financial system attack', 'banking system attack', 'stock market attack', 'trading platform attack',
                'cryptocurrency attack', 'blockchain attack', 'smart contract exploit', 'defi attack',
                'decentralized finance hack', 'nft theft', 'digital asset theft', 'wallet hacking', 'exchange hack',
                'mining pool attack', 'staking pool attack', 'governance attack', 'dao attack', 'oracle manipulation',
                'price feed manipulation', 'flash loan attack', 'impermanent loss exploit', 'yield farming exploit',
                'liquidity pool drain', 'rug pull', 'exit scam', 'ponzi scheme', 'pyramid scheme', 'investment scam',
                'cloud infrastructure attack', 'aws attack', 'azure attack', 'google cloud attack', 'cloudflare attack',
                'cdn attack', 'dns attack', 'domain hijacking', 'dns poisoning', 'dns spoofing', 'arp spoofing',
                'ip spoofing', 'mac spoofing', 'vlan hopping', 'switch attack', 'router attack', 'firewall bypass',
                'vpn attack', 'proxy attack', 'tor compromise', 'anonymity network attack', 'privacy tool compromise',
                'encryption bypass', 'crypto attack', 'quantum computing attack', 'post quantum cryptography',
                'ai system attack', 'machine learning poisoning', 'training data manipulation', 'model inversion',
                'membership inference', 'model stealing', 'adversarial attack', 'deepfake creation', 'synthetic media',
                'voice cloning', 'image manipulation', 'video manipulation', 'media forgery', 'digital tampering'
            ],
            
            'online_fraud': [
                'phishing', 'spear phishing', 'whaling', 'vishing', 'smishing', 'pharming', 'typosquatting',
                'domain spoofing', 'email spoofing', 'website spoofing', 'login page spoofing', 'payment page spoofing',
                'banking page spoofing', 'social media spoofing', 'profile cloning', 'identity cloning', 'catfishing',
                'romance scam', 'dating scam', 'marriage scam', 'inheritance scam', 'lottery scam', 'prize scam',
                'sweepstakes scam', 'grant scam', 'scholarship scam', 'job offer scam', 'employment scam',
                'work from home scam', 'remote job scam', 'fake check scam', 'overpayment scam', 'advance fee scam',
                '419 scam', 'nigerian prince scam', 'money transfer scam', 'wire transfer scam', 'western union scam',
                'moneygram scam', 'paypal scam', 'venmo scam', 'cashapp scam', 'zelle scam', 'cryptocurrency scam',
                'bitcoin scam', 'ether scam', 'altcoin scam', 'initial coin offering scam', 'ico scam', 'sto scam',
                'security token offering scam', 'nft scam', 'digital art scam', 'virtual real estate scam',
                'metaverse scam', 'virtual world scam', 'online gaming scam', 'virtual item scam', 'skin gambling',
                'loot box scam', 'in game purchase scam', 'mobile game scam', 'app store scam', 'google play scam',
                'subscription scam', 'recurring billing scam', 'free trial scam', 'negative option scam',
                'automatic renewal scam', 'membership scam', 'premium service scam', 'exclusive access scam',
                'early bird scam', 'limited time offer scam', 'countdown timer scam', 'fake urgency scam',
                'artificial scarcity scam', 'fake discount scam', 'coupon scam', 'voucher scam', 'promo code scam',
                'referral scam', 'multi level marketing scam', 'network marketing scam', 'affiliate marketing scam',
                'dropshipping scam', 'ecommerce scam', 'online store scam', 'marketplace scam', 'amazon scam',
                'ebay scam', 'etsy scam', 'shopify scam', 'woocommerce scam', 'fake website scam', 'counterfeit goods',
                'replica products', 'fake reviews', 'review manipulation', 'astroturfing', 'sockpuppeting',
                'fake accounts', 'bot accounts', 'sybil attack', 'coordination scam', 'collusion scam', 'price fixing',
                'bid rigging', 'auction manipulation', 'shill bidding', 'bid shielding', 'search engine manipulation',
                'seo spam', 'black hat seo', 'keyword stuffing', 'link farming', 'link scheme', 'google bombing',
                'search result manipulation', 'fake news', 'misinformation', 'disinformation', 'propaganda',
                'conspiracy theory', 'fake science', 'pseudoscience', 'health misinformation', 'medical misinformation',
                'vaccine misinformation', 'political misinformation', 'election interference', 'voter suppression',
                'digital gerrymandering', 'social media manipulation', 'trend manipulation', 'hashtag hijacking',
                'twitter bombing', 'facebook manipulation', 'instagram manipulation', 'tiktok manipulation'
            ],
            
            'identity_theft': [
                'identity theft', 'identity fraud', 'personal information theft', 'data theft', 'information theft',
                'credit card theft', 'debit card theft', 'bank account theft', 'financial identity theft',
                'tax identity theft', 'government benefits theft', 'social security theft', 'national id theft',
                'passport theft', 'driving license theft', 'health insurance theft', 'medical identity theft',
                'synthetic identity theft', 'child identity theft', 'deceased identity theft', 'criminal identity theft',
                'character identity theft', 'reputation theft', 'digital identity theft', 'online identity theft',
                'social media identity theft', 'email account theft', 'cloud account theft', 'apple id theft',
                'google account theft', 'microsoft account theft', 'facebook account theft', 'instagram account theft',
                'twitter account theft', 'linkedin account theft', 'gaming account theft', 'steam account theft',
                'epic games account theft', 'playstation network theft', 'xbox live theft', 'nintendo account theft',
                'crypto wallet theft', 'exchange account theft', 'mining account theft', 'staking account theft',
                'domain name theft', 'website theft', 'blog theft', 'content theft', 'intellectual property theft',
                'copyright theft', 'patent theft', 'trademark theft', 'trade secret theft', 'business idea theft',
                'research data theft', 'academic work theft', 'thesis theft', 'dissertation theft', 'publication theft',
                'personal data breach', 'information leak', 'data exposure', 'privacy breach', 'confidentiality breach',
                'security breach', 'unauthorized access', 'illegal access', 'system intrusion', 'account takeover',
                'profile takeover', 'page takeover', 'group takeover', 'community takeover', 'forum takeover',
                'website takeover', 'domain takeover', 'dns takeover', 'subdomain takeover', 'cloud takeover',
                'server takeover', 'database takeover', 'backup theft', 'archive theft', 'historical data theft',
                'biometric data theft', 'fingerprint theft', 'facial recognition theft', 'voice print theft',
                'dna data theft', 'genetic information theft', 'health data theft', 'medical record theft',
                'prescription theft', 'insurance claim theft', 'benefits claim theft', 'pension theft',
                'retirement account theft', 'investment account theft', 'brokerage account theft', 'trading account theft',
                'forex account theft', 'commodity account theft', 'derivatives account theft', 'futures account theft',
                'options account theft', 'mutual fund theft', 'etf theft', 'bond theft', 'stock theft',
                'security theft', 'financial instrument theft', 'banking instrument theft', 'monetary instrument theft'
            ],
            
            'data_breach': [
                'data breach', 'information breach', 'security breach', 'privacy breach', 'confidentiality breach',
                'database breach', 'server breach', 'cloud breach', 'network breach', 'system breach',
                'application breach', 'website breach', 'mobile app breach', 'desktop app breach', 'api breach',
                'endpoint breach', 'gateway breach', 'firewall breach', 'vpn breach', 'proxy breach',
                'authentication breach', 'authorization breach', 'access control breach', 'permission breach',
                'privilege breach', 'role breach', 'policy breach', 'rule breach', 'regulation breach',
                'compliance breach', 'standard breach', 'protocol breach', 'specification breach', 'requirement breach',
                'customer data breach', 'user data breach', 'client data breach', 'patient data breach',
                'student data breach', 'employee data breach', 'member data breach', 'subscriber data breach',
                'donor data breach', 'volunteer data breach', 'partner data breach', 'vendor data breach',
                'supplier data breach', 'contractor data breach', 'consultant data breach', 'advisor data breach',
                'personal information breach', 'sensitive information breach', 'confidential information breach',
                'proprietary information breach', 'trade secret breach', 'intellectual property breach',
                'financial information breach', 'banking information breach', 'credit information breach',
                'tax information breach', 'health information breach', 'medical information breach',
                'genetic information breach', 'biometric information breach', 'location information breach',
                'behavioral information breach', 'preference information breach', 'interest information breach',
                'purchase history breach', 'browsing history breach', 'search history breach', 'viewing history breach',
                'listening history breach', 'reading history breach', 'communication history breach',
                'social media activity breach', 'online activity breach', 'digital footprint breach',
                'metadata breach', 'log data breach', 'analytics data breach', 'metrics data breach',
                'statistics breach', 'research data breach', 'survey data breach', 'poll data breach',
                'questionnaire data breach', 'form data breach', 'application data breach', 'registration data breach',
                'enrollment data breach', 'subscription data breach', 'membership data breach', 'loyalty data breach'
            ],
            
            'crypto_crime': [
                'cryptocurrency crime', 'bitcoin crime', 'ether crime', 'altcoin crime', 'blockchain crime',
                'digital currency crime', 'virtual currency crime', 'crypto fraud', 'bitcoin fraud', 'ether fraud',
                'altcoin fraud', 'ico fraud', 'initial coin offering fraud', 'sto fraud', 'security token offering fraud',
                'nft fraud', 'non fungible token fraud', 'digital art fraud', 'virtual asset fraud', 'token fraud',
                'coin fraud', 'stablecoin fraud', 'algorithmic stablecoin fraud', 'collateralized stablecoin fraud',
                'defi fraud', 'decentralized finance fraud', 'yield farming fraud', 'liquidity mining fraud',
                'staking fraud', 'governance fraud', 'dao fraud', 'decentralized autonomous organization fraud',
                'smart contract fraud', 'oracle fraud', 'bridge fraud', 'cross chain fraud', 'layer 2 fraud',
                'sidechain fraud', 'rollup fraud', 'zk rollup fraud', 'optimistic rollup fraud', 'plasma fraud',
                'state channel fraud', 'payment channel fraud', 'lightning network fraud', 'atomic swap fraud',
                'flash loan fraud', 'impermanent loss fraud', 'rug pull', 'exit scam', 'pump and dump',
                'wash trading', 'spoofing', 'front running', 'back running', 'sandwich attack', 'time bandit attack',
                'miner extractable value', 'mev attack', 'validator extractable value', 'vev attack',
                'sequencer extractable value', 'sev attack', 'proposer extractable value', 'pev attack',
                'crypto theft', 'bitcoin theft', 'ether theft', 'altcoin theft', 'wallet theft', 'hot wallet theft',
                'cold wallet theft', 'hardware wallet theft', 'paper wallet theft', 'brain wallet theft',
                'seed phrase theft', 'private key theft', 'public key theft', 'address theft', 'transaction theft',
                'block theft', 'chain theft', 'network theft', 'protocol theft', 'fork theft', 'airdrop theft',
                'bounty theft', 'reward theft', 'incentive theft', 'subsidy theft', 'grant theft', 'funding theft',
                'investment theft', 'donation theft', 'contribution theft', 'participation theft', 'engagement theft',
                'mining theft', 'staking theft', 'validation theft', 'verification theft', 'confirmation theft',
                'finality theft', 'settlement theft', 'clearing theft', 'custody theft', 'storage theft',
                'exchange theft', 'trading theft', 'liquidity theft', 'market making theft', 'arbitrage theft',
                'speculation theft', 'hedging theft', 'insurance theft', 'derivatives theft', 'futures theft',
                'options theft', 'swaps theft', 'forwards theft', 'perpetuals theft', 'margin trading theft',
                'leverage trading theft', 'short selling theft', 'long position theft', 'short position theft'
            ],
            
            'social_media_crime': [
                'social media crime', 'facebook crime', 'instagram crime', 'twitter crime', 'tiktok crime',
                'linkedin crime', 'youtube crime', 'whatsapp crime', 'telegram crime', 'signal crime',
                'discord crime', 'reddit crime', 'pinterest crime', 'snapchat crime', 'wechat crime',
                'line crime', 'kakao crime', 'viber crime', 'imo crime', 'zoom crime', 'teams crime',
                'slack crime', 'microsoft teams crime', 'google meet crime', 'skype crime', 'facetime crime',
                'profile hacking', 'account takeover', 'page takeover', 'group takeover', 'community takeover',
                'fake profile', 'impersonation', 'identity theft', 'catfishing', 'romance scam', 'dating scam',
                'friendship scam', 'family emergency scam', 'grandparent scam', 'relative in trouble scam',
                'stranded traveler scam', 'virtual kidnapping scam', 'fake emergency scam', 'urgent help scam',
                'financial assistance scam', 'money transfer scam', 'gift card scam', 'prepaid card scam',
                'reloadable card scam', 'store card scam', 'brand voucher scam', 'online coupon scam',
                'promotional code scam', 'discount voucher scam', 'membership scam', 'subscription scam',
                'premium access scam', 'exclusive content scam', 'private group scam', 'secret community scam',
                'elite membership scam', 'vip access scam', 'early access scam', 'beta testing scam',
                'product testing scam', 'review scam', 'feedback scam', 'survey scam', 'poll scam',
                'questionnaire scam', 'research study scam', 'academic survey scam', 'market research scam',
                'focus group scam', 'user testing scam', 'quality assurance scam', 'bug bounty scam',
                'security testing scam', 'penetration testing scam', 'vulnerability assessment scam',
                'compliance audit scam', 'regulatory review scam', 'legal compliance scam', 'tax compliance scam',
                'financial compliance scam', 'banking compliance scam', 'anti money laundering scam',
                'counter terrorism financing scam', 'sanctions compliance scam', 'export control scam',
                'trade compliance scam', 'environmental compliance scam', 'health safety compliance scam',
                'data protection compliance scam', 'privacy compliance scam', 'gdpr compliance scam',
                'ccpa compliance scam', 'hipaa compliance scam', 'pci dss compliance scam', 'sox compliance scam'
            ],
            
            'dark_web_crime': [
                'dark web crime', 'deep web crime', 'tor network crime', 'i2p crime', 'freenet crime',
                'zero net crime', 'loki net crime', 'monero crime', 'zcash crime', 'dash crime',
                'privacy coin crime', 'anonymous cryptocurrency crime', 'untraceable transaction crime',
                'coin mixing crime', 'coin tumbling crime', 'chain analysis evasion', 'transaction obfuscation',
                'privacy protocol crime', 'stealth address crime', 'ring signature crime', 'zk snark crime',
                'zk stark crime', 'bulletproof crime', 'mimblewimble crime', 'confidential transaction crime',
                'illegal marketplace', 'darknet market', 'hidden service market', 'tor hidden service',
                'i2p hidden service', 'freenet hidden service', 'drug marketplace', 'weapons marketplace',
                'stolen data marketplace', 'hacking tools marketplace', 'malware marketplace', 'exploit marketplace',
                'zero day marketplace', 'vulnerability marketplace', 'botnet marketplace', 'ddos service marketplace',
                'hacking service marketplace', 'social engineering service', 'phishing kit marketplace',
                'spam service marketplace', 'fake id marketplace', 'forged document marketplace',
                'counterfeit currency marketplace', 'fake passport marketplace', 'fake driving license marketplace',
                'fake degree marketplace', 'fake certificate marketplace', 'fake license marketplace',
                'fake permit marketplace', 'fake authorization marketplace', 'illegal content distribution',
                'child exploitation material', 'terrorist content', 'extremist content', 'hate speech content',
                'incitement to violence', 'radicalization content', 'recruitment content', 'propaganda content',
                'instructional content', 'tutorial content', 'guide content', 'manual content', 'handbook content',
                'textbook content', 'reference content', 'encyclopedia content', 'database content',
                'archive content', 'library content', 'repository content', 'collection content', 'compilation content',
                'anthology content', 'omnibus content', 'treasury content', 'miscellany content', 'assortment content',
                'variety content', 'selection content', 'choice content', 'pick content', 'option content',
                'alternative content', 'substitute content', 'replacement content', 'surrogate content',
                'proxy content', 'stand in content', 'understudy content', 'double content', 'clone content'
            ],

             # Cyber Crimes (150+ keywords)
            'cyber_crime': [
                'hacking', 'cyber attack', 'phishing', 'malware', 'virus', 'trojan', 'ransomware', 'spyware',
                'adware', 'keylogger', 'botnet', 'ddos', 'dos attack', 'sql injection', 'xss', 'cross site scripting',
                'csrf', 'clickjacking', 'session hijacking', 'cookie theft', 'password cracking', 'brute force',
                'social engineering', 'pretexting', 'baiting', 'quid pro quo', 'tailgating', 'impersonation',
                'identity theft', 'credit card fraud', 'bank fraud', 'online scam', 'internet fraud', 'web fraud',
                'digital fraud', 'electronic fraud', 'computer fraud', 'network intrusion', 'system breach',
                'data breach', 'information theft', 'data theft', 'privacy violation', 'confidentiality breach',
                'security breach', 'unauthorized access', 'illegal access', 'system compromise', 'network compromise',
                'server compromise', 'website defacement', 'domain hijacking', 'dns poisoning', 'arp spoofing',
                'ip spoofing', 'email spoofing', 'caller id spoofing', 'sms spoofing', 'voip hacking', 'pbx hacking',
                'voicemail hacking', 'sim swapping', 'port out scam', 'account takeover', 'profile hacking',
                'social media hacking', 'facebook hacking', 'instagram hacking', 'twitter hacking', 'linkedin hacking',
                'whatsapp hacking', 'telegram hacking', 'signal hacking', 'email hacking', 'gmail hacking',
                'outlook hacking', 'yahoo hacking', 'password reset', 'account recovery', 'two factor bypass',
                'authentication bypass', 'authorization bypass', 'privilege escalation', 'root access', 'admin access',
                'system access', 'network access', 'database access', 'file access', 'document access', 'record access',
                'information access', 'data access', 'cloud hacking', 'aws hacking', 'azure hacking', 'google cloud',
                'serverless hacking', 'container escape', 'kubernetes hacking', 'docker escape', 'virtual machine',
                'hypervisor escape', 'firmware hacking', 'bios hacking', 'uefi hacking', 'hardware hacking',
                'iot hacking', 'smart device hacking', 'camera hacking', 'router hacking', 'modem hacking',
                'switch hacking', 'firewall bypass', 'vpn hacking', 'proxy hacking', 'tor compromise'
            ],
            
            # Financial Crimes (150+ keywords)
            'financial_crime': [
                'fraud', 'scam', 'financial fraud', 'bank fraud', 'credit fraud', 'debit fraud', 'card fraud',
                'check fraud', 'wire fraud', 'securities fraud', 'investment fraud', 'stock fraud', 'bond fraud',
                'mutual fund fraud', 'insurance fraud', 'health insurance fraud', 'auto insurance fraud',
                'home insurance fraud', 'life insurance fraud', 'tax fraud', 'income tax fraud', 'sales tax fraud',
                'vat fraud', 'gst fraud', 'customs fraud', 'duty evasion', 'tax evasion', 'money laundering',
                'terror financing', 'hawala', 'underground banking', 'parallel banking', 'informal value transfer',
                'structured transactions', 'smurfing', 'placement layering integration', 'shell companies',
                'offshore accounts', 'tax havens', 'beneficial ownership', 'nominee directors', 'bearer shares',
                'anonymous corporations', 'trust misuse', 'foundation abuse', 'charity fraud', 'nonprofit fraud',
                'ngo fraud', 'religious organization fraud', 'educational institution fraud', 'hospital fraud',
                'medical fraud', 'healthcare fraud', 'medicare fraud', 'medicaid fraud', 'pharmaceutical fraud',
                'drug fraud', 'clinical trial fraud', 'research fraud', 'academic fraud', 'scientific fraud',
                'publication fraud', 'plagiarism', 'copyright infringement', 'patent infringement', 'trademark',
                'intellectual property theft', 'trade secret theft', 'industrial espionage', 'corporate espionage',
                'economic espionage', 'business intelligence theft', 'market research theft', 'customer data theft',
                'supplier data theft', 'competitor information', 'bid rigging', 'price fixing', 'market allocation',
                'group boycott', 'tying arrangement', 'exclusive dealing', 'predatory pricing', 'price discrimination',
                'deceptive pricing', 'bait and switch', 'false advertising', 'misleading claims', 'exaggerated benefits',
                'hidden fees', 'undisclosed charges', 'unauthorized billing', 'cramming', 'slamming', 'negative option',
                'automatic renewal', 'subscription trap', 'free trial scam', 'pyramid scheme', 'ponzi scheme',
                'multi level marketing', 'chain referral', 'matrix program', 'gifting circle', 'investment club',
                'forex scam', 'binary options', 'cryptocurrency scam', 'bitcoin fraud', 'ether fraud', 'ico fraud',
                'nft fraud', 'metaverse scam', 'virtual world fraud', 'online gaming fraud', 'virtual currency'
            ],
            
            # Missing Persons (150+ keywords)
            'missing_person': [
                'missing', 'disappeared', 'vanished', 'lost contact', 'not found', 'cannot locate', 'whereabouts unknown',
                'last seen', 'last location', 'final sighting', 'recent contact', 'phone disconnected', 'social media inactive',
                'unreachable', 'unresponsive', 'no response', 'silent', 'quiet', 'absent', 'away', 'gone', 'departed',
                'left', 'vacated', 'evacuated', 'withdrawn', 'retreated', 'receded', 'faded', 'diminished', 'decreased',
                'reduced', 'lessened', 'lowered', 'dropped', 'fallen', 'sunk', 'descended', 'plummeted', 'plunged',
                'dived', 'nosedived', 'tumbled', 'collapsed', 'crumbled', 'disintegrated', 'dissolved', 'melted',
                'evaporated', 'vaporized', 'dematerialized', 'vanished', 'disappeared', 'evanesced', 'faded away',
                'melted away', 'dissolved away', 'evaporated away', 'vanished into thin air', 'gone without trace',
                'left no trace', 'no sign', 'no evidence', 'no clue', 'no lead', 'no information', 'no data',
                'no record', 'no documentation', 'no paperwork', 'no file', 'no archive', 'no history', 'no background',
                'no profile', 'no identity', 'no existence', 'no presence', 'no appearance', 'no manifestation',
                'no representation', 'no indication', 'no suggestion', 'no hint', 'no clue', 'no inkling', 'no intimation',
                'no whisper', 'no rumor', 'no gossip', 'no talk', 'no discussion', 'no conversation', 'no dialogue',
                'no communication', 'no contact', 'no connection', 'no relation', 'no relationship', 'no association',
                'no link', 'no bond', 'no tie', 'no attachment', 'no affiliation', 'no membership', 'no participation',
                'no involvement', 'no engagement', 'no commitment', 'no dedication', 'no devotion', 'no loyalty',
                'no allegiance', 'no faithfulness', 'no fidelity', 'no constancy', 'no steadfastness', 'no reliability'
            ],
            
            # Property Damage (150+ keywords)
            'property_damage': [
                'vandalism', 'property damage', 'destruction', 'wrecking', 'ruination', 'demolition', 'razing',
                'leveling', 'flattening', 'bulldozing', 'knocking down', 'tearing down', 'pulling down', 'breaking down',
                'smashing', 'shattering', 'crushing', 'pulverizing', 'grinding', 'milling', 'powdering', 'fragmenting',
                'splintering', 'sharding', 'cracking', 'fracturing', 'splitting', 'cleaving', 'rending', 'ripping',
                'tearing', 'shredding', 'slashing', 'cutting', 'slicing', 'dicing', 'chopping', 'mincing', 'hacking',
                'hewing', 'carving', 'whittling', 'sculpting', 'shaping', 'forming', 'molding', 'casting', 'forging',
                'hammering', 'pounding', 'beating', 'battering', 'pummeling', 'thrashing', 'whipping', 'lashing',
                'flogging', 'scourging', 'flagellating', 'strapping', 'caning', 'birching', 'spanking', 'smacking',
                'slapping', 'cuffing', 'boxing', 'punching', 'jabbing', 'hooking', 'uppercutting', 'crossing',
                'swinging', 'roundhousing', 'spinning', 'backfisting', 'elbowing', 'kneeing', 'kicking', 'stomping',
                'trampling', 'crushing', 'squashing', 'flattening', 'compressing', 'compacting', 'condensing',
                'squeezing', 'pressing', 'pushing', 'shoving', 'thrusting', 'propelling', 'driving', 'moving',
                'displacing', 'relocating', 'transferring', 'shifting', 'transposing', 'transplanting', 'transmitting',
                'conveying', 'transporting', 'carrying', 'bearing', 'hauling', 'towing', 'dragging', 'pulling',
                'tugging', 'yanking', 'jerking', 'wrenching', 'twisting', 'turning', 'rotating', 'spinning', 'revolving'
            ],
            
            # Domestic Violence (150+ keywords)
            'domestic_violence': [
                'domestic violence', 'spousal abuse', 'partner violence', 'intimate partner violence', 'relationship abuse',
                'marital violence', 'conjugal violence', 'family violence', 'household violence', 'home violence',
                'domestic abuse', 'spousal abuse', 'partner abuse', 'intimate partner abuse', 'relationship abuse',
                'marital abuse', 'conjugal abuse', 'family abuse', 'household abuse', 'home abuse', 'domestic assault',
                'spousal assault', 'partner assault', 'intimate partner assault', 'relationship assault', 'marital assault',
                'conjugal assault', 'family assault', 'household assault', 'home assault', 'domestic battery',
                'spousal battery', 'partner battery', 'intimate partner battery', 'relationship battery', 'marital battery',
                'conjugal battery', 'family battery', 'household battery', 'home battery', 'domestic harassment',
                'spousal harassment', 'partner harassment', 'intimate partner harassment', 'relationship harassment',
                'marital harassment', 'conjugal harassment', 'family harassment', 'household harassment', 'home harassment',
                'domestic stalking', 'spousal stalking', 'partner stalking', 'intimate partner stalking', 'relationship stalking',
                'marital stalking', 'conjugal stalking', 'family stalking', 'household stalking', 'home stalking',
                'domestic threat', 'spousal threat', 'partner threat', 'intimate partner threat', 'relationship threat',
                'marital threat', 'conjugal threat', 'family threat', 'household threat', 'home threat', 'domestic coercion',
                'spousal coercion', 'partner coercion', 'intimate partner coercion', 'relationship coercion', 'marital coercion',
                'conjugal coercion', 'family coercion', 'household coercion', 'home coercion', 'domestic control',
                'spousal control', 'partner control', 'intimate partner control', 'relationship control', 'marital control',
                'conjugal control', 'family control', 'household control', 'home control', 'domestic isolation',
                'spousal isolation', 'partner isolation', 'intimate partner isolation', 'relationship isolation',
                'marital isolation', 'conjugal isolation', 'family isolation', 'household isolation', 'home isolation',
                'domestic financial abuse', 'spousal financial abuse', 'partner financial abuse', 'intimate partner financial',
                'relationship financial abuse', 'marital financial abuse', 'conjugal financial abuse', 'family financial',
                'household financial abuse', 'home financial abuse', 'domestic emotional abuse', 'spousal emotional',
                'partner emotional abuse', 'intimate partner emotional', 'relationship emotional abuse', 'marital emotional',
                'conjugal emotional abuse', 'family emotional abuse', 'household emotional abuse', 'home emotional abuse'
            ],
            
            # Drug Related Crimes (150+ keywords)
            'drug_crime': [
                'drug trafficking', 'drug dealing', 'narcotics', 'substance abuse', 'drug possession', 'drug distribution',
                'drug manufacturing', 'drug cultivation', 'drug smuggling', 'drug transport', 'drug sale', 'drug purchase',
                'drug trade', 'drug business', 'drug network', 'drug cartel', 'drug gang', 'drug organization',
                'drug ring', 'drug operation', 'drug activity', 'drug transaction', 'drug exchange', 'drug transfer',
                'drug delivery', 'drug supply', 'drug demand', 'drug consumption', 'drug use', 'drug abuse',
                'drug addiction', 'drug dependence', 'drug habit', 'drug problem', 'drug issue', 'drug matter',
                'drug concern', 'drug situation', 'drug condition', 'drug state', 'drug status', 'drug position',
                'drug circumstance', 'drug environment', 'drug setting', 'drug context', 'drug background',
                'drug atmosphere', 'drug climate', 'drug mood', 'drug tone', 'drug spirit', 'drug feeling',
                'drug sensation', 'drug perception', 'drug impression', 'drug notion', 'drug idea', 'drug thought',
                'drug concept', 'drug conception', 'drug understanding', 'drug comprehension', 'drug knowledge',
                'drug awareness', 'drug consciousness', 'drug recognition', 'drug realization', 'drug appreciation',
                'drug grasp', 'drug mastery', 'drug command', 'drug control', 'drug power', 'drug authority',
                'drug influence', 'drug sway', 'drug leverage', 'drug pull', 'drug weight', 'drug clout',
                'drug muscle', 'drug strength', 'drug force', 'drug might', 'drug potency', 'drug power',
                'drug energy', 'drug vigor', 'drug vitality', 'drug dynamism', 'drug drive', 'drug motivation',
                'drug incentive', 'drug stimulus', 'drug spur', 'drug goad', 'drug prod', 'drug push', 'drug shove',
                'drug thrust', 'drug impulse', 'drug momentum', 'drug impetus', 'drug force', 'drug pressure',
                'drug stress', 'drug strain', 'drug tension', 'drug anxiety', 'drug worry', 'drug concern',
                'drug care', 'drug attention', 'drug notice', 'drug regard', 'drug consideration', 'drug thoughtfulness'
            ],
            
            # Sexual Offenses (150+ keywords)
            'sexual_offense': [
                'sexual assault', 'rape', 'molestation', 'sexual abuse', 'sexual violence', 'sexual harassment',
                'sexual misconduct', 'sexual offense', 'sexual crime', 'sexual violation', 'sexual exploitation',
                'sexual coercion', 'sexual pressure', 'sexual force', 'sexual threat', 'sexual intimidation',
                'sexual blackmail', 'sexual extortion', 'sexual bribery', 'sexual corruption', 'sexual deception',
                'sexual fraud', 'sexual trickery', 'sexual manipulation', 'sexual control', 'sexual domination',
                'sexual submission', 'sexual surrender', 'sexual yielding', 'sexual capitulation', 'sexual resignation',
                'sexual acceptance', 'sexual agreement', 'sexual consent', 'sexual permission', 'sexual authorization',
                'sexual approval', 'sexual endorsement', 'sexual support', 'sexual backing', 'sexual sponsorship',
                'sexual patronage', 'sexual advocacy', 'sexual promotion', 'sexual advancement', 'sexual furtherance',
                'sexual facilitation', 'sexual enablement', 'sexual empowerment', 'sexual strengthening',
                'sexual reinforcement', 'sexual bolstering', 'sexual buttressing', 'sexual propping', 'sexual shoring',
                'sexual supporting', 'sexual upholding', 'sexual maintaining', 'sexual sustaining', 'sexual preserving',
                'sexual conserving', 'sexual protecting', 'sexual guarding', 'sexual defending', 'sexual shielding',
                'sexual sheltering', 'sexual harboring', 'sexual housing', 'sexual lodging', 'sexual accommodating',
                'sexual quartering', 'sexual billeting', 'sexual boarding', 'sexual rooming', 'sexual staying',
                'sexual dwelling', 'sexual residing', 'sexual inhabiting', 'sexual occupying', 'sexual possessing',
                'sexual holding', 'sexual owning', 'sexual having', 'sexual keeping', 'sexual retaining',
                'sexual preserving', 'sexual conserving', 'sexual saving', 'sexual storing', 'sexual stockpiling',
                'sexual hoarding', 'sexual accumulating', 'sexual amassing', 'sexual gathering', 'sexual collecting',
                'sexual assembling', 'sexual compiling', 'sexual organizing', 'sexual arranging', 'sexual ordering',
                'sexual systematizing', 'sexual methodizing', 'sexual regulating', 'sexual controlling',
                'sexual directing', 'sexual managing', 'sexual supervising', 'sexual overseeing', 'sexual monitoring',
                'sexual watching', 'sexual observing', 'sexual scrutinizing', 'sexual examining', 'sexual inspecting',
                'sexual checking', 'sexual verifying', 'sexual confirming', 'sexual validating', 'sexual authenticating'
            ],
            
            # Online Harassment (150+ keywords)
            'online_harassment': [
                'cyberbullying', 'online harassment', 'internet bullying', 'digital harassment', 'web harassment',
                'social media bullying', 'facebook bullying', 'instagram bullying', 'twitter bullying', 'tiktok bullying',
                'whatsapp bullying', 'telegram bullying', 'signal bullying', 'email harassment', 'message harassment',
                'text harassment', 'sms harassment', 'mms harassment', 'chat harassment', 'forum harassment',
                'comment harassment', 'post harassment', 'share harassment', 'like harassment', 'follow harassment',
                'unfollow harassment', 'block harassment', 'report harassment', 'flag harassment', 'remove harassment',
                'delete harassment', 'edit harassment', 'modify harassment', 'change harassment', 'alter harassment',
                'adjust harassment', 'adapt harassment', 'modulate harassment', 'regulate harassment', 'control harassment',
                'direct harassment', 'manage harassment', 'supervise harassment', 'oversee harassment', 'monitor harassment',
                'watch harassment', 'observe harassment', 'scrutinize harassment', 'examine harassment', 'inspect harassment',
                'check harassment', 'verify harassment', 'confirm harassment', 'validate harassment', 'authenticate harassment',
                'certify harassment', 'attest harassment', 'witness harassment', 'testify harassment', 'swear harassment',
                'affirm harassment', 'declare harassment', 'state harassment', 'assert harassment', 'claim harassment',
                'allege harassment', 'contend harassment', 'maintain harassment', 'insist harassment', 'persist harassment',
                'persevere harassment', 'continue harassment', 'endure harassment', 'last harassment', 'survive harassment',
                'persist harassment', 'remain harassment', 'stay harassment', 'linger harassment', 'abide harassment',
                'dwell harassment', 'reside harassment', 'inhabit harassment', 'occupy harassment', 'possess harassment',
                'hold harassment', 'own harassment', 'have harassment', 'keep harassment', 'retain harassment',
                'preserve harassment', 'conserve harassment', 'save harassment', 'protect harassment', 'guard harassment',
                'defend harassment', 'shield harassment', 'shelter harassment', 'harbor harassment', 'house harassment',
                'lodge harassment', 'accommodate harassment', 'quarter harassment', 'billet harassment', 'board harassment',
                'room harassment', 'stay harassment', 'dwell harassment', 'reside harassment', 'inhabit harassment',
                'occupy harassment', 'possess harassment', 'hold harassment', 'own harassment', 'have harassment',
                'keep harassment', 'retain harassment', 'preserve harassment', 'conserve harassment', 'save harassment'
            ],
            
            'ai_ml_crime': [
                'ai crime', 'artificial intelligence crime', 'machine learning crime', 'deep learning crime',
                'neural network crime', 'generative ai crime', 'chatgpt crime', 'language model crime',
                'transformer crime', 'gpt crime', 'bert crime', 'dalle crime', 'midjourney crime',
                'stable diffusion crime', 'synthetic media crime', 'deepfake crime', 'voice cloning crime',
                'face swapping crime', 'image generation crime', 'video generation crime', 'text generation crime',
                'code generation crime', 'content generation crime', 'creative ai crime', 'autonomous system crime',
                'robot crime', 'drone crime', 'self driving car crime', 'autonomous vehicle crime',
                'smart device crime', 'iot crime', 'internet of things crime', 'smart home crime',
                'wearable crime', 'fitness tracker crime', 'health monitor crime', 'medical device crime',
                'industrial robot crime', 'manufacturing robot crime', 'service robot crime', 'entertainment robot crime',
                'educational robot crime', 'research robot crime', 'military robot crime', 'defense robot crime',
                'security robot crime', 'surveillance robot crime', 'inspection robot crime', 'maintenance robot crime',
                'cleaning robot crime', 'delivery robot crime', 'transportation robot crime', 'logistics robot crime',
                'warehouse robot crime', 'inventory robot crime', 'quality control robot crime', 'production robot crime',
                'assembly robot crime', 'packaging robot crime', 'shipping robot crime', 'receiving robot crime',
                'stocking robot crime', 'picking robot crime', 'sorting robot crime', 'counting robot crime',
                'weighing robot crime', 'measuring robot crime', 'testing robot crime', 'calibration robot crime',
                'alignment robot crime', 'adjustment robot crime', 'repair robot crime', 'service robot crime',
                'diagnostic robot crime', 'prognostic robot crime', 'predictive maintenance robot crime',
                'condition monitoring robot crime', 'performance monitoring robot crime', 'efficiency monitoring robot crime',
                'productivity monitoring robot crime', 'quality monitoring robot crime', 'safety monitoring robot crime',
                'security monitoring robot crime', 'compliance monitoring robot crime', 'regulatory monitoring robot crime',
                'environmental monitoring robot crime', 'health monitoring robot crime', 'wellness monitoring robot crime',
                'fitness monitoring robot crime', 'activity monitoring robot crime', 'sleep monitoring robot crime',
                'nutrition monitoring robot crime', 'hydration monitoring robot crime', 'medication monitoring robot crime',
                'treatment monitoring robot crime', 'recovery monitoring robot crime', 'rehabilitation monitoring robot crime',
                'therapy monitoring robot crime', 'counseling monitoring robot crime', 'coaching monitoring robot crime',
                'training monitoring robot crime', 'education monitoring robot crime', 'learning monitoring robot crime',
                'development monitoring robot crime', 'growth monitoring robot crime', 'progress monitoring robot crime',
                'achievement monitoring robot crime', 'success monitoring robot crime', 'performance monitoring robot crime'
            ]
        }
        
        # Priority factors (remains the same as previous)
        self.priority_factors = {
            'critical': ['urgent', 'emergency', 'critical', 'immediate', 'danger', 'serious', 'severe', 'life threatening',
                         'fatal', 'lethal', 'deadly', 'mortal', 'terminal', 'final', 'last', 'ultimate', 'extreme',
                        'maximum', 'highest', 'top', 'peak', 'pinnacle', 'zenith', 'apex', 'acme', 'summit', 'crest',
                        'crown', 'tip', 'topmost', 'uppermost', 'highest', 'maximum', 'supreme', 'paramount', 'preeminent',
                        'dominant', 'predominant', 'prevailing', 'prevalent', 'common', 'usual', 'ordinary', 'normal',
                        'regular', 'standard', 'typical', 'conventional', 'traditional', 'customary', 'habitual',
                        'routine', 'everyday', 'daily', 'quotidian', 'mundane', 'commonplace', 'prosaic', 'unremarkable'
                        ],
            
            'high': ['important', 'significant', 'major', 'substantial', 'considerable', 'notable', 'remarkable',
                    'outstanding', 'exceptional', 'extraordinary', 'unusual', 'uncommon', 'rare', 'scarce', 'sparse',
                    'infrequent', 'occasional', 'intermittent', 'sporadic', 'erratic', 'irregular', 'uneven', 'variable',
                    'changeable', 'unstable', 'volatile', 'fluctuating', 'oscillating', 'swinging', 'wavering', 'vacillating',
                    'hesitating', 'dithering', 'faltering', 'stumbling', 'staggering', 'tottering', 'reeling', 'lurching',
                    'swaying', 'rocking', 'rolling', 'pitching', 'tossing', 'heaving', 'bucking', 'jolting', 'jarring',
                    'shaking', 'vibrating', 'quivering', 'trembling', 'shuddering', 'shivering', 'quaking', 'wobbling'
                    ],
            
            'medium': ['moderate', 'average', 'medium', 'middling', 'intermediate', 'median', 'mean', 'central', 'middle',
                      'mid', 'halfway', 'equidistant', 'balanced', 'equal', 'even', 'level', 'uniform', 'consistent',
                      'constant', 'steady', 'stable', 'fixed', 'set', 'established', 'determined', 'decided', 'settled',
                      'resolved', 'concluded', 'finished', 'completed', 'accomplished', 'achieved', 'attained', 'reached',
                      'gained', 'obtained', 'acquired', 'secured', 'procured', 'got', 'received', 'accepted', 'taken',
                      'adopted', 'embraced', 'welcomed', 'received', 'greeted', 'met', 'encountered', 'faced', 'confronted'
                      ],
            
            'low': ['minor', 'small', 'trivial', 'insignificant', 'slight', 'minimal', 'negligible', 'inconsequential',
                   'unimportant', 'irrelevant', 'immaterial', 'extraneous', 'peripheral', 'marginal', 'borderline',
                   'fringe', 'edge', 'verge', 'brink', 'threshold', 'limit', 'boundary', 'border', 'frontier', 'perimeter',
                   'circumference', 'outline', 'contour', 'profile', 'silhouette', 'shape', 'form', 'figure', 'pattern',
                   'design', 'arrangement', 'organization', 'structure', 'framework', 'skeleton', 'shell', 'casing',
                   'housing', 'enclosure', 'container', 'receptacle', 'vessel', 'holder', 'carrier', 'bearer', 'porter'
                   ]
        }

    def preprocess_text(self, text):
        """Preprocess text for classification"""
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def predict_category(self, title, description, is_missing=False, is_injury=False, estimated_loss=0):
        """Predict crime category and priority"""
        try:
            # Combine text for analysis
            combined_text = f"{title} {description}"
            
            # Rule-based classification as primary
            category = self.rule_based_classification(combined_text)
            priority = self.calculate_priority(combined_text, is_missing, is_injury, estimated_loss)
            
            # If model is trained, use it for confirmation
            if self.is_trained:
                try:
                    predicted = self.pipeline.predict([self.preprocess_text(combined_text)])[0]
                    # Use model prediction if it's more specific than 'other'
                    if predicted != 'other':
                        category = predicted
                except Exception as e:
                    print(f"⚠️ Model prediction failed: {e}")
            
            return category, priority
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return 'other', 'medium'

    def rule_based_classification(self, text):
        """Rule-based crime classification with scoring"""
        text_lower = self.preprocess_text(text)
        scores = {}
        
        for category, keywords in self.crime_categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            # Return category with highest score
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return 'other'

    def calculate_priority(self, text, is_missing, is_injury, estimated_loss):
        """Calculate case priority with weighted scoring"""
        priority_score = 0
        text_lower = self.preprocess_text(text)
        
        # Text-based priority indicators
        if any(word in text_lower for word in self.priority_factors['critical']):
            priority_score += 3
        if any(word in text_lower for word in self.priority_factors['high']):
            priority_score += 2
        if any(word in text_lower for word in self.priority_factors['medium']):
            priority_score += 1
        
        # Additional factors
        if is_missing:
            priority_score += 3
        if is_injury:
            priority_score += 2
        if estimated_loss and estimated_loss > 10000:
            priority_score += 2
        elif estimated_loss and estimated_loss > 1000:
            priority_score += 1
        
        # Determine priority level
        if priority_score >= 5:
            return 'critical'
        elif priority_score >= 3:
            return 'high'
        elif priority_score >= 1:
            return 'medium'
        else:
            return 'low'

    def extract_keywords(self, text):
        """Extract relevant keywords from text"""
        try:
            words = self.preprocess_text(text).split()
            # Filter short words and return top 10 unique words
            meaningful_words = [word for word in words if len(word) > 3]
            return list(set(meaningful_words))[:10]
        except Exception as e:
            print(f"❌ Keyword extraction error: {e}")
            return []

    def load_model(self):
        """Load trained model - ADD THIS MISSING METHOD"""
        try:
            if os.path.exists('models/crime_classifier.pkl'):
                self.pipeline = joblib.load('models/crime_classifier.pkl')
                self.is_trained = True
                print("✅ Crime classifier model loaded successfully")
                return True
            else:
                print("⚠️ No trained model found. Using rule-based classification.")
                return False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

    def save_model(self):
        """Save trained model"""
        try:
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.pipeline, 'models/crime_classifier.pkl')
            print("✅ Crime classifier model saved successfully")
        except Exception as e:
            print(f"❌ Error saving model: {e}")

    def train_model(self, training_data):
        """Train the classification model"""
        try:
            texts = [self.preprocess_text(item['text']) for item in training_data]
            labels = [item['category'] for item in training_data]
            
            # Train the pipeline
            self.pipeline.fit(texts, labels)
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            print(f"✅ Model trained successfully with {len(training_data)} samples")
            return True
            
        except Exception as e:
            print(f"❌ Training error: {e}")
            return False

# Create global instance
crime_classifier = CrimeClassifier()

# MODULE-LEVEL FUNCTIONS - These are what your routes import
def classify_complaint(description, title="", is_missing=False, is_injury=False, estimated_loss=0):
    """Classify complaint using AI classifier"""
    try:
        category, priority = crime_classifier.predict_category(title, description, is_missing, is_injury, estimated_loss)
        return category, priority
    except Exception as e:
        print(f"❌ Classification error: {e}")
        return 'other', 'medium'

def extract_keywords(text):
    """Extract relevant keywords from text"""
    try:
        return crime_classifier.extract_keywords(text)
    except Exception as e:
        print(f"❌ Keyword extraction error: {e}")
        return []

# Try to load pre-trained model on startup (this will work now)
try:
    crime_classifier.load_model()
except Exception as e:
    print(f"⚠️ Could not load model on startup: {e}")
    print("ℹ️ Using rule-based classification instead")