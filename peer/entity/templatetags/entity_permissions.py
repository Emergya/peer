# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Terena.

from django import template

register = template.Library()

from peer.entity.security import can_edit_entity, can_change_entity_team, can_approve_change


class PermissionNode(template.Node):

    checker_function = None

    def __init__(self, entity, nodelist):
        self.entity = entity
        self.nodelist = nodelist

    def render(self, context):
        user = template.Variable('user').resolve(context)
        entity = template.Variable(self.entity).resolve(context)
        checker_function = self.__class__.checker_function
        if checker_function and checker_function.im_func(user, entity):
            return self.nodelist.render(context)
        else:
            return ''

class ApproveNode(PermissionNode):

    checker_function = can_approve_change

class EditNode(PermissionNode):

    checker_function = can_edit_entity

class ChangeTeamNode(PermissionNode):

    checker_function = can_change_entity_team

@register.tag
def canedit(parser, token):
    try:
        name, entity = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires one argument' %
                                           token.split_contents()[0])
    nodelist = parser.parse(('endcanedit', ))
    parser.delete_first_token()
    return EditNode(entity, nodelist)


@register.tag
def canchangeteam(parser, token):
    try:
        name, entity = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires one argument' %
                                           token.split_contents()[0])
    nodelist = parser.parse(('endcanchangeteam', ))
    parser.delete_first_token()
    return ChangeTeamNode(entity, nodelist)

@register.tag
def canapprove(parser, token):
    try:
        name, entity = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires one argument' %
                                           token.split_contents()[0])
    nodelist = parser.parse(('endcanapprove', ))
    parser.delete_first_token()
    return ApproveNode(entity, nodelist)
