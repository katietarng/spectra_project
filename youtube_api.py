import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


CLIENT_SECRETS_FILE = "client_secrets.json"

YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Authorize the request and store authorization credentials
def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_READ_WRITE_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
      credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

"""
Call the API's videos.list method to retrieve an existing video localization.
If the localized text is not available in the requested language,
this method will return text in the default language.
The localized object contains localized text if the hl parameter specified
a language for which localized text is available. Otherwise, the localized
object will contain metadata in the default language.
"""


def get_video_localization(youtube, video_id, language):
    results = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        maxResults=10,
        regionCode="",  # Need to convert lat/long coord and pass ISO country code
        hl=language
        ).execute()

    localized = results["items"][0]["snippet"]["localized"]

    print ("Video title is '%s' and description is '%s' in language '%s'"
           % (localized["title"], localized["description"], language))


if __name__ == "__main__":
  # The "action" option specifies the action to be processed.
  argparser.add_argument("--action", help="Action")
  # The "video_id" option specifies the ID of the selected YouTube video.
  argparser.add_argument("--video_id",
    help="ID for video for which the localization will be applied.")
  # The "default_language" option specifies the language of the video's default metadata.
  argparser.add_argument("--default_language", help="Default language of the video to update.",
    default="en")
  # The "language" option specifies the language of the localization that is being processed.
  argparser.add_argument("--language", help="Language of the localization.", default="de")
  # The "title" option specifies the localized title of the video to be set.
  argparser.add_argument("--title", help="Localized title of the video to be set.",
    default="Localized Title")
  # The "description" option specifies the localized description of the video to be set.
  argparser.add_argument("--description", help="Localized description of the video to be set.",
    default="Localized Description")

  args = argparser.parse_args()

  if not args.video_id:
    exit("Please specify video id using the --video_id= parameter.")

  youtube = get_authenticated_service(args)
  try:
    if args.action == 'set':
      set_video_localization(youtube, args.video_id, args.default_language, args.language, args.title, args.description)
    elif args.action == 'get':
      get_video_localization(youtube, args.video_id, args.language)
    elif args.action == 'list':
      list_video_localizations(youtube, args.video_id)
    else:
      exit("Please specify a valid action using the --action= parameter.")
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  else:
    print "Set and retrieved localized metadata for a video."