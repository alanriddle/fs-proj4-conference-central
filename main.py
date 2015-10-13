#!/usr/bin/env python

"""
main.py -- Udacity conference server-side Python App Engine
    HTTP controller handlers for memcache & task queue access

$Id$

created by wesc on 2014 may 24

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'

import webapp2
from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.api import memcache

from conference import ConferenceApi
from conference import MEMCACHE_FEATURED_SPEAKER_KEY
from models import Session

import logging


class SetAnnouncementHandler(webapp2.RequestHandler):
    def get(self):
        """Set Announcement in Memcache."""
        ConferenceApi._cacheAnnouncement()
        self.response.set_status(204)


class SendConfirmationEmailHandler(webapp2.RequestHandler):
    def post(self):
        """Send email confirming Conference creation."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You created a new Conference!',            # subj
            'Hi, you have created a following '         # body
            'conference:\r\n\r\n%s' % self.request.get(
                'conferenceInfo')
        )

class MakeFeaturedSpeakerMessage(webapp2.RequestHandler):
    def post(self):
        """Make Featured Message for memcache."""
        wsck = self.request.get('websafeConferenceKey')
        wssk = self.request.get('websafeSessionKey')

        speaker = ndb.Key(urlsafe=wssk).get().speaker
        sessions = Session.query(ancestor=ndb.Key(urlsafe=wsck))
        sessions = sessions.fetch()

        sessions_with_same_speaker = [ s for s in sessions
                                       if s.speaker == speaker ]

        session_names = [ s.name for s in sessions_with_same_speaker ]

        if len(session_names) > 1:
            # build message for memcache
            conference_name = ndb.Key(urlsafe=wsck).get().name

            message = ["Featured Speaker",
                       speaker,
                       "Conference: " + conference_name
                      ]

            s_names = []
            for s_name in session_names:
                s_names.append("Session: " + s_name)

            message = message + s_names
            message = "\n".join(message)

            memcache.set(MEMCACHE_FEATURED_SPEAKER_KEY, message)
        else:
            memcache.delete(MEMCACHE_FEATURED_SPEAKER_KEY)



app = webapp2.WSGIApplication([
    ('/crons/set_announcement', SetAnnouncementHandler),
    ('/tasks/send_confirmation_email', SendConfirmationEmailHandler),
    ('/tasks/make_featured_speaker_message', MakeFeaturedSpeakerMessage),
], debug=True)
