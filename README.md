## Canvas Submission Uploader

A very simple submission script for [Instructure Canvas](https://www.canvaslms.com/).

I find it useful for multi-file submissions, where I always risk forgetting a piece of code that
I need to submit. As an [OMSCS](https://www.omscs.gatech.edu/) student, I find this VERY useful.

The code performs a verification by downloading files and checking their digests after submitting.

## Disclaimer

While I put a bit of effort into this, and I use it myself, bugs can happen. APIs can change.
I'm not responsible if your assignment doesn't get submitted and you get a bad grade. **Before the deadline, always check in the web interface if your assignment was submitted, and if the timestamp of the submission matches what do you expect.**

Please note that this is an unofficial tool. I'm unaffiliated with Instructure, Georgia Tech, or any other institution using Canvas. Every user should be responsible for using this; if you don't understand or trust it, check the [Official Canvas API](https://canvas.instructure.com/doc/api/) and only start using this if you believe it works properly.


## Instructions

Steps:
* Create an access token for canvas (Account -> Settings -> Approved integrations -> New Access Token).
  Please remember that such token must be kept private. Don't commit it to public repositories, and if 
  you leak it, you'll need to revoke it.
* Just copy this template in each directory where you hold the files for an assignment
* Tweak the values at the beginning of the script, they're commented. You may choose to pass
  your access token in a CANVAS\_KEY environment variable instead of hardcoding.
* Run the script when you want to submit. Please note that this is designed to use Python3,
  and it's standalone (no need for virtual environments, etc, it will setup its dependencies
  automatically in an isolated way, so it won't mess with your system deps). Just set the proper shebang if needed.

## Caveats

* It seems that Canvas doesn't work properly with empty files. Don't use empty files as placeholders
when you don't have data yet, or verification will fail.
* This is untested on Windows. I use it on Linux and Mac.
