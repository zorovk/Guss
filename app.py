import webapp2
import config

tempconfig = {}
tempconfig["webapp2_extras.sessions"] = {
            "secret_key": config.get_config("session_secret_key")
            }

app = webapp2.WSGIApplication([
                    webapp2.Route("/user/login", handler="user_auth.LoginHandler", name="login"),
                    webapp2.Route("/user/logout", handler="user_auth.LogoutHandler", name="logout"),
                    webapp2.Route("/user/confirm", handler="user_confirm.UserConfirmHandler", name="account-confirm"),
                    webapp2.Route("/admin/config", handler="admin_config.AdminConfigHandler", name="manage-config"),
                    webapp2.Route("/admin/user/add", handler="admin_user.AdminAddUserHandler", name="add-user"),
                    webapp2.Route("/admin/user", handler="admin_user.AdminUserHandler", name="manage-user"),
                    webapp2.Route("/", handler="homepage.HomepageHandler", name="home"),
                ], debug=True, config=tempconfig)
