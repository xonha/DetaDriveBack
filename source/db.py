import os

import deta

_deta_key = os.getenv("DETA_PROJECT_KEY")
_deta = deta.Deta(_deta_key)  # type: ignore

storage = _deta.Drive("storage")

tbl_users = _deta.Base("users")
tbl_files = _deta.Base("files")
tbl_users_files = _deta.Base("users_files")
