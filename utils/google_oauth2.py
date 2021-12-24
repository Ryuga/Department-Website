import requests
from google_auth_oauthlib.flow import Flow
from django.conf import settings


class GoogleOauth(object):

    endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"

    def __init__(self, redirect_uri):
        self.redirect_uri = redirect_uri
        self.scopes = [
                     "https://www.googleapis.com/auth/userinfo.profile",
                     "https://www.googleapis.com/auth/userinfo.email",
                     "openid",
                 ]
        self.flow = Flow.from_client_config(
            client_config=settings.GOOGLE_CLIENT_SECRET,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )

    def get_access_token(self, request):
        response = self.flow.fetch_token(code=request.GET.get("code"))
        access_token = response.get("access_token")
        return access_token

    def get_user_json(self, access_token):
        headers = {"Authorization": "Bearer {}".format(access_token)}
        resp = requests.get(self.endpoint, headers=headers).json()
        return resp
