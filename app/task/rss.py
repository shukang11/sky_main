import re
import time
from typing import Optional, Dict, Any, List
import feedparser
from app.utils import get_unix_time_tuple, filter_all_img_src
from app.utils import celery_app
from app.utils import session
from app.utils import get_logger
from app.model import RssContentModel, RssModel

logger = get_logger(__name__)


@celery_app.task(name="web_task.parser_feed_url")
def parser_feed(feed_url: str) -> bool:
    """  经过 `parser_feed_root`后将其中的数据调用 `save_feed_items`存储
    """
    result = parser_feed_root(feed_url)
    return save_feed_items(feed_url, result)


def parser_feed_root(feed_url: str) -> Dict[str, any]:
    """  解析rss网址,产生一个包含了 items 的字典，还需要对其中的信息进行处理
    Args:
        feed_url: rss的网址
    Return:
        一个字典对象
    """
    feeds = feedparser.parse(feed_url)
    payload: Dict[str, any] = {}
    if not hasattr(feeds, "version"):
        # 如果没有版本信息，无法判断是不是个xml，以及使用哪个版本的解析
        return payload
    version: str = feeds.version
    rss_title: str = feeds.feed.title if hasattr(
        feeds.feed, "title"
    ) else ""  # rss的标题
    rss_link: str = feeds.feed.link if hasattr(feeds.feed, "link") else None  # 链接
    if not rss_link:
        return payload

    payload["version"] = version
    payload["title"] = rss_title
    payload["link"] = rss_link

    subtitle: Optional[str] = None
    if version == "atom10":
        subtitle = ""
    elif version == "rss20":
        subtitle = feeds.feed.subtitle or ""  # 副标题
    payload["subtitle"] = subtitle

    result: List[Dict[str, any]] = []
    for item in feeds["entries"]:
        r = {}
        for k in item:
            r[k] = item[k]
        result.append(r)
    payload["items"] = result
    return payload


def save_feed_items(feed_url: str, payload: Optional[Dict[str, any]]) -> bool:
    """  存储获得的订阅信息流
    Args:
        feed_url: 订阅的网址
        payload: 获得的信息流，需要进行处理后存储到表
    Return:
        如果处理成功，则返回 True
    """
    if not payload:
        return False
    operator_map = {
        "rss20": parse_rss20,
        "atom10": parse_atom,
        "rss10": parse_rss10,
    }
    operator = operator_map.get(payload["version"]) or parse_rss20
    if not operator:
        return False
    version = payload["version"] if hasattr(payload, "version") else ""
    title = payload["title"] or "无标题"
    subtitle = payload["subtitle"]
    items = payload["items"]
    rss: RssModel = RssModel.query.filter(RssModel.rss_link == feed_url).one()
    rss.rss_title = title
    rss.version = payload.get('version')
    session.commit()
    for item in items:
        try:
            parsed = operator(item)
            descript: str = ""
            title: str = parsed.get("title") or ""
            link = parsed.get("link") or ""
            cover_img = parsed.get("cover_img") or ""
            published = parsed.get("published") or ""
            descript = parsed.get("descript") or ""
            timeLocal = get_unix_time_tuple()
            model: RssContentModel = RssContentModel(
                link, rss.rss_id, title, descript, cover_img, published, timeLocal
            )
            model.save(True)
        except Exception as error:
            logger.warning(str(error))
            continue

    return True


def parse_rss20(item: Dict[Any, any]) -> Optional[Dict[Any, any]]:
    """  将信息流中的每一项进行格式化整理
    Args:
        item: 字典格式的输入
    Return:
        整理后的字典对象，其中键值对是被整理过的
    """
    try:
        result: Dict[str, any] = {}
        title: str = item["title"]
        summary: str = item["summary"]
        imgs = filter_all_img_src(summary)
        link: str = item["link"] or item["id"] or ""
        published = time.gmtime(time.time())

        if hasattr(item, "published"):
            published = item["published"]
        if hasattr(item, "published_parsed"):
            published = item["published_parsed"]

        published = str(time.mktime(published))
        result.setdefault("title", title)
        result.setdefault("descript", summary)
        result.setdefault("link", link)
        if len(imgs) > 0:
            result.setdefault("cover_img", imgs[0])
        result.setdefault("published", published)
        return result
    except Exception as e:
        return None


def parse_rss10(item: Dict[str, any]) -> Optional[Dict[str, any]]:
    return parse_rss20(item)


def parse_atom(item: Dict[str, any]) -> Optional[Dict[str, any]]:
    return parse_rss20(item)
