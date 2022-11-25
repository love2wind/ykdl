# -*- coding: utf-8 -*-

from .._common import *


class Douyin(Extractor):
    name = '抖音直播 (Douyin)'

    quality_2_profile_id = {
          'ORIGIN': ['原画', 'OG'],
        'FULL_HD1': ['蓝光', 'BD'],
             'HD1': ['超清', 'TD'],
             'SD1': ['高清', 'HD'],
             'SD2': ['标清', 'SD']
     }

    def prepare(self):
        info = MediaInfo(self.name)

        if 'amemv.com' in self.url:
            data = get_response('https://webcast.amemv.com/webcast/room/reflow/info/',
                                params={
                                    'verifyFp': '',
                                    'type_id': 0,
                                    'live_id': 1,
                                    'sec_user_id': '',
                                    'app_id': 1128,
                                    'msToken': '',
                                    'X-Bogus': '',
                                    'room_id': match1(self.url, '/reflow/(\d+)')
                                }).json()
            video_info = data['data'].get('room')
        else:
            install_cookie()
            for _ in range(2):
                html = get_content(self.url, cache=False)
                data = match1(html,
                             'id="RENDER_DATA" type="application/json">(.+?)</script>',
                             '__INIT_PROPS__ = (.+?)</script>')
                if data:
                    break
            data = json.loads(unquote(data))
            self.logger.debug('data: \n%s', data)

            try:
                video_info = data['app']['initialState']['roomStore']['roomInfo'].get('room')
            except KeyError:
                video_info = data['/webcast/reflow/:id'].get('room')

        assert video_info and video_info['status'] == 2, 'live is off!!!'

        title = video_info['title']
        info.artist = nickName = video_info['owner']['nickname']
        info.title = '{title} - {nickName}'.format(**vars())

        stream_info = video_info['stream_url']
        stream_urls = []
        if 'flv_pull_url' in stream_info:
            for ql, url in stream_info['flv_pull_url'].items():
                stream_urls.append(['flv', ql, url])
            stream_urls.append(['flv', 'ORIGIN', stream_info.get('rtmp_pull_url')])
        if 'hls_pull_url_map' in stream_info:
            for ql, url in stream_info['hls_pull_url_map'].items():
                stream_urls.append(['m3u8', ql, url])
            stream_urls.append(['m3u8', 'ORIGIN', stream_info.get('hls_pull_url')])

        for ext, ql, url in stream_urls:
            if not url:
                continue
            video_profile, stream = self.quality_2_profile_id[ql]
            info.streams[stream + '-' + ext[:3]] = {
                'container': ext,
                'video_profile': video_profile,
                'src' : [url],
            }

        return info

site = Douyin()
