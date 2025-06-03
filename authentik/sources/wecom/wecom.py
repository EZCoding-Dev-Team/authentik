"""WeCom Views"""

from django.core.cache import cache
from structlog.stdlib import get_logger

from authentik.core.sources.flow_manager import SourceFlowManager
from authentik.lib.utils.http import get_http_session
from authentik.sources.wecom.models import WeComSource, UserWeComSourceConnection

LOGGER = get_logger()

AK_CACHE_KEY = "authentik_wecom_access_token"
CODE_CACHE_KEY = "authentik_wecom_code"


class WeComAuth:
    """WeCom authentication utilities"""

    _source: WeComSource
    _code: str

    def __init__(self, source: WeComSource, code: str):
        self._source = source
        self._code = code
        self._session = get_http_session()
        self._session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )

    def get_access_token(self) -> str:
        """Get access token from WeCom"""
        cache_key = f"{AK_CACHE_KEY}:{self._source.corp_id}_{self._source.agent_id}"
        access_token = cache.get(cache_key)
        if access_token:
            return access_token
        response = self._session.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken",
            params={
                "corpid": self._source.corp_id,
                "corpsecret": self._source.secret,
            },
        )
        response.raise_for_status()
        data = response.json()
        if data.get("errcode") != 0:
            raise Exception("Unable to get access token:", data.get("errmsg"))
        access_token = data.get("access_token")
        if not access_token:
            raise Exception("Unable to get access token")
        cache.set(cache_key, access_token, data.get("expires_in"))
        return access_token

    def get_user_access(self, code: str) -> [str, str]:
        """Get user access from WeCom"""
        access_token = self.get_access_token()
        response = self._session.get(
            "https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo",
            params={
                "access_token": access_token,
                "code": code,
            },
        )
        response.raise_for_status()
        data = response.json()
        if data.get("errcode") != 0:
            raise Exception("Unable to get user access:", data.get("errmsg"))
        user_id = data.get("userid")
        user_ticket = data.get("user_ticket")
        return user_id, user_ticket

    def get_user_brief(self, user_id):
        """Get user brief info from WeCom"""
        access_token = self.get_access_token()
        response = self._session.get(
            "https://qyapi.weixin.qq.com/cgi-bin/user/get",
            params={
                "access_token": access_token,
                "userid": user_id,
            },
        )
        response.raise_for_status()
        data = response.json()
        if data.get("errcode") != 0:
            raise Exception("Unable to get user access:", data.get("errmsg"))
        return data

    def get_user_detail(self, ticket: str) -> dict:
        """Get user detail from WeCom"""
        access_token = self.get_access_token()
        response = self._session.post(
            "https://qyapi.weixin.qq.com/cgi-bin/auth/getuserdetail",
            params={"access_token": access_token},
            json={"user_ticket": ticket},
        )
        response.raise_for_status()
        data = response.json()
        if data.get("errcode") != 0:
            raise Exception("Unable to get user access:", data.get("errmsg"))
        return data

    def get_user_info(self) -> tuple[dict, str]:
        """Get user info of the WeCom token"""
        user_id, ticket = self.get_user_access(self._code)
        user_brief = self.get_user_brief(user_id)
        if user_brief.get("status") != 1:
            raise Exception("Unable to login: user in not active")
        user_detail = self.get_user_detail(ticket)
        user = {
            "userid": user_id,
            "name": user_brief.get("name"),
            "email": user_detail.get("email"),
            "biz_email": user_detail.get("biz_mail"),
            "mobile": user_detail.get("mobile")
        }
        return user, user_id


class WeComSourceFlowManager(SourceFlowManager):
    """Flow manager for WeCom sources"""

    user_connection_type = UserWeComSourceConnection

    def update_user_connection(
        self, connection: UserWeComSourceConnection, **kwargs
    ) -> UserWeComSourceConnection:
        """Set the access_token on the connection"""
        connection.access_token = kwargs.get("access_token")
        return connection
