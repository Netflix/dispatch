---
description: >-
  We take the security of Dispatch seriously. The following are a set of
  policies we have adopted to ensure that security issues are addressed in a
  timely fashion.
---

# Security

## Reporting a security issue

We ask that you do not report a security issue to our standard GitHub issue tracker.

If you believe you've identified a security issue with `Dispatch`, please report it via our public Netflix bug bounty program at [https://bugcrowd.com/netflix](https://bugcrowd.com/netflix)

Once you've submitted the issue, it will be handled by our triage team, typically within 48 hours.

## Support Versions

At any given time, we will provide security support for the `master` branch and the two most recent releases.

## Disclosure Process

Our process for taking a security issue from private discussion to public disclosure involves multiple steps.

Approximately one week before full public disclosure, we will send advance notification of the issue to a list of people and organizations, primarily composed of known users of `Dispatch`. This notification will consist of an email message containing:

- A full description of the issue and the affected versions of `Dispatch`.
- The steps we will be taking to remedy the issue.
- The patches, if any, will be applied to `Dispatch`.
- The date on which the `dispatch` team will apply these patches, issue new releases, and publicly disclose the issue.

Simultaneously, the reporter of the issue will receive notification of the date we plan to make the issue public.

On the day of disclosure, we will take the following steps:

- Apply the relevant patches to the `Dispatch` repository. The commit messages for these patches will indicate that they are for security issues but will not describe the issue in any detail; instead, they will warn of upcoming disclosure.
- Issue the relevant releases.

If a reported issue is particularly time-sensitive – due to a known exploit in the wild, for example – the time between advance notification and public disclosure may be shortened considerably.

The list of people and organizations who receives the advanced notification of security issues is not, and will not, be made public. This list generally consists of high-profile downstream users and is entirely at the discretion of the `Dispatch` team.
