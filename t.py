s="""1) Positive (willing to communicate further or likely to purchase in the future)
2) Neutral (interjections, modal particles, nouns or adjectives with no obvious emotional meaning)
3) Positive (willing to communicate further or likely to purchase in the future)
4) neutral(no obvious emotional meaning)
5) neutral(no obvious emotional meaning)
6) positive(willing to purchase in the future)
7) positive(willing to purchase in the future)
8) neutral(involves numbers, phone numbers, dates, addresses or web addresses)"""

import re

print(s)
print()
print(re.sub(r" *\(", " (", s.lower()))


