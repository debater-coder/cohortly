#set text(
  font: "Rubik",
)
#set heading(numbering: "1.")
#show heading: it => {
  if it.level > 3 {
    block(it.body)
  } else {
    it
  }
}
#show link: underline
#set page(
  header: context [
    Cohortly - Software Engineering Major Project
  ],
  paper: "a3",
)
#align(center, text(17pt)[*Cohortly \
Software Engineering Major Project*])

#align(center)[Hamzah Ahmed]

#outline()
#pagebreak(weak: true)
#set page(numbering: "1", margin: 3cm)
#counter(page).update(1)

#let data_dictionary_table(text) = table(
  columns: (2fr, 2fr, 1fr, 1fr, 2fr),
  align: (auto, auto, auto, center, auto),
  [*Data Structure (type)*], [*Attributes*], [*Data type*], [*Max length*], [*Description*],
  ..csv(bytes(text)).flatten(),
)

#set list(indent: 2em)
= Definition and Analysis of Problem
== Problem Statement and Project Proposal
Student cohorts perform the best when they collaborate. Stronger students in a
subject can assist weaker students by sharing notes and doing peer study
sessions. This also benefits the tutor, as it gives an opportunity for them to
revise the material.

Currently, these sessions are uncoordinated and take place across disparate
messaging applications. Study material, and answers to queries can easily get
lost in these closed messaging channels, leaving out the opportunity for them to
benefit others with the same questions.

A peer tutoring web-app would allow students to coordinate group study sessions,
share notes and study material and have a shared set of questions and answers to
post and view.

== Stakeholders
=== Students

Such a system would be run most effectively when it is maintained primarily by
students. Students will be both the tutors and the pupils in this system, where
tutors benefit by revising the content by explaining it, and pupils benefit by
catching up on the topics they may have missed in class. Additionally, some
admin work is required to effectively run such a system, which should also be
done by students. Student "moderators" volunteer to help keep a specific subject
running smoothly by organising group sessions, and ensuring content is
appropriate, correct and on-topic.

=== Teachers
A core requirement of this project is not to introduce any additional teacher
workload. This system intentionally keeps teacher involvement minimal, as
teacher involvement would not only create extra workload but would also affect
group dynamics in a significant way. Additionally, teacher involvement would
potentially create duty-of-care issues, where teachers may be liable to supervise
student activity. Thus, the system does not involve teachers with any student-to-student
interaction and teachers should only be able to see aggregated statistics on student progress
and have access to a contribution leaderboard.

== Specifications
=== Functional
==== Authentication
+ The system should allow teachers and students to log in using the school portal system
+ The system should allow students to:
  - Post Q&As
  - Schedule or join sessions
  - Share resources
  - Set peer tutoring availability
+ The system should allow moderators to:
  - Remove inappropriate or irrelevant content
  - Review flags for out-of-syllabus or disputed material
  - Add subtopics to subjects
+ The system should allow system administrators to:
  - Add or remove moderators
  - Create and manage subjects
+ The system should allow teachers only to:
  - View statistics on platform use (contribution credits) and student topic mastery ratings
==== Scheduling and Study Sessions
+ Students should be able to view public study sessions/tutoring sessions, and filter by:
  - Subject
  - Host (tutor or subject moderator)
  - Date/time
  - Sessions should show:
  - Subject or topic
  - Session title and description
  - Date and time
  - Meeting link or location
  - Host (student or moderator)
  - Participant list
  - Maximum capacity
+ Students should be able to:
  - Set availability as a peer tutor:
  - Set availability for tutoring sessions
  - Set size (max number of students) of session
  - Accept or decline requests
+ Subject moderators should be able to create general study sessions:
  - General study sessions timing is decided by scheduling polls
+ Students should be able to vote in scheduling polls:
  - Students vote for their available times, and the most popular time slot is chosen
==== Topic Hierarchy
+ The system should represent topics in a hiearchical way:
  - Topics are associated with a subject, and topics can have sub-topics corresponding to increasing detail
+ Students should be able to vote on the difficulty and mastery (how much they understand) of a topic
+ Teachers should be able to view aggregated statistics on difficulty and mastery metrics
==== Moderation
+ Students should be able to flag content as:
  - Inappropriate
  - Out of syllabus
  - Disputed
+ Moderators should be able to see a queue of flagged content, and choose an action (accept flag/delete/reject flag)
+ The system should store all moderator actions in an audit log, so moderator actions are held accountable to the moderator
==== Q&A
+ Students should be able to:
  - Post questions, associated with a topic in the topic hierarchy
  - Respond with answers
  - Flag a question
==== Resource Sharing
+ To share notes, worksheets and study materials, students should be able to:
  - Share links
  - Upload files
+ The system should tag resources with:
  - Subject
  - Topic
  - Uploader
  - Upload date
+ The system must scan uploaded files with VirusTotal API or similar
+ The system must limit to safe file formats (PDF, DOCX, PPTX, etc.)
+ Students should be able to flag resources
==== Points system
+ Students should be able to upvote resources, Q&A, and study sessions to indicate that they were helpful
+ After a study sessions, participants should be able to provide anonymous feedback on a study session, including:
  - A rating out of 5
  - General feedback
+ The system should provide students with *contribution credits* for participating, with higher credit amounts for more helpful activities
+ The system should display a leaderboard for the students with the highest credit amounts

=== Non-Functional
==== Usability
+ The system must be functional on desktop an mobile devices
+ The most commonly used actions must be easy to access intuitively
+ The interface must be consistent
+ There must be a help page to explain more complex processes (such as moderation, the contribution credits system, etc.)
==== Security and Privacy
+ Only students or teachers logged in through the school portal should be able to view any data within the system
+ Uploaded content should be automatically scanned with VirusTotal and restricted to safe formats

= Research and Planning
== Gantt Chart

#text(size: 8pt)[
  #{
    // Base import (change "../src/lib.typ" to "@preview/gantty:0.5.1")
    import "@preview/gantty:0.5.1": gantt

    // Extra imports of specific drawers to allow customization (see the manual!)
    import "@preview/gantty:0.5.1": (
      drawers.default-dependencies-drawer, drawers.default-dividers-drawer, drawers.default-drawer,
      drawers.default-field-drawer, drawers.default-headers-drawer, drawers.default-sidebar-drawer,
      drawers.default-tasks-drawer, header.default-day-header, header.default-month-header, header.default-week-header,
      header.default-year-header, milestones.default-milestones-drawer,
    )

    // Change, for instance, the colour of the milestones to be blue.
    let gantt = gantt.with(
      drawer: (
        milestones: default-milestones-drawer.with(style: (
          stroke: (paint: blue, thickness: 1pt),
        )),
        sidebar: default-sidebar-drawer,
        field: default-field-drawer,
        headers: default-headers-drawer.with(
          headers: (
            default-year-header(),
            default-month-header(gridlines-style: none),
            default-week-header(),
          ),
        ),
        dividers: default-dividers-drawer,
        tasks: default-tasks-drawer,
        dependencies: default-dependencies-drawer,
      ),
    )
    // And render
    gantt(yaml("gantt.yaml"))
  }
]


== Design
=== Data flow Diagram
==== Context Diagram (Level 0)
#image("./images/context-diagram.png")
==== Level 1
#image("./images/l1dfd.png")
==== Level 2
#image("./images/l2dfd.png")

=== Structure Chart
==== Level 1
#image("./images/l1str.png")
==== Level 2
#image("./images/l2str.png")
=== Class diagram
#image("./images/classes.png")
=== Decision Trees
#image("./images/dtree.png")
=== Database Schema
#image("./images/schema.png")
#pagebreak(weak: true)
=== Data Dictionary
#data_dictionary_table(
  "users (array of records),id,integer,8 bytes,Primary key
,sub,string,100 chars,OIDC subject claim from school-portal supplied JWT
,name,string,70 chars,Full name of user (from school portal)
,email,string,254 chars,Email address of user (from school portal)
,created_at,timestamp,8 bytes,When the record was created
,role,integer,8 bytes,Role ID (foreign key to roles table)
,role_display,string,20 chars,Display name for role
,is_admin,boolean,1 byte,Whether the user has admin rights
",
)
#data_dictionary_table(
  "
subjects (array of records),id,integer,8 bytes,Primary key
,name,string,40 chars,
,created_at,timestamp,8 bytes,When the record was created
,topics,array of topic records,EOF,Subtopics of this subject
",
)
#data_dictionary_table(
  "
topic (record),id,integer,8 bytes,Primary key
,name,string,40 chars,
,description,string,EOF,
,created_at,timestamp,8 bytes,When the record was created
,subtopics,array of records,EOF,Subtopics of this topic
",
)
#data_dictionary_table(
  "
difficulty_ratings (array of records),id,integer,8 bytes,Primary key
,topic_id,integer,8 bytes,Foreign Key to topic
,created_at,timestamp,8 bytes,When the record was created
,user_id,integer,8 bytes,User who rated topic (foreign key to users)
",
)
#data_dictionary_table(
  "
contribution_credits (array of records),id,integer,8 bytes,Primary key
,points,integer,4 bytes,Number of points this contribution is worth
,created_at,timestamp,8 bytes,When the record was created
,user_id,integer,8 bytes,Recipient of the contribution credit (foreign key to users)
,reason_id,integer,8 bytes,ID of the credit reason (foreign key to credit_reasons)
,reason_name,string,20 chars,Internal name of credit reason
,reason_display_name,string,20 chars,Display name of credit reason
",
)
#data_dictionary_table(
  "
audit_logs (array of records),id,integer,8 bytes,Primary key
,user_id,integer,8 bytes,Moderator who performed the action (foreign key to users)
,created_at,integer,8 bytes,When the record was created
,operation,string,EOF,JSON description of the operation
",
)
#data_dictionary_table(
  "
sessions (array of records),created_at,integer,8 bytes,When the record was created
,location,string,100 chars,Voice channel or meeting link to join the session
,capacity,integer,4 bytes,Max number of students allowed to join the session
,title,string,30 chars,Title of the session
,description,string,EOF,Description of the session
,needs_join_requests,boolean,1 byte,Whether the session needs a request to join
,open,boolean,1 byte,Whether the session is open to new participants
,host,integer,8 bytes,User who hosts the session (foreign key to users)
,subject_id,integer,8 bytes,The subject the session is associated with (foreign key to subjects)
,topic_id,array of integer,EOF,Topics the session is associated with (foreign key to topics)
,id,integer,8 bytes,Primary key
,session_start,integer,8 bytes,Timestamp the session starts
,session_end,integer,8 bytes,Timestamp the session ends
,upvotes_id,integer,8 bytes,Foreign key to upvotes_collection
,scheduing_poll_id,integer,8 bytes,Foreign key to scheduling_poll
,participants,array of records,EOF,Participants in this session
,feedback,array of records,EOF,Feedback ratings given by session members
",
)
#data_dictionary_table(
  "
participant (record),id,integer,8 bytes,Primary key
,created_at,integer,8 bytes,When the record was created
,status_id,integer,8 bytes,The status of the students' request to join the session (foreign key to session_participant_statuses)
,status_display,string,20 chars,The display name for the status of the students' request to join the session
,user_id,integer,8 bytes,The participant (foreign key to users)
",
)
#data_dictionary_table(
  "
feedback (record),id,integer,8 bytes,Primary key
,created_at,integer,8 bytes,When the record was created
,rating,integer,4 bytes,Rating out of 5 for the session
,feedback,string,EOF,Optional written feedback for the session
,created_by,integer,8 bytes,Who created this feedback record (foreign key to user)
",
)
#block(
  breakable: false,
  [
    *Notes:*
    - Character lengths are provisional lengths for the size of a single line when displayed.
    - In SQLite, the max length of an `INTEGER` is 8 bytes, so that length is used for all IDs
    - 8 byte Unix epoch timestamps are used, as 4 byte epoch timestamps cannot represent timestamps past 19 January 2038
  ],
)

=== Algorithms
==== Main program
```
logged_in = false
User = Null

BEGINMAIN
   WHILE logged_in = false
    User = Login()
   ENDWHILE

   WHILE logged_in
      Get user input
      CASEWHERE user input
        'admin'         : AdminPage()
        'leaderboard'   : LeaderboardPage()
        'sessions'      : SessionsPage()
        'questions'     : QuestionsPage()
        'resources'     : ResourcesPage()
        'topics'        : TopicsPage()
        'log out'       : logged_in = false
      END CASE
   ENDWHILE
ENDMAIN
```
==== Login
```
BEGIN Login()
    CsrfToken = GenerateRandomString()

    RedirectToSbhsPortal()

    AuthCode = GetParamFromUrl('code')
    CsrfState = GetParamFromUrl('state')

    IF AuthCode <> CsrfState THEN
        logged_in = false
        RETURN Null
    ENDIF

    Response = ExchangeAuthCodeForTokens()

    AccessToken = GetFromResponse(Response, 'access_token')
    RefreshToken = GetFromResponse(Response, 'refresh_token')
    IdToken = GetFromResponse(Response, 'id_token')

    IF AccessToken = Null THEN
        logged_in = false
        RETURN Null
    ENDIF

    IF IdToken <> Null THEN
        TokenValid = VerifyToken(IdToken)       'Note that this uses digital signature algorithms (DSA) to verify the token rather than a database search
        IF TokenValid THEN
            Claims = GetUserClaims(IdToken)
            logged_in = true
            RETURN CreateUserRecord(Claims.id, Claims.name, Claims.email)
        ENDIF
    ENDIF

    RETURN Null
END Login
```
#pagebreak(weak: true)
==== Leaderboard
```
BEGIN LeaderboardPage()
    CohortYear = Get user input

    LeaderboardRecords = []

    Open StudentDatabase
    Open CreditsDatabase

    FOR i = 0 to StudentDatabase.Length
        StudentRecord = StudentDatabase[i]

        'This is implemented using an SQL WHERE clause
        CreditRecords = FilterByUserId(CreditsDatabase, StudentRecord.UserId)

        Points = 0
        For j = 0 to CreditRecords.Length
            Points = Points + CreditRecords[j].Points
        NEXT j

        LeaderboardRecord = Empty leaderboard record
        LeaderboardRecord.Student = StudentRecord
        LeaderboardRecord.Points = Points
    NEXT i

    MergeSortDescendingByPoints(LeaderboardRecord)

    Close CreditsDatabase
    Close StudentDatabase

    FOR i = 0 to 29
        IF i < LeaderboardRecords.Length THEN
            Record = LeaderboardRecords[i]
            Display 'Place', i + 1
            Display 'Name', Record.Student.Name
            Display 'Points', Points
        ENDIF
    NEXT i
END LeaderboardPage

BEGIN MergeSortDescendingByPoints(Records)
    IF Records.length <= 1 THEN
        RETURN Records
    ENDIF

    Middle = Records.length / 2

    Left = MergeSortDescendingByPoints(Records from index 0 to Middle)
    Right = MergeSortDescendingByPoints(Records from index Middle + 1 to Records.length - 1)

    RETURN MergeByPointsDescending(Left, Right)
END MergeSortByPoints

BEGIN MergeByPointsDescending(Left, Right)
    MergedArray = []
    WHILE Left is not empty AND RIGHT is not empty
        IF Left.Length > 0 AND Right.Length > 0 THEN
            IF Left[0].Points > Right[0].Points THEN
                Append Left[0] to MergedArray
                Remove Left[0]
            ELSE
                Append Right[0] to MergedArray
                Remove Right[0]
            ENDIF
        ELSE IF Left.Length > 0 THEN
                Append Left[0] to MergedArray
                Remove Left[0]
        ELSE IF Right.Length > 0 THEN
                Append Right[0] to MergedArray
                Remove Right[0]
        ENDIF
    ENDWHILE

    RETURN MergedArray
END MergeByPointsDescending

```
#pagebreak(weak: true)
==== Questions Page
```
BEGIN QuestionsPage()
    Get user input
    CASEWHERE user input
        'search_questions'  :  QuestionsSearch()
        'new_question'      :  NewQuestion()
        'edit_question'     :  EditQuestion()
        'delete_question'   :  DeleteQuestion()
        'upvote_question'   :  UpvoteQuestion()
        'new_answer'        :  NewAnswer()
        'edit_answer'       :  EditAnswer()
        'delete_answer'     :  DeleteAnswer()
        'upvote_answer'     :  UpvoteAnswer()
    END CASE
END QuestionsPage

```
==== Session Page
```
BEGIN SessionsPage()
    Get user input

    CASEWHERE user input
        'search'             : SessionsSearch()
        'group_polls'        : SessionsPoll()
        'peer_tutoring'      : SessionsPeerTutoring()
        'feedback'           : SessionsFeedback()
    END CASE
END SessionsPage

BEGIN SessionsSearch()
    Get user input
    Open SessionsDatabase

    Index = 0
    WHILE Index < SessionsDatabase.Length
        IF Contains(SessionsDatabase[Index].name, user input) OR
           Contains(SessionsDatabase[Index].description, user input) THEN  'Note that the implementation will use a fuzzy search algorithm for more relevant search results
            Display 'Name', SessionsDatabase[Index].name
            Display 'Description', SessionsDatabase[Index].description
            Display 'Subject', SessionsDatabase[Index].subject
            Display 'Date', SessionsDatabase[Index].date
            Display 'Time', SessionsDatabase[Index].time
            Display 'Location', SessionsDatabase[Index].location
            Display 'Host', SessionsDatabase[Index].host
        ENDIF
        Index = Index + 1
    ENDWHILE

    Close SessionsDatabase
END SessionsSearch
```
=== Storyboard
#image("images/storyboard.png")
Zoom for detail.
=== Interface Design
==== Consistency
Consistency was a highly valued design element in Cohortly. All interactible buttons
are rounded box in one of two colours: blue for primary actions and grey for secondary actions.
Buttons also work similarly in other software, so Cohortly is not only internally consistent
but also externally consistent with other software the user is likely to have been used, allowing
them to learn it more efficiently.
#image("images/screenshots/buttons.png")

==== Navigation
Consistent navigation on every logged-in page allows for users to learn the navigation system once,
and quickly use it to move between pages without having to relearn navigation for different areas of
the interface.

For example, the "breadcrumb" pattern was used (a list of links forming a hierarchy), where a user
can click on any of the links in the breadcrumbs to quickly return to a specific page in the hierarchy.
#image("images/screenshots/breadcrumbs.png")

Above the breadcrumbs is a consistent navigation bar, including a link to the
help center, account details and a universal search bar. The search bar provides
another way to navigate. Because the search bar is universal (across all content
hosted by Cohortly), it can be used to quickly find a particular piece of content
(a question, answer, topic, subject, resource or session) without needing to manually
navigate the the particular list containing that page. Because Cohortly is designed
to host such a large amount of content, it is necessary to have this feature to make
this navigable.

#image("images/screenshots/search-page.png")

==== Forgiveness
In interface design, forgiveness refers to design decisions that are designed to make
the system resistant to human error. For example, confirmation is sought before performing
potentially destructive actions, such as leaving a subject or deleting some content.
#image("images/screenshots/forgiveness.png")

==== Efficiency of use
In Cohortly, efficiency of use is important in allowing moderators to perform their tasks
more efficiently. Subject syllabuses have many dozens of subtopics, so it is important that
the interface is quick to navigate and use. An example of this is the selection of subtopics
throughout the interface, where a dropdown with a filtered search is used to allow for quicker
selection of a subtopic where there may be dozens.

#image("images/screenshots/topic-select.png")
Additionally, this topic select supports using the Up and Down arrow keys to select a particular
topic more quickly, and supports using the Backspace key to remove a topic selection. Alongside
standard Tab key navigation in forms, this allows power users to much more efficiently navigate the
user interface.


= Producing and Implementing
== Logbook

=== 16 November 2025
At this stage I have some of my early specifications, so I can start considering what technologies to use for implementation:

Since my project is collaborative, functionality has a heavy dependency on the shared database. Most of the content in the web app is located on the server, so there is not much point having a JS-first application “shell” syncing server side state, since the shell can’t do much on its own. Thus a server-first implementation, with content rendered to HTML on the server makes the most sense. Additionally, offline functionality can still be available through read-only service worker caching of rendered pages.

Technology stack:
Rust-based server side libraries:
Axum for server
Maude for templating (html generated by rust macros)
This allows for a JSX-like component system except its entirely server-side
Lightweight client side libraries:
Alpine.js for simple client side interactivity
Possibly solid or svelte for any highly interactive component islands (but loaded only in those places)
HTMX for no-reload form and link UX
Pico css for semantic html styling

Authentication:
Server-side OAuth: students login with student portal, their ID token, access token, refresh token are all stored in HTTP-only cookie
=== 7 January 2026
Completed authentication middleware:
Can now log in with the SBHS portal, interfacing with OAuth and OIDC
The middleware extracts name, user ID and email address from the ID Token (JWT)
=== 21 April 2026
Completed database integration.
I chose SQLite for the database for its ease of deployment. SQLite is a bit more bare in functionality compared to some heavier databases and suffers from relaxed typing, but using it means that the system can be deployed as a single container with a persistent volume attached. If this ends up being student-run that is very useful.
Can now create courses in the database which students can join
I chose breadcrumb navigation to have a consistent way for users to navigate the hierarchical interface.

=== 12 July 2026
Finished implementation of subjects and topics in the peer tutoring system.

=== 18 July 2026
Began rewrite of major project to Python with Django. The axum-based stack
proved unproductive since the project required many repetitive forms. This
proved far more efficient in Django, compared to axum where the form HTML must
be written manually.

Most of the HTML and styles could be carried over without too much change,
so much of the work went into backend improvement. Despite a slight initial learning
curve, after very few hours this approach proved very productive.

=== 19 July 2026
Completed implementation of all existing features in the new Django-based
system. Including:
- Authentication
- Subjects
- Initial topics system

=== 21 August 2026
Finished topic system, allowing moderators to create, edit and reorder
topics. Topic descriptions are markdown text, allowing for features such
as headings, code and images to be included in the description. This markdown
system was planned to be reused in other areas of the web application, allowing
for rich text in questions and answers.

=== 23 August 2026
Completed question and answer system, including upvoting questions and answers,
and marking an answer as a solution. Also created a search feature,
re-implemented profile and settings menus, and much of the initial study
sessions scaffolding.

=== 24 August 2026
Implemented interactive calendars using the `fullcalendar.js` library, supporting
efficient visualisation of study sessions. A similar calendar was also included grade-wide
to allow the prevention of scheduling conflicts between different subjects.

=== 30 August 2026
Implemented resources, peer-tutoring sessions, virus scanning (and email reminders) and email alerts for uploaded
viruses. Installed onto live system at https://cohortly.up.railway.app/

== User documentation
This is the user documentation included in the product.

=== Getting Started

Cohortly is a web application designed to foster student collaboration by allowing students to share their
knowledge in Q&As and study sessions.

To use Cohortly, you log in with your School Portal account. Your account is linked to your email address,
student ID and full name. Access is limited to Sydney Boys High School students only. Once logged in, you will
be redirected to the Dashboard

=== Joining a subject

From the dashboard, you can join a subject by clicking the "Join or leave subjects" button. From there you can
manage your subject memberships. Joining a subject is required before you can use the study sessions or Q&A
features. From there, you can click on a subject to view its detail page.

=== Asking and answering questions

From the subject page, you can click on the "Questions" link in the sidebar to access the questions list. From
there, you can ask a question, or view existing questions. Within a question, you can upvote the question if you
find it helpful, post an answer, and upvote answers. Upvoted questions and answers appear earlier in their lists,
allowing people to find them more easily. If you posted a questions, you can mark the answer that best answers it
as the solution to your question, where it will appear at the top of the answers list to help people find it more easily.
Since questions serve as a resource for other students,
they should be clear and well-written, asking a specific syllabus-relevant question.

=== Uploading and using resources
You can upload resources (past papers, study notes, textbooks) as either
a PDF document, or as a link to Google Docs or some other website. Uploaded
documents must be in PDF format and be under 10 MB in size. Documents will
be scanned for viruses before being visible to other students.
=== Joining study sessions
Group study sessions are created by moderators and are designed to be larger general review sessions to assist
many students in reviewing and catching up similar content. Peer tutoring sessions can be created by anyone,
and allow a small group or one-on-one study sessions to catch particular students up on content they may have missed or be weaker at.
On your dashboard, you can see the study sessions for all subjects across the Cohortly instance for your grade. Clicking
on any entry will send you to the session detail page for that session, showing description, time, location, participants
and other relevant information. If you are a member of that subject, you can join the session by clicking on "Join session" on
the session detail page. Sessions filtered to a subject can be accessed by clicking on "Sessions" in the sidebar on any subject page.
+== Participating in peer tutoring
You can create a peer tutoring session by clicking "Create a peer
tutoring session" on the subject's session page. This creates a new empty
peer tutoring session, which will appear to other students as long as there
are spots available. You can select a capacity up to 8 (but smaller groups
of 2-3 are recommended) for that session, after which it will be
automatically closed to new participants. You can manually set the open or closed status of
the session by clicking on the "Edit session" button and ticking or unticking the "open" checkbox. When students join
your session, you can choose whether to accept or decline their join request.
=== Frequently Asked Questions
==== Why can't I join a session?
Sessions are capacity limited to a number of students decided by the host.
This prevents groups from becoming too large and making it harder to support students.
Session participation is assigned on a first-come-first-serve basis. When a session is
at capacity, the join button will be grayed out.
==== Why can't I see my subject on the dashboard?

Your dashboard will only show a subject you are a member of. If you have not yet joined a subject it will not be
visible on that page. If your subject is not visible on the subjects list page, then you will need to contact the administrator to add the subject.

==== How are new subject requests processed?

Before a new subject is created, a moderator who will manage group study sessions and Q&A content needs to be appointed.
More than one moderator can be appointed for large subjects to split the workload. Moderator choice is subject to the
administrator's discretion, and moderator privileges can be revoked if abused. A moderator can only moderate content
for their appointed subject.

==== How does moderation work?
Moderators chosen for each subject by an administrator can create and modify group study sessions. They can also modify or delete
questions and answers if they contain inappropriate content.



= Testing and Evaluating
== Test Report
=== Authentication
This is handled by the student portal.

#table(
  columns: (1fr, 1fr, 1fr, 1fr),
  [*Input (username)*], [*Input (password)*], [*Expected output*], [*Reason*],
  [4440000000], [Correct corresponding password], [ The main dashboard is shown ], [Testing successful authentication],
  [bob], [banana], [ Error message: "Invalid username or password" ], [Testing non-existent accounts],
  [4440000000], [banana], [ Error message: "Invalid username or password" ], [Testing incorrect password],
)

=== Sessions
_Create session_
#table(
  columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
  [*Input (session type)*],
  [*Input (start date and time)*],
  [*Input (end date and time)*],
  [*Input (Capacity)*],
  [*Expected output*],
  [*Reason*],

  [Peer tutoring],
  [30/08/2026 5:00pm],
  [30/08/2026 5:30pm],
  [2],
  [ Error message: "Date must not be in the past" ],
  [Testing cannot make past sessions],

  [Peer tutoring],
  [31/08/2026 5:00pm],
  [31/08/2026 5:00pm],
  [2],
  [ Error message: "End time must be after start time" ],
  [Testing cannot make zero-time session],

  [Peer tutoring],
  [31/08/2026 5:00pm],
  [31/08/2026 4:00pm],
  [2],
  [ Error message: "End time must be after start time" ],
  [Testing cannot make end before start],

  [Peer tutoring],
  [31/08/2026 5:00pm],
  [31/08/2026 5:40pm],
  [8],
  [ Peer tutoring session is shown ],
  [Testing can make peer tutoring up to 8 people],

  [Peer tutoring],
  [31/08/2026 5:00pm],
  [31/08/2026 5:40pm],
  [0],
  [ Error message: "Capacity must be greater than 0" ],
  [Testing capacity is a positive integer],

  [Peer tutoring],
  [31/08/2026 5:00pm],
  [31/08/2026 5:40pm],
  [-1],
  [ Error message: "Capacity must be greater than 0" ],
  [Testing capacity is a positive integer],

  [Peer tutoring],
  [31/08/2026 5:00pm],
  [31/08/2026 5:40pm],
  [9],
  [ Error message: "Capacity must be at most 8" ],
  [Testing peer tutoring capacity limit],

  [Group study session],
  [31/08/2026 5:00pm],
  [31/08/2026 5:40pm],
  [250],
  [ Group study session shown ],
  [Testing group study capacity limit],

  [Group study session],
  [31/08/2026 5:00pm],
  [31/08/2026 5:90pm],
  [250],
  [ Error message: "Invalid time" ],
  [Testing invalid time],

  [Group study session],
  [32/08/2026 5:00pm],
  [32/08/2026 5:30pm],
  [250],
  [ Error message: "Invalid date" ],
  [Testing invalid date],

  [Group study session],
  [31/08/2026 5:00pm],
  [31/08/2026 5:40pm],
  [251],
  [ Error message: "Capacity must be at most 250" ],
  [Testing group study capacity limit],
)

=== Resources

_Create resource_
#table(
  columns: (1fr, 1fr, 1fr, 1fr, 1fr),
  [*Input (Resource title)*], [*Input (Description)*], [*Input (File upload)*], [*Expected output*], [*Reason*],

  [], [Resource description], [-], [Error message: "Title cannot be blank"], [Testing blank title],
  [Study resource], [ #lorem(15) ], [-], [Resource page is shown], [Testing creation of resource with no file],
  [Study resource], [], [image.png], [Error message: File must be a valid PDF], [Testing upload of non-PDF],
  [Study resource], [], [image.pdf], [Error mesage: File must be a valid PDF], [Testing upload of corrupted PDF],
  [Study resource],
  [],
  [virus.pdf],
  [Resource page with error message is shown: "This file has been flagged as a virus"],
  [Testing virus scanning],

  [Study resource], [], [-], [Error message: "Include either a file upload or description"], [Testing blank resource],
)

=== Questions page

_Create question_
#table(
  columns: (1fr, 1fr, 1fr, 1fr),
  [*Input (Question title)*], [*Input (Question body)*], [*Expected output*], [*Reason*],

  [Test], [#lorem(15)], [Error message: "Title must be greater than or equal to 15 characters"], [Testing short title],

  [15CharactersLen], [#lorem(15)], [Question page is shown], [Testing exactly 15 characters long title],

  [How do I write good test data?],
  [],
  [Error message: "Description must be greater than or equal to 30 characters"],
  [Testing blank description],

  [How do I write good test data?],
  [#lorem(15) `<IMG SRC=# onmouseover="alert('xxs')">`],
  [Question page is shown with no image.],
  [Testing sanitation of input data to thwart XSS attacks],

  [How do I write good test data?],
  [#lorem(15) `User drag and drops image`],
  [Question page is shown with image.],
  [Testing drag and drop of image],

  [How do I write good test data?],
  [#lorem(15) `User drag and drops PDF`],
  [Question page is shown with no file.],
  [Testing only images allowed on question page],

  [How do I write good test data?],
  [#lorem(15) `$ E = mc^2 $`],
  [Question page is shown with equation: $ E = m c^2 $.],
  [Testing formatting of mathematical equations],

  [How do I write good test data?],
  [`this is **bolded text** and _italics_`],
  [Question page is shown with proper formatting ],
  [Testing formatting of text in question (this is *bolded text* and _italics_)],
)


=== Reccomendations
This system passes preliminary testing of the main cases, as well as some user inputs
designed to test input santisiation and resistance to XSS attacks. However, this testing
methodology lacks more sophisticated testing such as load testing, automated fuzzing (DAST),
and testing for race conditions. These tests should be perfomred before installation of the
system.

== Evaluation

+ The system should allow teachers and students to log in using the school portal system #emoji.checkmark.heavy (Partial)

*Students can log in but teacher support was dropped due to time limitations*

The system should allow students to:
- Post Q&As #emoji.checkmark.box
- Schedule or join sessions #emoji.checkmark.box
- Share resources #emoji.checkmark.box
- Set peer tutoring availability #emoji.checkmark.box

*All of these features are fully implemented*

The system should allow moderators to:
- Remove inappropriate or irrelevant content #emoji.checkmark.box
- Review flags for out-of-syllabus or disputed material #sym.ballot.cross
- Add subtopics to subjects #emoji.checkmark.box

*Essential moderation features such as removing and editing content as well as creating and modifying subtopics
was implemented, but more advanced moderation features were omitted due to time limitations.*

The system should allow system administrators to:
- Add or remove moderators #emoji.checkmark.box
- Create and manage subjects #emoji.checkmark.box

*This was fully implemented (admin dashboard).*

The system should allow teachers only to:
- View statistics on platform use (contribution credits) and student topic mastery ratings #sym.ballot.cross

*Teacher access was not implemented.*

==== Scheduling and Study Sessions
Students should be able to view public study sessions/tutoring sessions, and filter by: #emoji.checkmark.heavy (Partial)
- Subject
- Host (tutor or subject moderator)
- Date/time
- Sessions should show:
- Subject or topic
- Session title and description
- Date and time
- Meeting link or location
- Host (student or moderator)
- Participant list
- Maximum capacity

*All of these features are implemented and are able to be viewed and searched by, but advanced filtering
by these properties was not implemented.*

Students should be able to:
- Set availability as a peer tutor: #emoji.checkmark.box
- Set availability for tutoring sessions #emoji.checkmark.box
- Set size (max number of students) of session #emoji.checkmark.box
- Accept or decline requests #emoji.checkmark.box

*This was fully implemented.*

Subject moderators should be able to create general study sessions: #emoji.checkmark.box
- General study sessions timing is decided by scheduling polls #sym.ballot.cross
Students should be able to vote in scheduling polls: #sym.ballot.cross
- Students vote for their available times, and the most popular time slot is chosen #sym.ballot.cross

*While general study sessions were implemented, the polling feature was omitted due to time limitations.*
==== Topic Hierarchy
The system should represent topics in a hiearchical way:#emoji.checkmark.box
- Topics are associated with a subject, and topics can have sub-topics corresponding to increasing detail
Students should be able to vote on the difficulty and mastery (how much they understand) of a topic#sym.ballot.cross
Teachers should be able to view aggregated statistics on difficulty and mastery metrics#sym.ballot.cross

*While the topic hierarchy can be created and modified by moderators, difficulty rating was not implemented.*

==== Moderation
Students should be able to flag content as:#sym.ballot.cross
- Inappropriate
- Out of syllabus
- Disputed
Moderators should be able to see a queue of flagged content, and choose an action (accept flag/delete/reject flag)#sym.ballot.cross
The system should store all moderator actions in an audit log, so moderator actions are held accountable to the moderator#sym.ballot.cross

*Moderators can manually edit or remove harmful content but these advanced moderation features were not implmented.
At the scale of a student cohort where students' names are associated with their actions, the moderation problem
is far more tractable so these were not as important.*

==== Q&A
Students should be able to:#emoji.checkmark.box
- Post questions, associated with a topic in the topic hierarchy
- Respond with answers
- Flag a question

*These were fully implemented*
==== Resource Sharing
+ To share notes, worksheets and study materials, students should be able to:#emoji.checkmark.box
  - Share links
  - Upload files
+ The system should tag resources with:#emoji.checkmark.box
  - Subject
  - Topic
  - Uploader
  - Upload date
+ The system must scan uploaded files with VirusTotal API or similar#emoji.checkmark.box
+ The system must limit to safe file formats (PDF, DOCX, PPTX, etc.)#emoji.checkmark.heavy (Partial)
+ Students should be able to flag resources#emoji.checkmark.box

*This was fully implemented except resources can only either be PDF or link to external content (eg Google Docs), for ease
of validation.*

==== Points system
+ Students should be able to upvote resources, Q&A, and study sessions to indicate that they were helpful#sym.ballot.cross
+ After a study sessions, participants should be able to provide anonymous feedback on a study session, including:#sym.ballot.cross
  - A rating out of 5
  - General feedback
+ The system should provide students with *contribution credits* for participating, with higher credit amounts for more helpful activities#sym.ballot.cross
+ The system should display a leaderboard for the students with the highest credit amounts#sym.ballot.cross

*None of this was implemented due to time limitations*

=== Non-Functional
==== Usability
+ The system must be functional on desktop an mobile devices#emoji.checkmark.heavy (Partial)
+ The most commonly used actions must be easy to access intuitively#emoji.checkmark.box
+ The interface must be consistent#emoji.checkmark.box
+ There must be a help page to explain more complex processes (such as moderation, the contribution credits system, etc.)#emoji.checkmark.box

*The system is designed primarily for desktop, and while it is usable on mobile it is not specifically optimised for it.*


==== Security and Privacy
+ Only students or teachers logged in through the school portal should be able to view any data within the system#emoji.checkmark.box
+ Uploaded content should be automatically scanned with VirusTotal and restricted to safe formats#emoji.checkmark.box


#import "@preview/numbly:0.1.0": numbly
#counter(heading).update(0)
#set heading(
  numbering: numbly(
    "Appendix {1:A}.", // use {level:format} to specify the format
    "{1:A}.{2}.",
  ),
  supplement: [],
)
