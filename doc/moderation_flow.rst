.. _moderation-flow:

Moderation Flow
===============

Functional Design
-----------------

Overview
^^^^^^^^

The moderation flow implements the use cases where the federation administrators want/are required to have control
over the entities metadata (for policy enforcement, quality assurance, etc.). When moderation is enabled in PEER, all changes
in the metadata entities made in PEER have to be reviewed and approved by a moderator before they are reflected to the actual
metadata XML document that is stored in disk under version control. The assumption is that the XML files are considered the
"published" version of the metadata and are used for metadata aggregation etc.

The functional design is captured in the following use cases and flow diagrams

Use Case 1
^^^^^^^^^^

+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Title                  | Entity owner creates new entity                                                                                     |
+=======================+=====================================================================================================================+
|Primary Actor          | Entity Owner (EO)                                                                                                   |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Pre-conditions         | 1. PEER is functional                                                                                               |
|                       | 2. MODERATION_ENABLED is set to True                                                                                |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Post-conditions        | Entity metadata is stored in the database                                                                           |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Flow                   | 1. EO logs in to PEER.                                                                                              |
|                       | 2. EO selects "add entity" from the drop-down menu.                                                                 |
|                       | 3. EO selects one of the domains he owns and clicks the "create entity" button.                                     |
|                       | 4. EO is presented with the "Edit metadata" form.                                                                   |
|                       | 5. EO enters the entity metadata by copy - pasting them into the text_edit form.                                    |
|                       | 6. EO clicks on "submit changes for moderation" button                                                              |
|                       | 7. EO is presented with a pop-up window with the message that the metadata is valid, the diff between the stored    |
|                       |    and the changed metadata (in this case, the whole metadata document) and an input field to enter a description   |
|                       |    of the changes made                                                                                              |
|                       | 8. EO enters the message describing the changes they made and clicks on "submit changes"                            |
|                       | 9. EO is presented with a message saying "The changes have been submitted for moderation" and the form is reloaded  |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Alternative flows      | 5a. EO selects "By uploading a file and selects the file with the metadata from his local hard disk.                |
|                       |                                                                                                                     |
|                       | 5b. EO selects "By fetching a remote URL" and enters the URL where the metadata is available.                       |
|                       |                                                                                                                     |
|                       | 7a. EO is presented with a pop-up window with the message that the metadata is invalid and informational messages   |
|                       | on what exactly is invalid.                                                                                         |
|                       |                                                                                                                     |
|                       | 8a. EO clicks on "cancel"                                                                                           |
|                       | GOTO 5                                                                                                              |
|                       |                                                                                                                     |
|                       | 8a. EO clicks on "submit changes" without entering a message describing the changes                                 |
|                       |                                                                                                                     |
|                       | 8b. EO is presented with a message saying that this is an obligatory field                                          |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Satisfied requirements | N\/A                                                                                                                |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+

.. image:: images/usecase1.png
    :align: center

Use Case 2
^^^^^^^^^^

+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Title                  | Entity owner changes the metadata of an existing entity                                                             |
+=======================+=====================================================================================================================+
|Primary Actor          | Entity Owner (EO)                                                                                                   |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Pre-conditions         | 1. PEER is functional                                                                                               |
|                       | 2. MODERATION_ENABLED is set to True                                                                                |
|                       | 3. The entity metadata is already stored                                                                            |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Post-conditions        | The modified entity metadata is stored in the database                                                              |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Flow                   | 1. EO logs in to PEER.                                                                                              |
|                       | 2. EO selects "My domains and entities" from the drop-down menu.                                                    |
|                       | 3. EO selects one of the domains he owns and clicks on the entity name.                                             |
|                       | 4. EO is presented with the details of the entity.                                                                  |
|                       | 5. EO clicks on "Edit metadata".                                                                                    |
|                       | 6. EO is presented with the "Edit metadata" form.                                                                   |
|                       | 7. EO makes the necessary changes in the text edit metadata form .                                                  |
|                       | 8. EO clicks on "submit changes for moderation" button                                                              |
|                       | 9. EO is presented with a pop-up window with the message that the metadata is valid, the diff between the stored    |
|                       |    and the changed metadata and an input field to enter a description of the changes made                           |
|                       | 10. EO enters the message describing the changes they made and clicks on "submit changes"                           |
|                       | 11. EO is presented with a message saying "The changes have been submitted for moderation" and the form is reloaded |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Alternative flows      | 7a. EO selects "By uploading a file" and selects the file with the updated metadata from his local hard disk.       |
|                       |                                                                                                                     |
|                       | 7b. EO selects "By fetching a remote URL" and enters the URL where the updated metadata is available.               |
|                       |                                                                                                                     |
|                       | 9a. EO is presented with a pop-up window with the message that the metadata is invalid and informational messages   |
|                       | on what exactly is invalid.                                                                                         |
|                       |                                                                                                                     |
|                       | 10a. EO clicks on "cancel"                                                                                          |
|                       | GOTO 7                                                                                                              |
|                       |                                                                                                                     |
|                       | 10b. EO clicks on "submit changes" without entering a message describing the changes                                |
|                       |                                                                                                                     |
|                       | 11b. EO is presented with a message saying that this is an obligatory field                                         |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Satisfied requirements | N\/A                                                                                                                |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+

.. image:: images/usecase2.png
    :align: center


Use Case 3
^^^^^^^^^^

+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Title                  | Mderator approves/rejects the metadata changes for an existing entity                                               |
+=======================+=====================================================================================================================+
|Primary Actor          | Moderator (M)                                                                                                       |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Pre-conditions         | 1. PEER is functional                                                                                               |
|                       | 2. MODERATION_ENABLED is set to True                                                                                |
|                       | 3. The entity metadata has been changed by the entity owner                                                         |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Post-conditions        | The modified entity metadata is stored in the database                                                              |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Flow                   | 1. M logs in to PEER.                                                                                               |
|                       | 2. M selects "full list of entities" from the drop down menu                                                        |
|                       | 3. M selects one of the domains that is marked with "(pending moderation)" and clicks on the entity name.           |
|                       | 4. M is presented with the details of the entity.                                                                   |
|                       | 5. M clicks on "Approve/Reject metadata changes".                                                                   |
|                       | 6. M is presented with the "Edit metadata" form where he can overview the metadata with the EO changes reflected.   |
|                       | 7. M clicks on "Review changes and publish" button                                                                  |
|                       | 8. M is presented with a pop-up window with the message that the metadata is valid, the diff between the stored     |
|                       |     and the changed metadata and an input field to enter a commit message.                                          |
|                       | 9. M enters the commit message describing the changes and clicks on "submit changes".                               |
|                       | 10. M is presented with a message saying "Metadata has been modified" and the form is reloaded.                     |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Alternative flows      | 6a. M additionally makes some more changes to the metadata or corrects some of the changes made by the EO.          |
|                       |                                                                                                                     |
|                       | 7c. M clicks on "Discard Changes"                                                                                   |
|                       |                                                                                                                     |
|                       | 8a. M is presented with a pop-up window with the message that the metadata is invalid and informational messages    |
|                       | on what exactly is invalid.                                                                                         |
|                       |                                                                                                                     |
|                       | 8c. M is presented with a pop-up window with the message tha the changes will be discarded, the diff of what will   |
|                       | be discarded and an input field to enter a message                                                                  |
|                       |                                                                                                                     |
|                       | 9c. M enters a message and clicks on "Discard changes"                                                              |
|                       |                                                                                                                     |
|                       | 9a. EO clicks on "cancel"                                                                                           |
|                       | GOTO 7                                                                                                              |
|                       |                                                                                                                     |
|                       | 10c. M is presented with a message saying "Metadata modifications have been discarded" and the form is reloaded.    |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+
|Satisfied requirements | N\/A                                                                                                                |
+-----------------------+---------------------------------------------------------------------------------------------------------------------+

.. image:: images/usecase3.png
    :align: center


Technical Design
----------------

Overview
^^^^^^^^

The moderation flow is modelled using a `Finite State Machine <http://en.wikipedia.org/wiki/Finite-state_machine>`_ design pattern
with the help of `django-fsm <https://github.com/kmmbvnr/django-fsm>`_ .
Three states are defined for the entity metadata:
* new
* modified
* published

 An entity metadata is *new* when the Entity Owner has just added it in PEER. *Modified* describes the case where the entity
 metadata has been changed by the owner or a reviewer but has not been approved. *Published* describes the state of the
 entity metadata after they have been approved by a moderator. Only *published* entity metadata are committed to the VCS

 The following state table describes the states and the transitions

+---------------+--------------------------+-----------------+---------------------------------------+
| Current State |      Input               |   Next State    |               Output                  |
+===============+==========================+=================+=======================================+
| New           | moderator approval       | Published       | New version committed to git          |
+---------------+--------------------------+-----------------+---------------------------------------+
| New           | owner modification       | Modified        | New version saved in the DB           |
+---------------+--------------------------+-----------------+---------------------------------------+
| Modified      | moderator approval       | Published       | New version committed to git          |
+---------------+--------------------------+-----------------+---------------------------------------+
| Modified      | moderator rejection      | Published       | Modified version removed from DB      |
+---------------+--------------------------+-----------------+---------------------------------------+
| Modified      | owner modification       | Modified        | New version saved in the DB           |
+---------------+--------------------------+-----------------+---------------------------------------+
| Published     | owner modification       | Modified        | New version saved in the DB           |
+---------------+--------------------------+-----------------+---------------------------------------+
| Published     | moderator modification   | Published       | New version committed to git          |
+---------------+--------------------------+-----------------+---------------------------------------+
| Published     | moderator modification   | Modified        | New version saved in the DB           |
+---------------+--------------------------+-----------------+---------------------------------------+


The states and transitions are also visualized in the following diagram

.. image:: images/peer_fsm.png
    :align: center

Implementation Details
^^^^^^^^^^^^^^^^^^^^^^

Models
``````
The use of django-fsm dictates the definition of an additional field (FSMField) in the Entity model. This is a protected
field that holds the current state of the metadata and can take the values of *new*, *modified* and *published* as
described in the the Functional Design.

A text field (temp_metadata) is also added to the Entity model in order to store the modified metadata until it has been
approved by the moderator.

Finally, a ManyToManyField named moderators is added and contains the explicitly specified moderators for a given entity.

Three new methods are defined for performing the transitions between states for the model instance

.. code-block:: python

    @transition(field=state, source='*', target=STATE.MOD)
    def modify(self, temp_metadata):
        self.temp_metadata = temp_metadata

    @transition(field=state, source='*', target=STATE.PUB)
    def approve(self, name, content, username, commit_msg):
        self.temp_metadata = ''
        self.metadata.save(name, content, username, commit_msg)

    @transition(field=state, source='modified', target=STATE.PUB)
    def reject():
        self.temp_metadata = ''


All three methods are called from the BaseMetadataEditForm save() method.

modify() is called when an entity instance has its metadata modified. The modified metadata is stored in the DB in the
field *temp_metadata*

approve() is called when an entity instance has its metadata modifications approved. The temp_metadata field is cleared
and the metadata is committed to the VCS calling the .metadata.save() method (VFF)

reject() is called when an entity instance has its metadata modifications rejected. The temp_metadata field is cleared

A new field, moderators, is added to the Domain model in order to allow explicitly assignment of moderator status for
all the entities of a given Domain.

Templates
`````````
The simple_edit_metadata.html template is changed in order to present different values to the submit buttons depending
on whether the user is a moderator for the entity or not.

In edit_metadata.html, a hidden field is also added and it's value is sent on submit in order to determine if the POST
request is for submitting changes or approving submitted changes. The javascript is modified in order to allow the pop
up window to show different values depending on the action (submitting changes/approving changes).

A new template tag (cannapprove) is defined and used in order to show UI elements if the currently logged in used is
a moderator. This uses the same logic as the cannedit tag, backed by the can_approve_change method in security.py that
returns True if the user is superuser or explicitly defined as a moderator for the given Entity

Views
`````
The metadata view is changed to contain logic to handle the case when moderation is enabled and act accordingly to what
actions are performed by the user.

Forms
`````
The save() method of the BaseMetadataEditForm is modified as shown below:

.. code-block:: python

    def save(self, action):
        content = write_temp_file(self.metadata)
        name = self.entity.metadata.name
        username = authorname(self.user)
        commit_msg = self.cleaned_data['commit_msg_' + self.type].encode('utf8')
        if settings.MODERATION_ENABLED:
            if action == 'submit_changes':
                self.entity.modify(self.metadata)
            elif action == 'approve_changes':
                self.entity.approve(name, content, username, commit_msg)
            elif action == 'discard_changes':
                self.entity.reject()
        else:
            self.entity.metadata.save(name, content, username, commit_msg)
        self.entity.save()


As shown modify(), approve() or reject() is called depending on the action by the user.

Static Files
````````````
jquery.mesh.js is modified to add dynamically selected messages and title for the popup dialog.