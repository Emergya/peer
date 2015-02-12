.. Terena PEER documentation master file, created by
   sphinx-quickstart on Wed Jun  1 13:09:37 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

================================
Welcome to PEER's documentation!
================================

:Author: `Terena <http://www.terena.org/>`_
:Website: https://github.com/Yaco-Sistemas/peer/
:Release: |release|

PEER is envisioned as a lightweight, global registrar for SAML Metadata
representing both SAML and non-SAML endpoints (e.g., OpenID, IMI). It is
intended as a focused activity to catalyze international use of federated
identity. The service is not intended to be a replacement for federation or
inter-federation, but is intended to be a tool supporting such activities.


Administration Manual
=====================

.. toctree::
   :maxdepth: 2

   install
   configuration
   remote-auth
   upgrade

User Manual
===========

.. toctree::
   :maxdepth: 2

   users
   domains
   entities
   moderation_flow

Appendices
==========

.. toctree::
   :maxdepth: 1

   branding

Support and Development
=======================

The `PEER project web site <https://github.com/Yaco-Sistemas/peer/>`_ is the
main online source of PEER support and development information.

To report bugs, use the
`issue tracker <https://github.com/Yaco-Sistemas/peer/issues>`_.

If you've got questions that aren't answered by this documentation,
contact the `PEER mailing list
<http://lists.iay.org.uk/listinfo.cgi/peer-iay.org.uk>`_.

Browse and check out tagged and trunk versions of PEER via the
`PEER GitHub repository <https://github.com/Yaco-Sistemas/peer/>`_. To check
out the trunk via ``git``, use this command:

.. code-block:: bash

 git clone git@github.com:Yaco-Sistemas/peer.git
