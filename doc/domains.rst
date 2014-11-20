
Domain management
=================

Basically, a domain in this system consists of the string representation of
a DNS domain, and a reference to a user, the owner of the domain. It also
has a *verified* mark, the semantics of which will be explained below. Any
user can have any number of domains.

In the user profile view, accessible by clicking on the button labelled with
the username in the upper right corner, there is a link labelled
**add domain**. Following it, the user is presented with a form to add a
new domain. In this form the user simply has to fill in the name of the
domain, and click on the *add domain* button.

Adding a domain is not enough to use it in the system. Once a domain is added,
PEER has to verify that the user has actual management rights over that domain
in the DNS environment. If the user has already registered and verified a
superdomain of the new domain, the new domain will automatically be marked as
verified. Otherwise, after adding a domain, the user is redirected to the
verification page of the domain, which is also the main page of a domain.

It is not compulsory to verify the domain immediately after adding it: the
user can, at any later time, click on a button labelled *Verify
Ownership*, which takes her to the verification page. In this page there
are several options to validate the domain.


HTTP Validation
---------------
With this option the user needs to create a resource in the root of the
HTTP service for that domain with a specific string given in the verification
page. Once she creates it, she has to click the **Verify ownership by HTTP**
button. The system then sends an HTTP GET request to ``http://<the new
domain>/<the verification string>``, and only when it gets a 200 OK response
code, it considers the domain (and marks it as) verified.


DNS Validation
--------------
For the DNS verification the user has to create a DNS TXT record in the
domain with that string. Once created, when clicking in the
**Verify ownership by DNS**, button the system checks that such record
exists and only if it exits is the domain marked as verified.

You can also verify a subdomain by adding the TXT record to the subdomain
itself or to the second-level domain.

.. note::

    The DNS record changes may take some time to propagate.


Manual validation
-----------------
This option is only available for administrators. In this case the
administrator user just need to click on the **Verify ownership by force**
button to mark the domain as validated. The system trusts these kind of
users and will do as they say without problems.

When an administrator validates a domain using this option she will be
redirected to another page where she will be able to add users to this
domain's team. Being on a domain's team means having the same privileges
as the owner of the team. This way an administrator can create several
domains and assign teams to manage them.

Other domain actions
--------------------

The domains belonging to the user are listed in her profile as
*verified* or *unverified*. In the case of unverified domains she can click
on the **Verify Ownership** button which takes her to the
*verification page*. She can also delete any domain from this page.

In the case of verified domains the **Verify Ownership** button will
dissapear and, in the case of an administrator user, it will be replaced
by a **Manage domain team** button that will takes her to the page
where she can add and remove users to such team.

Every entity in PEER is associated with a domain object. This is used in
some validators that check that some parts of the entity's metadata (such as
endpoints) belongs to its entity's domain.
