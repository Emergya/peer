from functools import update_wrapper

from django.conf.urls import url
from django.contrib.admin.sites import AdminSite

from peer.entity import views
from peer.entity.models import Entity
from peer.entity.feeds import EntitiesFeed, ChangesFeed


class PublicAdminSite(AdminSite):

    def has_permission(self, request):
        return True

    def get_urls(self):

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = [
            # Entity basic views
            #url(r'^$', self.changelist_view, name='entity_entity_changelist'),
            url(r'^$', wrap(self._registry[Entity].changelist_view),
                name='entities_list'),
            url(r'^new/$', views.entity_add, name='entity_add'),
            url(r'^add/$', views.entity_add, name='entity_entity_add'),

            # Group Views
            url(r'^group/add$',
                'peer.entity.views.group.entity_group_add', name='entity_group_add'),
            url(r'^group/(?P<entity_group_id>\d+)$',
                'peer.entity.views.group.entity_group_view', name='entity_group_view'),
            url(r'^group/(?P<entity_group_id>\d+)/edit$',
                'peer.entity.views.group.entity_group_edit', name='entity_group_edit'),
            url(r'^group/(?P<entity_group_id>\d+)/remove$',
                'peer.entity.views.group.entity_group_remove', name='entity_group_remove'),

            # More entity basic views
            url(r'^(?P<entity_id>\d+)/delete/$', views.entity_remove,
                name='entity_remove'),
            url(r'^(?P<entity_id>\d+)/view/$', views.entity_view,
                name='entity_view'),
            url(r'^(?P<entity_id>\d+)/detail/$', views.entity_view,
                name='entity_entity_change'),
            url(r'^(?P<domain_name>\w+)/add$', 'peer.entity.views.entity_add_with_domain',
                name='entity_add_with_domain'),

            # Global views
            url(r'^rss$', EntitiesFeed(), name='entities_feed'),

            # Search view
            url(r'^search$', 'peer.entity.views.search.search_entities', name='search_entities'),

            # Metadata views
            url(r'^(?P<entity_id>\d+)/edit_metadata/$',
                'peer.entity.views.metadata.edit_metadata', name='edit_metadata'),
            url(r'^(?P<entity_id>\d+)/text_edit_metadata/$',
                'peer.entity.views.metadata.text_edit_metadata', name='text_edit_metadata'),
            url(r'^(?P<entity_id>\d+)/file_edit_metadata/$',
                'peer.entity.views.metadata.file_edit_metadata', name='file_edit_metadata'),
            url(r'^(?P<entity_id>\d+)/remote_edit_metadata/$',
                'peer.entity.views.metadata.remote_edit_metadata', name='remote_edit_metadata'),

            # Team views
            url(r'^(?P<entity_id>\d+)/sharing/$',
                'peer.entity.views.teams.sharing', name='sharing'),
            url(r'^(?P<entity_id>\d+)/list_delegates/$',
                'peer.entity.views.teams.list_delegates', name='list_delegates'),
            url(r'^(?P<entity_id>\d+)/make_owner/$',
                'peer.entity.views.teams.make_owner', name='make_owner'),
            url(r'^(?P<entity_id>\d+)/remove_delegate/(?P<user_id>\d+)$',
                'peer.entity.views.teams.remove_delegate', name='remove_delegate'),
            url(r'^(?P<entity_id>\d+)/add_delegate/(?P<username>.+)$',
                'peer.entity.views.teams.add_delegate', name='add_delegate'),


            # Metarefresh views
            url(r'^(?P<entity_id>\d+)/edit_metarefresh/$',
                'peer.entity.views.metadata_utils.metarefresh_edit', name='metarefresh_edit'),

            # Monitor endpoint views
            url(r'^(?P<entity_id>\d+)/monitoring_prefs/$',
                'peer.entity.views.metadata_utils.monitoring_prefs', name='monitoring_prefs'),

            # Metadata revision views
            url(r'^(?P<entity_id>\d+)/get_diff/(?P<r1>\w+)/(?P<r2>\w+)$',
                'peer.entity.views.revisions.get_diff', name='get_diff'),
            url(r'^(?P<entity_id>\d+)/get_revision/(?P<rev>\w+)$',
                'peer.entity.views.revisions.get_revision', name='get_revision'),
            url(r'^(?P<entity_id>\d+)/latest_metadata/$',
                'peer.entity.views.revisions.get_latest_metadata', name='get_latest_metadata'),

            # CSS with highlight colors
            url(r'^pygments.css$', 'peer.entity.views.revisions.get_pygments_css',
                name='get_pygments_css'),

            # Entity feed
            url(r'^(?P<entity_id>\d+)/rss$', ChangesFeed(), name='changes_feed'),
        ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), 'entity', self.name


entities = PublicAdminSite(name='entities')
