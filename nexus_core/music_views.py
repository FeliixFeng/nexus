"""MPD 音乐控制 API"""
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mpd import MPDClient


MPD_HOST = 'localhost'
MPD_PORT = 6600
MUSIC_DIR = os.path.expanduser('~/data/music')


def _get_client():
    client = MPDClient()
    client.timeout = 3
    client.connect(MPD_HOST, MPD_PORT)
    return client


@csrf_exempt
@require_http_methods(["GET"])
def music_status(request):
    """获取当前播放状态"""
    try:
        client = _get_client()
        status = client.status()
        current = client.currentsong()
        client.disconnect()

        return JsonResponse({
            'success': True,
            'title': current.get('title', current.get('file', '未知')),
            'artist': current.get('artist', ''),
            'album': current.get('album', ''),
            'state': status.get('state', 'stop'),  # play/pause/stop
            'volume': int(status.get('volume', 0)),
            'random': status.get('random', '0') == '1',
            'repeat': status.get('repeat', '0') == '1',
            'elapsed': status.get('elapsed', '0'),
            'duration': status.get('duration', '0'),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def music_control(request):
    """控制播放: play/pause/next/prev/stop/random"""
    try:
        data = json.loads(request.body)
        action = data.get('action', '')

        client = _get_client()

        if action == 'play':
            client.play()
        elif action == 'pause':
            client.pause()
        elif action == 'toggle':
            # mpd pause 只在播放中有效，stop 时需要 play
            status = client.status()
            if status.get('state') == 'play':
                client.pause()
            else:
                client.play()
        elif action == 'next':
            client.next()
        elif action == 'prev':
            client.previous()
        elif action == 'stop':
            client.stop()
        elif action == 'restart':
            # 重新播放当前歌曲
            client.seekcur(0)
        elif action == 'random':
            # 切换随机模式
            status = client.status()
            new_state = '0' if status.get('random', '0') == '1' else '1'
            client.random(new_state)
        elif action == 'repeat':
            # 切换循环模式
            status = client.status()
            new_state = '0' if status.get('repeat', '0') == '1' else '1'
            client.repeat(new_state)
        elif action == 'play_random':
            # 随机切一首播放
            client.random(1)
            client.next()
        elif action == 'seek':
            # 跳转到指定秒数
            time = data.get('time', 0)
            client.seekcur(int(time))

        client.disconnect()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def music_lyrics(request):
    """获取当前歌曲的嵌入歌词 (LRC 格式)"""
    try:
        client = _get_client()
        current = client.currentsong()
        client.disconnect()

        file_path = current.get('file', '')
        if not file_path:
            return JsonResponse({'success': False, 'error': '无歌曲播放'})

        full_path = os.path.join(MUSIC_DIR, file_path)
        if not os.path.exists(full_path):
            return JsonResponse({'success': False, 'error': '文件不存在'})

        from mutagen.id3 import ID3
        audio = ID3(full_path)
        uslt_tags = audio.getall('USLT')
        if not uslt_tags:
            return JsonResponse({'success': True, 'lyrics': None})

        lyrics_text = uslt_tags[0].text
        return JsonResponse({'success': True, 'lyrics': lyrics_text})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
