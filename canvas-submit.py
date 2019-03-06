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

# https://stackoverflow.com/a/44873382
def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


# https://stackoverflow.com/a/16696317 with tweaks
def download_file(url, f):
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    # possibly unneeded.
    f.flush()


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

hashes = {}
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

    hashes[fn] = sha256sum(fn)
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
submission_response = r3.json()

print("")
print("Submission upload OK!")
print("")
print("Verifying...")
r4 = requests.get(
    CANVAS_API_BASE
    + "courses/{COURSE_ID}/assignments/{ASSIGNMENT_ID}/submissions/{user_id}".format(
        COURSE_ID=COURSE_ID,
        ASSIGNMENT_ID=ASSIGNMENT_ID,
        user_id=submission_response["user_id"],
    ),
    params={"access_token": CANVAS_KEY},
)
r4.raise_for_status()

submission_request_response = r4.json()
attachments = submission_request_response["attachments"]

for a in attachments:
    fn = a["filename"]
    url = a["url"]
    with open("/tmp/" + fn, "wb") as tmp:
        download_file(url, tmp)
        digest = sha256sum(tmp.name)
        if digest != hashes[fn]:
            raise ValueError("Unmatching content for file {fn}".format(fn=fn))
        print(
            "{fn} verification succeeded, sha256 digest: {digest}".format(
                fn=fn, digest=digest
            )
        )


print("")
print("Submission verification OK!")
