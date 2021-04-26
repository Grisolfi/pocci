# POCCI

A sample of a CI Server using Github Checks API

## Usage

In order to get this app working, you must export the variables below:
`GH_APPLICATION_ID` refers to your GitHub App ID
`GH_PEM_FILE` refers to the path of your GithHub App's .pem file.

1. Install pre-reqs
1. Export variables above
1. Start application `python3 main.py`


You could also use [smee.io](https://smee.io) to redirect GitHub Traffic to your internal network

## References

1. https://docs.github.com/en/developers/apps/creating-ci-tests-with-the-checks-api
1. https://docs.github.com/en/rest/reference/checks
