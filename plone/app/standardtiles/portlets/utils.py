# -*- coding: utf-8 -*-
from zope.browser.interfaces import IView
from zope.component import queryMultiAdapter

import logging
logger = logging.getLogger('plone.app.standardtiles')


def findView(tile, viewName):
    """Find the view to use for portlet/viewlet context lookup."""
    view = tile
    prequest = tile.request.get('PARENT_REQUEST', None)

    # Attempt to determine the underlying view name from the parent request
    # XXX: This won't work if using ESI rendering or any other
    # technique that doesn't use plone.subrequest
    if viewName is None and prequest is not None:
        ppublished = prequest.get('PUBLISHED', None)
        if IView.providedBy(ppublished):
            viewName = prequest['PUBLISHED'].__name__

    request = tile.request
    if prequest is not None:
        request = prequest

    if viewName is not None:
        try:
            view = queryMultiAdapter((tile.context, request), name=viewName)
        except TypeError:
            # Helps to debug an issue where broken view registration raised:
            # TypeError: __init__() takes exactly N arguments (3 given)
            logger.exception('Error in resolving view for tile: {0:s}'.format(
                tile.url))
            view = None

    if view is None:
        view = tile

    # Decide whether to mark the view
    # XXX: Again, this probably won't work well if not using plone.subrequest
    layoutPolicy = queryMultiAdapter((tile.context, request), name='plone_layout')  # noqa
    if layoutPolicy is not None:
        layoutPolicy.mark_view(view)

    return view
