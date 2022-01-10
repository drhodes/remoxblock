import hashlib


# NOTE: The kubernetes jupyterhub may not truncate the user id
# like this.
def generate_jupyterhub_userid(anonymous_student_id):
    anon_id = "jupyter-" + anonymous_student_id

    # jupyterhub truncates this and appends a five character hash.
    # https://tljh.jupyter.org/en/latest/topic/security.html
    #
    # where is this done?
    # https://gist.github.com/martinclaus/c6f229de82769b0b4ae6c7bf3b232106
    # https://github.com/jupyterhub/the-littlest-jupyterhub/blob/main/tljh/normalize.py

    userhash = hashlib.sha256(anon_id.encode("utf-8")).hexdigest()
    return f"{anon_id[:26]}-{userhash[:5]}"
