## Canvas Submission Uploader

A very simple submission script for [Instructure Canvas](https://www.canvaslms.com/).

I find it useful for multi-file submissions, where I always risk forgetting a piece of code that
I need to submit. As an [OMSCS](https://www.omscs.gatech.edu/) student, I find this VERY useful.

The code performs a verification by downloading files and checking their digests after submitting.

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
  automatically in an isolated way, so it won't mess with your system deps)

## Caveats

It seems that Canvas doesn't work properly with empty files. Don't use empty files as placeholders
when you don't have data yet, or verification will fail.

## Notes

This is an unofficial tool. I'm not affiliated with Instructure.

## Disclaimer

While I put a bit of effort into this, and I use it myself, bugs can happen. APIs can change.
I'm not responsibile if your assignment doesn't get submitted and you get a bad grade.
