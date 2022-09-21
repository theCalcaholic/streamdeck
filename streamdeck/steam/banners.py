import json
import re

import urllib3
from urllib.parse import urlencode
from typing import Tuple

http = urllib3.PoolManager()
protocol_pattern = re.compile(r'https?://')


async def get_logo_from_ddg(search) -> Tuple[str, int, int] | None:
    for suffix in '', ' web', ' service', ' streaming', ' web service':
        query = urlencode({
            'q': protocol_pattern.sub('', f'{search}{suffix}'),
            'format': 'json',
            'pretty': 0,
            't': 'streamdeck'
        })
        print(query)
        result = http.urlopen("GET", f"https://duckduckgo.com/?{query}")
        parsed = json.loads(result.data)
        print(parsed)
        try:
            if 'Image' in parsed and parsed['ImageIsLogo']:
                return f"https://duckduckgo.com{parsed['Image']}", int(parsed['ImageHeight'] or -1), \
                       int(parsed['ImageWidth'] or -1)
            for topic in parsed['RelatedTopics'] or []:
                if 'Icon' in topic and topic['Icon']['URL']:
                    return f"https://duckduckgo.com{topic['Icon']['URL']}", int(topic['Icon']['Height'] or -1), \
                           int(topic['Icon']['Width'] or -1)
        except ValueError:
            pass
    return None


if __name__ == '__main__':
    print(get_logo_from_ddg('https://youtube.com')[0])
