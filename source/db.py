import os

import deta

_deta_key = os.getenv("DETA_PROJECT_KEY")
_deta_enviroment = os.getenv("DETA_ENVIRONMENT", "dev")
_deta = deta.Deta(_deta_key)  # type: ignore


storage = _deta.Drive(_deta_enviroment + "_storage")

tbl_users = _deta.Base(_deta_enviroment + "_users")
tbl_files = _deta.Base(_deta_enviroment + "_files")
tbl_users_files = _deta.Base(_deta_enviroment + "_users_files")
