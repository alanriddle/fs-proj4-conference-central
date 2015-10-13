# Udacity Full-Stack Developer Nanodegree - Project 4 - Conference Central

## To Run This Application
1. Update the value of `application` in `app.yaml` to the app ID you
   have registered in the App Engine admin console and would like to use to host
   your instance of this project.
1. Update the values at the top of `settings.py` to
   reflect the respective client IDs you have registered in the
   [Developer Console][1].
1. Update the value of CLIENT_ID in `static/js/app.js` to the Web client ID
1. Run the app with the devserver using `dev_appserver.py DIR`, and ensure it's running by visiting your local server's address (by default [localhost:8080][2].)
1. Deploy your application.


[1]: https://console.developers.google.com/
[2]: https://localhost:8080/

## Task 1 - Design rationale for Session and Speaker
I chose to implement Speaker as a StringProperty in Session rather than a full-fledged entity.

The rationale is expedience, better performance, and lower datastore costs.

Usually when session information is requested, the speaker's name is needed.  Implementing 'speaker' as a string means all session information (including speaker name) can be retrieved in a single datastore call.  If 'speaker' was a separate entity, one datastore call would be needed to get the session information and another datastore call to get the speaker's name.

One datastore call is simpler code (less to go wrong), better performance, and lower datastore costs.  This project requirements can be met using a simple string.  Of course, more complex projects could require using an entity for speaker.

SessionForm contains a field 'websafeSessionKey'. This was included to simplify testing for when I need a reference to the session.

## Task 2 - Add session wishlists 
The following Endpoints were added:
- addSessionToWishlist(User, SessionKey)
- getSessionsInWishlist(User)

Wishlists are implemented as a list of websafe Session keys in the user Profile.

## Task 3 - Work on indexes and queries
The following two additional queries are implemented:
- getConferenceSessionCounts() - List of all conferences and associated count of sessions for each
- getConferenceSpeakers(websafeConferenceKey) - List of distinct speakers for specified conference

### Solve the following query related problem
Statement of Problem: 
- Let's say that you don't like workshops and you don't like sessions after 7 pm. 
- How would you handle a query for all non-workshop sessions before 7 pm?
- What is the problem for implementing this query?
- What ways to solve it did you think of?

I am interpreting this as meaning the session should not go past 7pm. For example, a session staring at 6pm with a duration of 90 minutes should be filtered out.

The problem with this query is that datastore does not allow:
- filtering on 'not equal to'
and
- filtering on computed fields.

#### Use 'OR' to filter for non-workshop sessions
One approach to get around this to use ndb.OR and filter on 'equal to' for all of the session types EXCEPT 'workshop.  Implications are that this approach will work best if the session types are small in number and seldom changed.

For example, in this code there are only three types 'WORKSHOP', 'KEYNOTE', and 'LECTURE'.  To find non-workshop sessions, query on 'KEYNOTE' OR 'LECTURE'.

If there are many session types or session types might be added in the future, application code would need to read the session type class and build up the query filter.

#### Filter for sessions ending by 7pm in application code (or store 'endTime' in Session)
Next, we need to filter out all sessions that end after 7pm. Restated the startTime + duration should be <= 7pm (19:00). As far as I know, datastore does not filter on computed fields so I would filter this in application code.

Assuming the typical use case is to filter on sessions for a single conference in a query, doing the filtering in application code is reasonable (the number of sessions is not too big). 

But if the use case is to query sessions across all conferences, the session entity should modified to include an attribute for 'endTime'. The application code would store the 'endTime' when the session was created by doing a time calculation to add 'duration' to the 'startTime'. Now datastore could do a query across all sessions with 'endTime' less than or equal to 7pm (for all conferences).

## Task 4 - Add a Task
getFeaturedSpeaker() is implemented by adding a task whenever a session was added to a conference.

The task examines sessions within the conference. If there is a total of more than 1 session within that conference with the same speaker as the added session, the task creates a message with the  conference name, speaker name, and the names of the sessions and puts in memcache.
