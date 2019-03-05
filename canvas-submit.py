#!/usr/bin/env python3
import os
import sys
from tempfile import gettempdir, NamedTemporaryFile
import hashlib

# start editing here

# pick an access token in Account -> Settings -> Approved Integrations -> New Access Token.
# KEEP THE TOKEN PRIVATE (hence, don't commit this script in public repos)
# if you accidentally leak the token, you must delete it from canvas!
CANVAS_KEY = "mycanvaskey"
# Base API URL for Georgia Tech Canvas. Tweak this for other institutes.
CANVAS_API_BASE = "https://gatech.instructure.com/api/v1/"
# from your course url - e.g. https://gatech.instructure.com/courses/35002 - pick the final number
COURSE_ID = 35002
# from the url of your chosen assignment - e.g. https://gatech.instructure.com/courses/35002/assignments/112300 - pick the final number
ASSIGNMENT_ID = 112300

# here, you should set the files that you'd like to upload, as a list, e.g. [ "file1.ext", "file2.ext" ]
FILENAMES = []

# stop editing here

REQUIREMENTS = """
certifi==2018.11.29
chardet==3.0.4
idna==2.8
python-magic==0.4.15
requests==2.21.0
urllib3==1.24.1
"""


def add_custom_site_packages_directory(raise_if_failure=True):
    digest = hashlib.sha256(REQUIREMENTS.encode("utf8")).hexdigest()
    dep_root = os.path.join(gettempdir(), "pyallinone_{}".format(digest))
    os.makedirs(dep_root, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(dep_root):
        if dirpath.endswith(os.path.sep + "site-packages"):
            # that's our dir!
            sys.path.insert(0, os.path.abspath(dirpath))
            return dep_root

    if raise_if_failure:
        raise ValueError("could not find our site-packages dir")

    return dep_root


dep_root = add_custom_site_packages_directory(False)

deps_installed = False

while True:
    try:
        import requests
        import magic
        break
    except ImportError:
        if deps_installed:
            raise ValueError("Something was broken, could not install dependencies")
        try:
            from pip import main as pipmain
        except ImportError:
            from pip._internal import main as pipmain

        with NamedTemporaryFile() as req:
            req.write(REQUIREMENTS.encode("utf-8"))
            req.flush()
            pipmain(
                [
                    "install",
                    "--prefix",
                    dep_root,
                    "--upgrade",
                    "--no-cache-dir",
                    "--no-deps",
                    "-r",
                    req.name,
                ]
            )

        add_custom_site_packages_directory()
        deps_installed = True

file_ids = []
for fn in FILENAMES:
    print(
        "uploading {fn} for assignment {ASSIGNMENT_ID}".format(
            fn=fn, ASSIGNMENT_ID=ASSIGNMENT_ID
        )
    )
    r = requests.post(
        CANVAS_API_BASE
        + "courses/{COURSE_ID}/assignments/{ASSIGNMENT_ID}/submissions/self/files".format(
            COURSE_ID=COURSE_ID, ASSIGNMENT_ID=ASSIGNMENT_ID
        ),
        json={
            "access_token": CANVAS_KEY,
            "name": fn,
            "size": os.stat(fn).st_size,
            "content_type": magic.from_file(fn, mime=True),
        },
    )
    r.raise_for_status()
    response = r.json()
    upload_url = response["upload_url"]
    upload_params = response["upload_params"]

    r2 = requests.post(
        upload_url, data=upload_params, files={"file": (fn, open(fn, "rb"))}
    )
    r2.raise_for_status()

    upload_response = r2.json()
    file_ids.append(upload_response["id"])

print("Submitting...")
r3 = requests.post(
    CANVAS_API_BASE
    + "courses/{COURSE_ID}/assignments/{ASSIGNMENT_ID}/submissions".format(
        COURSE_ID=COURSE_ID, ASSIGNMENT_ID=ASSIGNMENT_ID
    ),
    json={
        "submission": {"submission_type": "online_upload", "file_ids": file_ids},
        "access_token": CANVAS_KEY,
    },
)

r3.raise_for_status()
print("\n")
print("UPLOAD OK!")
