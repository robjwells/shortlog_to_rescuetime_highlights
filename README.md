Shortlog to RescueTime highlights
=================================

This is a pretty basic Python script that scrapes "shortlog" files and uploads
each entry to RescueTime as a highlight.

The shortlog files have a simple structure:

```
2018-05-08 20:29:19 | Cleared through emails
2018-05-08 21:05:23 | Read 10 pages of Command and Control
```

It expects the date at the front to be in the (strftime) format
`%Y-%m-%d %H:%M:%S`, followed by a space, a pipe, and another space.
Anything that follows the pipe is taken as the highlight description.

It expects the shortlog files to be named `shortlog-%Y-%m-%d.txt`, so the
example above would be `shortlog-2018-05-08.txt`.

You need to [generate a RescueTime API key][api], and then store the
API key in your system keychain. Install the [keyring][] Python package
and set the API key with the following command:

```
keyring set rescuetime <your-username>
```

You use the script as follows:

```
python3 shortlog_to_rescuetime.py <your-username> <your-shortlog-directory>
```

By default it will upload the shortlog entries from *yesterday’s* log.
Use `--date=<target-date>` if you want to upload the entries from another day.

[api]: https://www.rescuetime.com/anapi/manage
[keyring]: https://www.rescuetime.com/anapi/manage
