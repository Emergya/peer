CHANGES
=======

0.17.1 (2015-06-24)
-------------------

- Use the new built-in schema migration framework.

0.17.0 (2015-02-12)
-------------------

- Updated djangosaml2 to 0.13.0

0.16.0 (2015-02-04)
-------------------

- django 1.7 support
- some changes in the front page
- Updated GitPython to 0.3.6, gitdb to 0.6.4, django-vff to 0.2b3

0.14.0 (2014-11-20)
-------------------
- When a subdomain of a verified domain is added by the same user,
  automatically set it as verified.
- Add `publicsuffix <http://pypi.python.org/pypi/publicsuffix>`_ dependency.
- Check that newly added domains are valid.

0.13.0 (2014-02-27)
-------------------
- Upgrade to Django 1.6.2
- Upgrade djangosaml to 0.10.0
- Upgrade django-registration to 1.0
- Upgrade django-recaptcha to 0.0.9
- Adapt form fields to Django 1.6.2
- Adapt urls.py to Django 1.6.2
- Adapt url tag in templates to Django 1.6.2
- Fix license headers (80 char length)
- Add navigation menu to the header, for logged users

0.12.0 (2013-10-29)
-------------------
- Add swig dependence.
- Bugfix in 0007 migration.
- Display validation errors and warnings in a more useful way, with only
  relevant information.
- Fix some encoding errors.
- Support domain validation through email. Add python-whois dependence.
- Add support for domain validation through https.
- Notify the domain owner of validation activity related to that domain.
- Support domain invalidation.
- Bugfix in email notifications.
- Warn about nxdomain response cached in DNS-based validation.
- Validate that DiscoHints elements only appears on IdP SSO nodes.
- Fix parsing the mdUI Info.
- Enforce that KeyDescriptor nodes appear before NameIDFormat ones.
- Avoid crashing in the prettify function with comments.
- Catch the XMLSyntax exception to avoid 500 error when invalid metadata.
- Check for multiple SSO of the same type and warn the user, because that is
  unsupported by SAMLmetaJS.

0.11.0 (2012-04-18)
-------------------
- Add support for schema validation (code stolen from pyff).
- Allow more customizations in the federated login UI.

0.10.2 (2013-02-28)
-------------------
- Upgrade django-recaptcha so it supports SSL
- Minor cleanups of staled files
- Use just the hostname to validate if an endpoint belongs to a domain.
  This allows using non standard ports for the endpoints. Patch by
  Hans Zandbelt

0.10.1 (2012-07-29)
-------------------
- Fix url hiding by reordering some url definitions.
- When importing an entity's metadata inside the EntitiesDescriptor tag, strip
  off such tag.
- Update SAMLmeteaJS to latest version upstream to fix issue #3.
- Several fixes in the documentation:

  - Make the paths more generic and add notes with real paths depending on the
    current version.
  - Add a note about the initial administrator's name.
  - Replace terena.org with example.com in the example configuration.
  - Fix some typos.

- Include txt templates in the distribution.

0.10.0 (2012-03-28)
-------------------
- Nagios integration by implementing a passive nagios agent that
  listen for Entity's updates (creations, updates and deletions)
  and send them to a Nagios server.
- Remove PEER names. If the DisplayName is present it is used as
  the label for the entity. Otherwise, the entity id is used and
  if neither of them exists, the PEER numeric id is used.
- Improve the usability of the SAMLmetaJS editor by showing
  user errors as soon as possible and asking the user either to
  fix them or to remove the information that is giving trouble.
- Implement REMOTE_USER authentication with an easy to switch
  settings option. Also document the web server part of the setup.
- Update djangosaml2 dependency version. This uses newest pysaml2 version.
  As a consequence encrypted assertions and signed response and requests
  work better now. Djangosaml2 0.4.2 also adds logging support.

0.9.0 (2012-03-03)
------------------
- Several changes to the SAMLmetaJS editor:
  - Support for IdP endpoints and certificates.
  - Support for EncryptionMethod in KeyDescriptors
  - Support for MDUI.PrivacyStatementURL and MDUI.InformationURL.
  - Many refactorings to improve code reuse.
  - Merge features from PEER 0.8.0 into SAMLmetaJS master branch.
- Show IdP information (endpoints and certificates) in the details view.
- Improve certificate rendering in the details view.
- Send emails to subscribers of entities when their endpoints are down.
- Allow to subscribe to entities for updates about their endpoints state.
- Refactor the views module of the entities application into a package
  which is easier to handle.
- Several bug fixes:
  - Fix the terms of use file in the metadata upload file form (issue #2).
  - Fix bad use of ugettext_lazy and use ugettext instead.
  - Fix a crash when an entity is new and does not have metadata yet.
  - Fix the way the diff is computed when submitting a change to the
  metadata of an entity.

0.8.0 (2012-01-31)
------------------
- Rich metadata support. Now it is possible to edit the logo and
  geolocalization hint of an entity. This feature is used
  to display richer multimedia information through PEER.
- Improve the metadata editor with request initiator and
  discovery response endpoint support. Also improve the localization
  plugin and add keywords and logo to the information plugin.
- Metadata refresh: if the entity id is a URL that points to the
  metadata itself the user can activate a periodic fetch of this
  metadata.
- Preview before commit: now the editing and commiting flows are
  separated by a modal dialog that ask for the commit message only
  when the changes are ready. In this dialog a diff of the current
  changes is available for easy reviewing.
- Git repositry co-existence: if there is already a Git repository
  with metadata files it can be reused in PEER by specifing the
  directory that PEER 'owns' inside this repository.
- Metadata grouping: a user can define an entity group by writing
  a query. A custom feed and map for this group are created
  automatically so following the changes for related entities
  becomes easier.
- Lots of bug fixes and documentation improvements.

0.7.0 (2011-12-22)
------------------
- DNS-based domain validation
- Delegated domains: an administrator can validate a domain directly and
  create a team that can manage such domains as if they were the owners.
- Administration team: an administrator can add (and remove) other users
  to the administrators team giving them full powers in the system.
- Support for EntityAttributes SAML extension via a SAMLmetaJS new plugin.

0.6.0 (2011-11-30)
------------------
- Attribute based restrictions. This mean, administrators can define
  which metadata attributes can be edited and which ones can't be changed.
- Attribute based notifications a.k.a. advanced filters in the feeds.
- Usability improvements by adding several helpful messages to a lot of
  views.
- Federated authentication.
- Password reset for those of you with volatile memories.
- Several bug fixes.
- Make all public pages HTML5 compliant.
- When validating domains try also the www hostname.
- Big flashy button to get the latest version of an entity's metadata.
- Add the possibility to specify a custom User Agent header for the
  domain ownership proof.
- When editing the metadata of an entity, warn the user that there are
  unsaved changes before he navigates to another page.
- Remove the metadata when removing the entity.

0.5.0 (2011-09-18)
------------------
- Big documentation review and lots of improvements.
- More robust entity validation.
- Fix small layout problems as a result of changing the metadata edition
  UI from accordion to tabs.
- Fix IE lack of indexOf Array method.
- Update jQuery version.
- Show more information of each entity when listing entities.
- Big improvements in the easiness off deployment.
- Clean up the settings.py file from options specific to
  beta.terena-peer.yaco.es.

0.4.0 (2011-08-28)
------------------
- More robust metadata edition
- Change metadata editors layout to use tabs instead of accordion UI.
- Add a most common domains filter and create the foundations of a filters
  infrastructure for future filters
- Update the SAMLmetaJS editor to the latest version upstream
- Warning emails when metadata is about to expire or already expired. Also
  display the expiration time in the UI.
- Add creation and modification timestamps for the entities.
- Entities feed, accesible from the homepage.
- Changes feed of an entity's metadata.
- New metadata validators: they check that the metadata that was entered
  belongs to the domain of the entity.
- Disable the SAMLmetaJS editor for IE since it lacks the right XML parsing
  technology.
- After adding a new entity, redirect the user to the metadata edit view.
- Allow to remove domains.
- Lots of bug fixes and UI tweaks.

0.3.0 (2011-07-27)
------------------
- Display the metadata in a nice format in the entity's details view
- Display the history of metadata changes in the entity's details view
- Organization plugin for the SAMLmetaJS editor
- Several fixes in the SAMLmetaJS editor.
- Entity protection. Only owners and users that are allowed to edit it can
  remove and edit an entity.
- Documentation improvements.
- Terms of Use widget to display legal information when the user is registered
  and when the metadata is updated through an external file or URL.
- User profile view redesign. Now it displays the entities that the user can
  edit even if the entities do not belong to a domain owned by the user.

0.2.0 (2011-07-05)
------------------
- Search entities
- Branding customization support
- SAMLmetaJS integration for metadata edition
- Team permissions for rights delegation
- Usability and design improvements all over the application
- Lots of bug fixes

0.1.0 (2011-06-15)
------------------
- Initial version which includes user registration, domain ownership proof,
  domain creation, entities creation, basic metadata edition
  and user invitation.
